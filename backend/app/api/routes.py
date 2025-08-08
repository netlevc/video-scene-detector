from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
import os
import shutil
from pathlib import Path
from typing import List

from ..models.video import (
    AnalysisRequest, AnalysisResponse, ProcessingRequest, ProcessingResponse,
    UploadResponse, PreviewResponse
)
from ..services.video_processor import VideoProcessor
from ..core.config import settings

router = APIRouter()
processor = VideoProcessor()


@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file"""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.allowed_extensions}"
        )
    
    # Validate file size
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size / (1024*1024)}MB"
        )
    
    # Create upload directory
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Save file
    file_path = Path(settings.upload_dir) / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create session
    session_id = processor.create_session(str(file_path))
    
    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        file_size=file.size
    )


@router.get("/preview/{session_id}", response_model=PreviewResponse)
async def get_preview(session_id: str):
    """Get video preview and current cut points"""
    
    session = processor.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return PreviewResponse(
        session_id=session_id,
        video_info=session.video_info,
        cut_points=session.cut_points
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_video(request: AnalysisRequest):
    """Analyze video for scene changes"""
    
    try:
        cut_points = processor.detect_changes(
            session_id=request.session_id,
            sensitivity=request.sensitivity,
            ignore_cursor=request.ignore_cursor,
            min_segment_duration=request.min_segment_duration
        )
        
        session = processor.get_session(request.session_id)
        
        return AnalysisResponse(
            session_id=request.session_id,
            video_info=session.video_info,
            cut_points=cut_points
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/adjust/{session_id}")
async def adjust_cuts(session_id: str, cut_points: List[dict]):
    """Adjust cut points manually"""
    
    session = processor.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Convert dict to CutPoint objects
    from app.models.video import CutPoint
    adjusted_cuts = []
    for cp in cut_points:
        adjusted_cuts.append(CutPoint(**cp))
    
    session.cut_points = adjusted_cuts
    return {"message": "Cut points adjusted successfully"}


@router.post("/process", response_model=ProcessingResponse)
async def process_video(request: ProcessingRequest):
    """Process video into segments"""
    
    try:
        output_path = processor.process_video(
            session_id=request.session_id,
            cut_points=request.cut_points
        )
        
        session = processor.get_session(request.session_id)
        segments_count = len(request.cut_points) + 1  # +1 for the last segment
        
        # Verify the output directory exists
        output_dir = Path(output_path)
        if not output_dir.exists():
            raise Exception("Output directory was not created")
        
        if not output_dir.is_dir():
            raise Exception("Output path is not a directory")
        
        return ProcessingResponse(
            session_id=request.session_id,
            zip_file_path=str(output_path),  # Keep same field name for compatibility
            segments_count=segments_count
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/download/{session_id}")
async def download_folder(session_id: str):
    """Get processed video segments folder location"""
    
    session = processor.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    download_dir = Path("..") / "download"
    
    if not download_dir.exists():
        raise HTTPException(status_code=404, detail="Download folder not found")
    
    # Return folder information instead of file download
    files = []
    for file_path in download_dir.rglob("*"):
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size
            })
    
    return {
        "session_id": session_id,
        "output_directory": str(download_dir),
        "files": files,
        "message": f"Files are available in: {download_dir}"
    } 