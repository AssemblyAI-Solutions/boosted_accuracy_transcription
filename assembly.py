from typing import Tuple, List
import assemblyai as aai
from fastapi import HTTPException

async def get_transcript_and_sentences(
    transcript_id: str,
    auth_token: str,
    confidence_filter: float = 1.0
) -> Tuple[str, List[str]]:
    """
    Retrieve transcript and sentences from AssemblyAI
    
    Args:
        transcript_id: The ID of the transcript to retrieve
        auth_token: AssemblyAI authentication token
    
    Returns:
        Tuple containing the full transcript text and list of sentences
    """
    try:
        # Initialize AssemblyAI client
        aai.settings.api_key = auth_token
        
        # Get transcript by ID
        transcript = aai.Transcript.get_by_id(transcript_id)
        
        if transcript.status != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Transcript status is {transcript.status}"
            )

        # Get sentences
        sentences = transcript.get_paragraphs()
        
        if confidence_filter < 1.0:
            sentences = [sentence for sentence in sentences if sentence.confidence < confidence_filter]
            if len(sentences) == 0:
                return transcript.text, []
            
        return transcript.text, [sentence.text for sentence in sentences]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving transcript: {str(e)}"
        ) 
    
def transcribe_audio(url: str, auth_token: str) -> str:
    aai.settings.api_key = auth_token
    transcriber = aai.Transcriber(config=aai.TranscriptionConfig(language_detection=True))
    transcript = transcriber.transcribe(url)
    
    return transcript.id