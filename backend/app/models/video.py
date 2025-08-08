from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ChangeType(str, Enum):
    BUTTON_CLICK = "button_click"
    DIALOG_OPEN = "dialog_open"
    UI_UPDATE = "ui_update"
    FORM_INPUT = "form_input"
    GENERAL_CHANGE = "general_change"
    UNKNOWN = "unknown"


class VideoInfo(BaseModel):
    filename: str
    duration: float
    frame_rate: float
    resolution: str
    total_frames: int
    file_size: int


class CutPoint(BaseModel):
    frame_number: int
    timestamp: float
    confidence: float
    change_type: str
    description: str
    thumbnail: Optional[str] = None


class VideoSession(BaseModel):
    session_id: str
    video_path: str
    video_info: VideoInfo
    cut_points: List[CutPoint]
    created_at: datetime
    status: str


class AnalysisRequest(BaseModel):
    session_id: str
    sensitivity: float = 0.8
    ignore_cursor: bool = True
    min_segment_duration: float = 1.0


class AnalysisResponse(BaseModel):
    session_id: str
    video_info: VideoInfo
    cut_points: List[CutPoint]
    processing_time: Optional[float] = None


class ProcessingRequest(BaseModel):
    session_id: str
    cut_points: List[CutPoint]


class ProcessingResponse(BaseModel):
    session_id: str
    zip_file_path: str
    segments_count: int
    processing_time: Optional[float] = None


class UploadResponse(BaseModel):
    session_id: str
    filename: str
    file_size: int


class PreviewResponse(BaseModel):
    session_id: str
    video_info: VideoInfo
    cut_points: List[CutPoint] 