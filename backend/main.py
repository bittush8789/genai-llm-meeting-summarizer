import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Import local modules
from database.mysql_db import init_db, save_meeting
from database.chroma_db import store_transcript_in_chroma
from services.transcription import transcribe_audio
from services.summarization import (
    generate_meeting_summary,
    extract_action_items,
    extract_decisions,
)

# Directory configurations
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MySQL tables
    print("Starting up: Initializing database and services...")
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Database initialization failed (check if MySQL is running): {e}")
    yield
    # Shutdown: clean up if needed
    print("Shutting down...")


app = FastAPI(
    title="AI Meeting Notes Summarizer API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_audio(
    file: UploadFile = File(None),
    transcript_text: str = Form(None),
    llm_model: str = Form("llama-3.3-70b-versatile"),
    transcription_model: str = Form("local-whisper-base")
):
    """
    Process uploaded audio OR pasted transcript text:
    1. Check if transcript text is provided directly
    2. Otherwise, save and transcribe audio
    3. Generate Summary, Action Items, and Decisions using LangChain + GroQ
    4. Store meeting details in MySQL
    5. Generate & store embeddings in ChromaDB
    6. Return response
    """
    file_path = None
    transcript = ""
    title = ""

    try:
        # Check manual transcript first
        if transcript_text and transcript_text.strip():
            print("Processing manually pasted transcript...")
            transcript = transcript_text.strip()
            title = "Pasted transcript notes"
        elif file:
            # 1. Validate file extension
            allowed_extensions = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
                )
                
            # 2. Save audio file locally
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to save audio file locally: {e}")
                
            # 3. Transcribe speech to text using Whisper
            print(f"Step 1/4: Transcribing speech to text using model '{transcription_model}'...")
            transcript = transcribe_audio(file_path, model_name=transcription_model)
            title = os.path.splitext(file.filename)[0].replace("_", " ").replace("-", " ").capitalize()
        else:
            raise HTTPException(
                status_code=400,
                detail="Validation Error: Please upload an audio file or paste a transcript manually."
            )

        if not transcript.strip():
            raise HTTPException(
                status_code=422,
                detail="Transcript content is empty. Cannot process summary."
            )

        # 4. Generate AI summary and extract key structures
        print(f"Step 2/4: Extracting meeting analytics using model '{llm_model}'...")
        summary = generate_meeting_summary(transcript, model_name=llm_model)
        action_items = extract_action_items(transcript, model_name=llm_model)
        decisions = extract_decisions(transcript, model_name=llm_model)

        # 5. Store meeting details in MySQL
        print("Step 3/4: Storing data in MySQL...")
        meeting_id = None
        try:
            meeting_id = save_meeting(
                title=title,
                transcript=transcript,
                summary=summary,
                decisions=decisions,
                action_items=action_items
            )
        except Exception as db_err:
            print(f"Warning: MySQL save failed: {db_err}")
            # We don't fail the request completely, we want to at least return the AI summaries.
            # But let's set a placeholder ID.
            meeting_id = 0

        # 6. Store embeddings in ChromaDB
        print("Step 4/4: Generating embeddings and saving to ChromaDB...")
        try:
            store_transcript_in_chroma(
                meeting_id=meeting_id,
                title=title,
                transcript=transcript
            )
        except Exception as vec_err:
            print(f"Warning: Vectorstore save failed: {vec_err}")

        # 7. Return structured JSON response
        return {
            "success": True,
            "id": meeting_id,
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "decisions": decisions,
            "action_items": action_items
        }

    except ValueError as ve:
        # E.g. Missing GroQ Key
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        # Re-raise HTTP exceptions directly
        raise he
    except Exception as e:
        print(f"Error processing meeting request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Clean up local saved audio to save space
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up local file: {file_path}")
            except Exception as e:
                print(f"Failed to delete local audio file: {e}")


# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"Warning: Static files path '{frontend_path}' not found.")
