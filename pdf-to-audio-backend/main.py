"""
PDF to Audio Conversion API - Simple Working Version
"""

import os
import tempfile
import time
import logging
from pathlib import Path
from typing import Optional, List
import uuid
import threading

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PDF to Audio Converter",
    description="Convert PDF documents to audio using MiniMax TTS",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_processor = PDFProcessor()
tts_service = TTSService()
audio_processor = AudioProcessor()

# Create directories for file storage
UPLOAD_DIR = Path("uploads")
AUDIO_DIR = Path("audio_output")
UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# Serve static audio files
app.mount("/audio", StaticFiles(directory="audio_output"), name="audio")

# In-memory storage for conversion status (use Redis in production)
conversion_status = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "PDF to Audio Converter API is running!"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "pdf_processor": "ready",
            "tts_service": "ready",
            "audio_processor": "ready"
        }
    }


@app.post("/api/convert-pdf")
async def convert_pdf_to_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Convert uploaded PDF to audio
    """
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    if file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File size too large (max 50MB)")
    
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize conversion status
        conversion_status[job_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting conversion...",
            "filename": file.filename
        }
        
        # Save uploaded file temporarily
        file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Start background conversion
        background_tasks.add_task(
            process_pdf_conversion,
            job_id,
            file_path,
            file.filename
        )
        
        return {
            "job_id": job_id,
            "message": "Conversion started",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error starting conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start conversion: {str(e)}")


@app.get("/api/conversion-status/{job_id}")
async def get_conversion_status(job_id: str):
    """
    Get conversion status by job ID
    """
    if job_id not in conversion_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return conversion_status[job_id]


@app.get("/api/download-audio/{job_id}")
async def download_audio(job_id: str):
    """
    Download converted audio file
    """
    if job_id not in conversion_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = conversion_status[job_id]
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Conversion not completed")
    
    audio_file = AUDIO_DIR / f"{job_id}.mp3"
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=audio_file,
        media_type="audio/mpeg",
        filename=f"{status['filename'].replace('.pdf', '.mp3')}"
    )


async def process_pdf_conversion(job_id: str, file_path: Path, filename: str):
    """
    Background task to process PDF conversion
    """
    try:
        # Update status: Extracting text
        conversion_status[job_id].update({
            "progress": 10,
            "message": "Extracting text from PDF..."
        })
        
        # Extract text from PDF
        text_content = await pdf_processor.extract_text(file_path)
        
        if not text_content.strip():
            raise Exception("No text found in PDF")
        
        # Update status: Processing text
        conversion_status[job_id].update({
            "progress": 30,
            "message": "Processing and chunking text..."
        })
        
        # Chunk text for TTS processing
        text_chunks = pdf_processor.chunk_text(text_content)
        
        # Update status: Converting to speech
        conversion_status[job_id].update({
            "progress": 50,
            "message": "Converting text to speech..."
        })
        
        # Convert text chunks to audio
        audio_files = []
        total_chunks = len(text_chunks)
        
        for i, chunk in enumerate(text_chunks):
            try:
                audio_data = await tts_service.text_to_speech(chunk)
                
                # Save chunk audio
                chunk_file = AUDIO_DIR / f"{job_id}_chunk_{i}.mp3"
                with open(chunk_file, "wb") as f:
                    f.write(audio_data)
                
                audio_files.append(chunk_file)
                
                # Update progress
                chunk_progress = 50 + (i + 1) / total_chunks * 30
                conversion_status[job_id].update({
                    "progress": chunk_progress,
                    "message": f"Converting chunk {i + 1}/{total_chunks}..."
                })
                
                # Small delay to prevent API rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                # Continue with other chunks
                continue
        
        if not audio_files:
            raise Exception("Failed to convert any text chunks to audio")
        
        # Update status: Merging audio
        conversion_status[job_id].update({
            "progress": 85,
            "message": "Merging audio files..."
        })
        
        # Merge audio files
        final_audio_path = AUDIO_DIR / f"{job_id}.mp3"
        await audio_processor.merge_audio_files(audio_files, final_audio_path)
        
        # Clean up chunk files
        for chunk_file in audio_files:
            try:
                chunk_file.unlink()
            except:
                pass
        
        # Calculate estimated duration (rough estimate)
        estimated_duration = len(text_content.split()) / 150  # ~150 words per minute
        
        # Update status: Completed
        conversion_status[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Conversion completed successfully!",
            "audioUrl": f"/audio/{job_id}.mp3",
            "estimatedDuration": estimated_duration
        })
        
        # Clean up original PDF
        try:
            file_path.unlink()
        except:
            pass
            
    except Exception as e:
        logger.error(f"Conversion failed for job {job_id}: {str(e)}")
        conversion_status[job_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"Conversion failed: {str(e)}"
        })
        
        # Clean up files
        try:
            file_path.unlink()
        except:
            pass


@app.delete("/api/cleanup/{job_id}")
async def cleanup_job(job_id: str):
    """
    Clean up job files and status
    """
    if job_id in conversion_status:
        del conversion_status[job_id]
    
    # Clean up files
    audio_file = AUDIO_DIR / f"{job_id}.mp3"
    if audio_file.exists():
        audio_file.unlink()
    
    return {"message": "Job cleaned up successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
