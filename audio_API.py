"""
FastAPI endpoints for audio file handling.
This module contains API routes for listing, retrieving, and managing audio files.
"""
import os
import glob
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import wave
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Create a router for audio endpoints
router = APIRouter(prefix="/audio", tags=["audio"])

# Models for API responses
class AudioFileInfo(BaseModel):
    filename: str
    path: str
    timestamp: Optional[str] = None
    duration: Optional[float] = None
    size: Optional[int] = None

class AudioFilesList(BaseModel):
    files: List[AudioFileInfo]
    count: int

@router.get("/list", response_model=AudioFilesList)
def list_audio_files():
    """Get a list of all audio recordings"""
    try:
        files = glob.glob("audio_files/*.wav")
        files.sort(key=os.path.getctime, reverse=True)  # Newest first
        
        file_info = []
        for file_path in files:
            info = AudioFileInfo(
                filename=os.path.basename(file_path),
                path=file_path,
                size=os.path.getsize(file_path)
            )
            
            # Try to get timestamp from filename
            try:
                parts = os.path.splitext(os.path.basename(file_path))[0].split('_')
                if len(parts) >= 3:
                    timestamp = f"{parts[1]}_{parts[2]}"
                    info.timestamp = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
                
            # Try to get duration
            try:
                with wave.open(file_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    info.duration = frames / float(rate)
            except:
                pass
                
            file_info.append(info)
            
        return AudioFilesList(files=file_info, count=len(file_info))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing audio files: {str(e)}")

@router.get("/file/{filename}")
def get_audio_file(filename: str):
    """Stream an audio file"""
    file_path = os.path.join("audio_files", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    return FileResponse(
        file_path, 
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.delete("/file/{filename}")
def delete_audio_file(filename: str):
    """Delete an audio file"""
    file_path = os.path.join("audio_files", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    try:
        os.remove(file_path)
        return {"status": "success", "message": f"Deleted audio file: {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")