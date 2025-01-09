from typing import List, Optional, Tuple
from anthropic import Anthropic, AnthropicError
import os
from dotenv import load_dotenv
import json
from multiprocessing import Pool

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client with basic configuration
try:
    client = Anthropic(
        api_key=ANTHROPIC_API_KEY
    )
except Exception as e:
    print(f"Error initializing Anthropic client: {e}")
    raise

PROMPT_TEMPLATE = '''
Your task is to identify possible corrections in the transcript I give you.
You will be given a chunk of a transcript and a list of specific vocabulary words that could be in the chunk.

Vocabulary boost list: {word_boost_list}

{domain}
{custom_instructions}

Original text:
{sentence}

Your job is to identify words that are misspelled in the transcript and correct them if they are spelled incorrectly.
Use the given vocabulary list for any specific terminology or proper nouns that may be in the transcript.
Use the context of the transcript to guide your corrections.

Additional instructions:
- Do not overcorrect the transcript. Only correct the words that look misspelled or inconsistent.
- Capitalize the first letter of proper nouns.
- Keep the structure and word order intact.
- Do not add or delete words unless you are making a correction.
- You don't have to modify the original transcript if it already looks correct.
- If there are no corrections needed, you should return an empty array like this [].

Return your suggested corrections in JSON with a confidence score between 0 and 1. For example, if you are extremely confident in the correction, you should return 1. If you are not confident at all, you should return less than 0.5.
Do not include explanations in your response.
Return your response as a JSON array of objects, where each object contains:
- original_word: the misspelled word from the transcript
- corrected_word: your suggested correction
- confidence: a number between 0 and 1 indicating your confidence in the correction
'''

def process_single_sentence(args) -> Tuple[int, str, float]:
    index, sentence, domain, word_boost_list, custom_instructions, boost_level = args
    
    prompt = PROMPT_TEMPLATE.format(
        domain="Domain: " + domain if domain else "",
        word_boost_list=", ".join(word_boost_list),
        custom_instructions="Custom instructions: " + custom_instructions if custom_instructions else "",
        sentence=sentence
    )

    model = "claude-3-5-haiku-20241022" if boost_level == "low" else "claude-3-5-sonnet-20241022"
    
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
    except AnthropicError as e:
        print("Error: ", e)
        return index, sentence, 0.0

    print("Response: ", response.content[0].text)

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    if model == "claude-3-5-haiku-20241022":
        input_cost = (input_tokens / 1000000) * 0.80
        output_cost = (output_tokens / 1000000) * 4
    elif model == "claude-3-5-sonnet-20241022":
        input_cost = (input_tokens / 1000000) * 3
        output_cost = (output_tokens / 1000000) * 15

    cost = input_cost + output_cost
    corrected = make_corrections(sentence, response.content[0].text)
    return index, corrected, cost

def process_sentences(
    sentences: List[str],
    domain: Optional[str],
    word_boost_list: List[str],
    custom_instructions: Optional[str],
    boost_level: str
) -> Tuple[str, float]:
    """
    Process sentences using Claude to improve transcript accuracy
    
    Args:
        sentences: List of sentences to process
        domain: Optional domain context
        word_boost_list: List of important terms to consider
        custom_instructions: Optional custom processing instructions
        boost_level: Decides the model to use
    
    Returns:
        Tuple containing corrected transcript and total API usage cost
    """
    # Prepare arguments for each sentence
    args_list = [(i, sentence, domain, word_boost_list, custom_instructions, boost_level) 
                 for i, sentence in enumerate(sentences)]
    
    # Process sentences in parallel using multiprocessing
    with Pool() as pool:
        results = pool.map(process_single_sentence, args_list)
    
    # Sort results by index and extract corrected sentences and costs
    sorted_results = sorted(results, key=lambda x: x[0])
    corrected_sentences = [result[1] for result in sorted_results]
    total_cost = sum(result[2] for result in sorted_results)

    return " ".join(corrected_sentences), total_cost

def make_corrections(original_sentence: str, corrected_sentence: str) -> str:
    """Apply corrections to a sentence by replacing original words with corrected ones.
    
    Args:
        original_sentence: The original sentence text
        corrected_sentence: JSON string containing correction pairs
        
    Returns:
        The sentence with corrections applied
    """
    # Handle empty or invalid input
    if not original_sentence or not corrected_sentence:
        return original_sentence

    # Extract JSON portion if needed
    json_str = corrected_sentence
    if '[{' in corrected_sentence:
        try:
            _, json_str = corrected_sentence.split('[{', 1)
            json_str = '[{' + json_str
        except ValueError:
            return original_sentence

    # Try to parse corrections JSON
    try:
        corrections = json.loads(json_str)
        if not isinstance(corrections, list):
            return original_sentence
    except json.JSONDecodeError:
        return original_sentence

    # Apply each correction
    result = original_sentence
    for correction in corrections:
        if not isinstance(correction, dict) or 'original_word' not in correction or 'corrected_word' not in correction:
            continue
        result = result.replace(correction['original_word'], correction['corrected_word'])

    return result