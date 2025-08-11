# This file defines the data structures (models) used throughout the Video Scene Detector application
# These models define what information is stored and how it's organized

# Import the necessary libraries for creating data models
from pydantic import BaseModel  # This helps create data models with validation
from typing import List, Optional  # These are used for type hints (making code more readable)
from datetime import datetime  # This handles dates and times
from enum import Enum  # This creates a set of predefined values


class ChangeType(str, Enum):
    """Types of changes that can be detected in a video"""
    BUTTON_CLICK = "button_click"  # When a button is clicked in the UI
    DIALOG_OPEN = "dialog_open"  # When a dialog or popup window opens
    UI_UPDATE = "ui_update"  # When the user interface updates (new content appears)
    FORM_INPUT = "form_input"  # When text is entered into a form
    GENERAL_CHANGE = "general_change"  # Any other type of change
    UNKNOWN = "unknown"  # When the type of change cannot be determined


class VideoInfo(BaseModel):
    """Information about a video file"""
    filename: str  # The name of the video file
    duration: float  # How long the video is in seconds
    frame_rate: float  # How many frames per second the video has
    resolution: str  # The video resolution (e.g., "1920x1080")
    total_frames: int  # Total number of frames in the video
    file_size: int  # Size of the video file in bytes


class CutPoint(BaseModel):
    """A point in the video where a scene change occurs"""
    frame_number: int  # Which frame number the cut point is at
    timestamp: float  # The time in seconds when the cut point occurs
    confidence: float  # How confident the system is about this cut point (0.0 to 1.0)
    change_type: str  # What type of change was detected (from ChangeType enum)
    description: str  # A human-readable description of the change
    thumbnail: Optional[str] = None  # Optional image showing what the frame looks like


class VideoSession(BaseModel):
    """A session for processing a single video"""
    session_id: str  # Unique identifier for this processing session
    video_path: str  # Path to the video file on the server
    video_info: VideoInfo  # Information about the video
    cut_points: List[CutPoint]  # List of all detected cut points
    created_at: datetime  # When this session was created
    status: str  # Current status of the session (uploaded, analyzed, processed, etc.)


class AnalysisRequest(BaseModel):
    """Request to analyze a video for scene changes"""
    session_id: str  # Which video session to analyze
    sensitivity: float = 0.8  # How sensitive the detection should be (0.1 to 1.0)
    ignore_cursor: bool = True  # Whether to ignore mouse cursor movements
    min_segment_duration: float = 1.0  # Minimum length of video segments in seconds


class AnalysisResponse(BaseModel):
    """Response containing the results of video analysis"""
    session_id: str  # The session that was analyzed
    video_info: VideoInfo  # Information about the video
    cut_points: List[CutPoint]  # All detected cut points
    processing_time: Optional[float] = None  # How long the analysis took (in seconds)


class ProcessingRequest(BaseModel):
    """Request to process a video into segments"""
    session_id: str  # Which video session to process
    cut_points: List[CutPoint]  # The cut points to use for creating segments


class ProcessingResponse(BaseModel):
    """Response containing information about processed video segments"""
    session_id: str  # The session that was processed
    zip_file_path: str  # Path to the folder containing processed segments
    segments_count: int  # How many video segments were created
    processing_time: Optional[float] = None  # How long the processing took (in seconds)


class UploadResponse(BaseModel):
    """Response when a video file is uploaded"""
    session_id: str  # Unique identifier for the new session
    filename: str  # Name of the uploaded file
    file_size: int  # Size of the uploaded file in bytes


class PreviewResponse(BaseModel):
    """Response containing video preview information"""
    session_id: str  # The session ID
    video_info: VideoInfo  # Information about the video
    cut_points: List[CutPoint]  # Any existing cut points (empty if not analyzed yet) 