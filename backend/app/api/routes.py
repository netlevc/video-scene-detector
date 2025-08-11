# This file contains all the API endpoints (web routes) for the Video Scene Detector
# These endpoints handle requests from the frontend web interface

# Import the necessary libraries for creating web API endpoints
from fastapi import APIRouter, UploadFile, File, HTTPException, Form  # FastAPI components for web endpoints
from fastapi.responses import FileResponse  # For sending files back to the client
import os  # For file and directory operations
import shutil  # For copying files
from pathlib import Path  # For handling file paths
from typing import List  # For type hints

# Import our custom models and services
from ..models.video import (
    AnalysisRequest, AnalysisResponse, ProcessingRequest, ProcessingResponse,
    UploadResponse, PreviewResponse
)  # Data models for requests and responses
from ..services.video_processor import VideoProcessor  # Main video processing logic
from ..core.config import settings  # Application configuration

# Create a router to organize all our API endpoints
router = APIRouter()

# Create a global video processor instance to handle all video operations
processor = VideoProcessor()


@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Handle video file uploads from the frontend"""
    
    # Validate that the uploaded file has an allowed extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,  # Bad request error
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.allowed_extensions}"
        )
    
    # Check if the file is too large
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=400,  # Bad request error
            detail=f"File too large. Maximum size: {settings.max_file_size / (1024*1024)}MB"
        )
    
    # Create the uploads directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Save the uploaded file to the uploads directory
    file_path = Path(settings.upload_dir) / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)  # Copy the uploaded file to disk
    
    # Create a new processing session for this video
    session_id = processor.create_session(str(file_path))
    
    # Return information about the uploaded file
    return UploadResponse(
        session_id=session_id,  # Unique identifier for this session
        filename=file.filename,  # Name of the uploaded file
        file_size=file.size  # Size of the file in bytes
    )


@router.get("/preview/{session_id}", response_model=PreviewResponse)
async def get_preview(session_id: str):
    """Get information about a video session and any existing cut points"""
    
    # Retrieve the session by its ID
    session = processor.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Return the session information
    return PreviewResponse(
        session_id=session_id,
        video_info=session.video_info,  # Video metadata (duration, resolution, etc.)
        cut_points=session.cut_points  # Any cut points that have been detected
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_video(request: AnalysisRequest):
    """Analyze a video to detect scene changes and cut points"""
    
    try:
        # Use the video processor to detect changes in the video
        cut_points = processor.detect_changes(
            session_id=request.session_id,  # Which video to analyze
            sensitivity=request.sensitivity,  # How sensitive the detection should be
            ignore_cursor=request.ignore_cursor,  # Whether to ignore mouse cursor movements
            min_segment_duration=request.min_segment_duration  # Minimum segment length
        )
        
        # Get the updated session information
        session = processor.get_session(request.session_id)
        
        # Return the analysis results
        return AnalysisResponse(
            session_id=request.session_id,
            video_info=session.video_info,
            cut_points=cut_points  # All detected cut points
        )
        
    except ValueError as e:
        # Handle errors where the session is not found
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Handle any other errors during analysis
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/adjust/{session_id}")
async def adjust_cuts(session_id: str, cut_points: List[dict]):
    """Allow manual adjustment of cut points by the user"""
    
    # Get the session
    session = processor.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Convert the dictionary data back to CutPoint objects
    from app.models.video import CutPoint
    adjusted_cuts = []
    for cp in cut_points:
        adjusted_cuts.append(CutPoint(**cp))
    
    # Update the session with the adjusted cut points
    session.cut_points = adjusted_cuts
    return {"message": "Cut points adjusted successfully"}


@router.post("/process", response_model=ProcessingResponse)
async def process_video(request: ProcessingRequest):
    """Process a video into segments based on the detected cut points"""
    
    try:
        # Use the video processor to create video segments
        output_path = processor.process_video(
            session_id=request.session_id,  # Which video to process
            cut_points=request.cut_points  # The cut points to use for segmentation
        )
        
        # Get the session information
        session = processor.get_session(request.session_id)
        segments_count = len(request.cut_points) + 1  # +1 for the last segment
        
        # Verify that the output directory was created successfully
        output_dir = Path(output_path)
        if not output_dir.exists():
            raise Exception("Output directory was not created")
        
        if not output_dir.is_dir():
            raise Exception("Output path is not a directory")
        
        # Return information about the processing results
        return ProcessingResponse(
            session_id=request.session_id,
            zip_file_path=str(output_path),  # Path to the output folder
            segments_count=segments_count  # How many segments were created
        )
        
    except ValueError as e:
        # Handle errors where the session is not found
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Handle any other errors during processing
        print(f"❌ Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/download/{session_id}")
async def download_folder(session_id: str):
    """Get information about the processed video segments and where to find them"""
    
    # Get the session
    session = processor.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Path to the download directory where processed files are stored
    download_dir = Path("..") / "download"
    
    # Check if the download directory exists
    if not download_dir.exists():
        raise HTTPException(status_code=404, detail="Download folder not found")
    
    # Collect information about all files in the download directory
    files = []
    for file_path in download_dir.rglob("*"):
        if file_path.is_file():
            files.append({
                "name": file_path.name,  # Name of the file
                "path": str(file_path),  # Full path to the file
                "size": file_path.stat().st_size  # Size of the file in bytes
            })
    
    # Return information about the processed files
    return {
        "session_id": session_id,
        "output_directory": str(download_dir),  # Path to the output folder
        "files": files,  # List of all processed files
        "message": f"Files are available in: {download_dir}"
    } 