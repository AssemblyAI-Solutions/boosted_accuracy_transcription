from fastapi import FastAPI, HTTPException, Header
from typing import List, Optional
from pydantic import BaseModel
from assembly import get_transcript_and_sentences, transcribe_audio
from llm import process_sentences
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

app = FastAPI()

class BoostLevel(str, Enum):
    HIGH = "high"
    LOW = "low"

class TranscriptRequest(BaseModel):
    transcript_id: str
    domain: Optional[str] = None
    word_boost_list: List[str]
    custom_instructions: Optional[str] = None
    boost_level: Optional[BoostLevel] = BoostLevel.HIGH

class TranscriptResponse(BaseModel):
    original_transcript: str
    corrected_transcript: str
    usage_costs: float
    time_taken_seconds: float

@app.post("/boost_accuracy", response_model=TranscriptResponse)
async def process_transcript(
    request: TranscriptRequest,
    authorization: str = Header(default=""),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        # Get transcript and sentences from AssemblyAI
        transcript, sentences = await get_transcript_and_sentences(
            request.transcript_id,
            authorization
        )

        print('OG Transcript: ', transcript)

        if not transcript or not sentences:
            raise HTTPException(
                status_code=404,
                detail="Transcript not found or processing failed"
            )

        start_time = time.time()
        # Process sentences with Anthropic - run in a thread pool since it's CPU intensive
        with ThreadPoolExecutor() as pool:
            corrected_transcript, total_cost = await asyncio.get_event_loop().run_in_executor(
                pool,
                process_sentences,
                sentences,
                request.domain,
                request.word_boost_list,
                request.custom_instructions,
                request.boost_level
            )
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")

        return TranscriptResponse(
            original_transcript=transcript,
            corrected_transcript=corrected_transcript,
            usage_costs=total_cost,
            time_taken_seconds=end_time - start_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# @app.get("/transcribe_audio")
# def transcribe(
#     url: str = "https://api.assemblyai-solutions.com/storage/v1/object/public/medical/voices_medical_conversation12_Outdoor_audio.wav?t=2025-01-09T21%3A22%3A05.218Z",
#     authorization: str = Header(default=""),
# ):
#     if not authorization:
#         raise HTTPException(status_code=401, detail="Authorization header required")

#     transcript_id = transcribe_audio(url, authorization)
#     return {"transcript_id": transcript_id}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)