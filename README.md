# 🦇 BAT – Boosted Accuracy Transcription

Open-source API designed to improve ASR transcription accuracy by post-processing with Anthropic's LLMs. This project is inspired by the [IEEE paper](https://arxiv.org/pdf/2409.09554) by [S. K. Sahu et al. (2023)](https://scholar.google.com/citations?user=6664y6cAAAAJ&hl=en).

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

4. You can use the `test.py` script to test the API locally.