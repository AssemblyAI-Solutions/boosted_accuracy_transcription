# BAT: Boosted Accuracy Transcription

A tool that improves transcription accuracy by post-processing AssemblyAI transcripts using LLMs.

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip3 install -r requirements.txt
```
3. Copy `.env.sample` to `.env` and fill in your API keys:
   - ANTHROPIC_API_KEY

## Usage

1. Start the API server:
```bash
uvicorn api:app --reload
```

2. The API accepts the following parameters:

   | Parameter | Description |
   |-----------|-------------|
   | `transcript_id` | **Required.** The transcript ID from AssemblyAI |
   | `domain` | Optional domain context (e.g., medical, legal, sales) |
   | `word_boost_list` | Custom terminology that may be mistranscribed |
   | `custom_instructions` | Additional formatting instructions or context |
   | `boost_level` | Accuracy vs cost tradeoff (`high`/`low`, defaults to `high`) |
   | `confidence_filter` | Confidence threshold between 0-1 for selective correction (defaults to 1.0) |

3. Include your AssemblyAI API key in the request header as `Authorization: <API_KEY>`