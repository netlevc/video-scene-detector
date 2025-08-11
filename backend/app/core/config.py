# This file contains all the configuration settings for the Video Scene Detector application
# These settings control how the application behaves, what files it accepts, and how it processes videos

# Import the necessary libraries for managing configuration
from pydantic_settings import BaseSettings  # This helps validate and manage configuration settings
from typing import Optional  # This is used for type hints (making code more readable)


class Settings(BaseSettings):
    """Configuration settings for the Video Scene Detector application"""
    
    # Server Settings - These control how the web server runs
    host: str = "0.0.0.0"  # The IP address the server listens on (0.0.0.0 means all addresses)
    port: int = 8000  # The port number the server runs on
    debug: bool = False  # Whether to run in debug mode (shows more detailed error messages)
    
    # File Settings - These control what files the application can handle
    upload_dir: str = "uploads"  # Folder where uploaded videos are stored
    processed_dir: str = "processed"  # Folder where processed video segments are saved
    temp_dir: str = "temp"  # Folder for temporary files during processing
    max_file_size: int = 500 * 1024 * 1024  # Maximum file size allowed (500MB)
    allowed_extensions: list = [".mp4", ".avi", ".mov", ".mkv"]  # Video file types that can be uploaded
    
    # Video Processing Settings - These control how videos are analyzed and processed
    default_sensitivity: float = 0.8  # How sensitive the scene detection is (0.1 = less sensitive, 1.0 = very sensitive)
    min_segment_duration: float = 1.0  # Minimum length of a video segment in seconds
    max_segment_duration: float = 300.0  # Maximum length of a video segment in seconds (5 minutes)
    
    # PySceneDetect Settings - These control the scene detection algorithm
    scene_detect_fps: int = 30  # Frame rate used for scene detection analysis
    content_detector_threshold_min: int = 3  # Minimum threshold for detecting changes (lower = more sensitive)
    content_detector_threshold_max: int = 27  # Maximum threshold for detecting changes (higher = less sensitive)
    cursor_mask_size: int = 25  # Size of the area around cursor to ignore (in pixels)
    cursor_mask_spacing: int = 60  # How often to check for cursor positions (in frames)
    edge_mask_width: int = 50  # Width of edge areas to ignore (in pixels)
    min_cursor_component_area: int = 500  # Minimum area for cursor detection (in pixels)
    
    # CORS Settings - These control which websites can access the API
    cors_origins: list = ["*"]  # Which websites can make requests (* = all websites)
    cors_allow_credentials: bool = True  # Whether to allow cookies and authentication
    cors_allow_methods: list = ["*"]  # Which HTTP methods are allowed (* = all methods)
    cors_allow_headers: list = ["*"]  # Which headers are allowed (* = all headers)
    
    # Session Settings - These control how long user sessions last
    session_timeout: int = 3600  # How long a session lasts in seconds (1 hour)
    
    class Config:
        env_file = ".env"  # Load settings from a .env file if it exists


# Create a global settings object that can be used throughout the application
settings = Settings() 