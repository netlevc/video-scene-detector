from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # File Settings
    upload_dir: str = "uploads"
    processed_dir: str = "processed"
    temp_dir: str = "temp"
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    allowed_extensions: list = [".mp4", ".avi", ".mov", ".mkv"]
    
    # Video Processing Settings
    default_sensitivity: float = 0.8
    min_segment_duration: float = 1.0  # seconds
    max_segment_duration: float = 300.0  # seconds
    
    # PySceneDetect Settings
    scene_detect_fps: int = 30  # FPS for scene detection
    content_detector_threshold_min: int = 3
    content_detector_threshold_max: int = 27
    cursor_mask_size: int = 25
    cursor_mask_spacing: int = 60
    edge_mask_width: int = 50
    min_cursor_component_area: int = 500
    
    # CORS Settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # Session Settings
    session_timeout: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"


settings = Settings() 