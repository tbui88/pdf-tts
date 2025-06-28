"""
PDF to Audio Conversion API - Working Demo Version
This version uses minimal dependencies and mock processing for demonstration
"""

import os
import time
import uuid
import json
import threading
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

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

# Create directories for file storage
UPLOAD_DIR = Path("uploads")
AUDIO_DIR = Path("audio_output")
UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# In-memory storage for conversion status
conversion_status: Dict[str, Dict[str, Any]] = {}


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
            "tts_service": "ready (mock)",
            "audio_processor": "ready"
        }
    }


@app.post("/api/convert-pdf")
async def convert_pdf_to_audio(file: UploadFile = File(...)):
    """Convert uploaded PDF to audio"""
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    if file.size and file.size > 50 * 1024 * 1024:  # 50MB limit
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
        
        # Save uploaded file temporarily (optional for demo)
        file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Start background conversion simulation
        thread = threading.Thread(
            target=simulate_pdf_conversion,
            args=(job_id, file.filename)
        )
        thread.daemon = True
        thread.start()
        
        return {
            "job_id": job_id,
            "message": "Conversion started",
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start conversion: {str(e)}")


@app.get("/api/conversion-status/{job_id}")
async def get_conversion_status(job_id: str):
    """Get conversion status by job ID"""
    if job_id not in conversion_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return conversion_status[job_id]


@app.get("/api/download-audio/{job_id}")
async def download_audio(job_id: str):
    """Download converted audio file"""
    if job_id not in conversion_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = conversion_status[job_id]
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Conversion not completed")
    
    # Generate mock audio content
    mock_audio = generate_mock_audio()
    
    filename = status['filename'].replace('.pdf', '.mp3')
    
    return Response(
        content=mock_audio,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def simulate_pdf_conversion(job_id: str, filename: str):
    """Simulate PDF conversion process"""
    try:
        # Simulate different stages with delays
        stages = [
            (10, "Extracting text from PDF..."),
            (25, "Processing and chunking text..."),
            (40, "Converting text to speech..."),
            (55, "Converting chunk 1/4..."),
            (70, "Converting chunk 2/4..."),
            (85, "Converting chunk 3/4..."),
            (95, "Converting chunk 4/4..."),
            (98, "Merging audio files..."),
        ]
        
        for progress, message in stages:
            time.sleep(1.5)  # Simulate processing time
            conversion_status[job_id].update({
                'progress': progress,
                'message': message
            })
        
        # Complete conversion
        time.sleep(2)
        conversion_status[job_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Conversion completed successfully!',
            'audioUrl': f'/api/download-audio/{job_id}',
            'estimatedDuration': 45  # Mock duration in seconds
        })
        
    except Exception as e:
        conversion_status[job_id].update({
            'status': 'failed',
            'progress': 0,
            'message': f'Conversion failed: {str(e)}'
        })


def generate_mock_audio() -> bytes:
    """Generate a simple mock MP3 file for demonstration"""
    
    # Create a basic MP3 file with ID3 header and silence
    id3_header = b'ID3\x03\x00\x00\x00\x00\x00\x00'
    
    # MP3 frame header for 44.1kHz, stereo, 128kbps
    mp3_frame = bytes([
        0xFF, 0xFB, 0x90, 0x00,  # Sync word and header
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ])
    
    # Create silence frames (about 10 seconds of silence)
    silence_frame = bytes([0x00] * 144)
    frames = [mp3_frame] + [silence_frame] * 400
    
    return id3_header + b''.join(frames)


@app.delete("/api/cleanup/{job_id}")
async def cleanup_job(job_id: str):
    """Clean up job files and status"""
    if job_id in conversion_status:
        del conversion_status[job_id]
    
    # Clean up uploaded file
    for file_path in UPLOAD_DIR.glob(f"{job_id}_*"):
        try:
            file_path.unlink()
        except:
            pass
    
    return {"message": "Job cleaned up successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
