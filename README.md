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
   - `domain`: (e.g., medical, legal, sales)
   - `word_boost_list`: (custom terminology that may be mistranscribed)
   - `transcript_id`: (the transcript ID from AssemblyAI)
   - `custom_instructions`: (this can be formatting instructions, additional context, etc.)
   - `boost_level`: (defaults to `high`, `high` is more accurate but more expensive, `low` is less accurate but cheaper)

3. Include your AssemblyAI API key in the request header as `Authorization: <API_KEY>`