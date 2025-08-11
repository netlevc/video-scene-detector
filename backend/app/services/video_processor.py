# This file contains the main video processing logic for the Video Scene Detector
# It handles uploading videos, detecting scene changes, and creating video segments

# Import the necessary libraries for video processing and file operations
import os  # For file and directory operations
import cv2  # OpenCV library for computer vision and image processing
import numpy as np  # NumPy for numerical operations on arrays
from typing import List, Optional, Tuple  # Type hints for better code readability
from datetime import datetime  # For handling dates and times
import uuid  # For generating unique identifiers
import json  # For working with JSON data
from pathlib import Path  # For handling file paths in a cross-platform way

# PySceneDetect imports - This is the main library for detecting scene changes in videos
from scenedetect import SceneManager, ContentDetector  # Core scene detection classes
from scenedetect.stats_manager import StatsManager  # Manages statistics during scene detection
from scenedetect.video_manager import VideoManager  # Handles video file operations
from scenedetect.frame_timecode import FrameTimecode  # Converts between frames and time
from scenedetect.scene_manager import save_images  # For saving frame images

# Import our custom models and configuration
from ..models.video import VideoInfo, CutPoint, ChangeType, VideoSession  # Our data models
from ..core.config import settings  # Application configuration settings


class VideoProcessor:
    """Main class for processing videos and detecting scene changes"""
    
    def __init__(self):
        """Initialize the video processor with an empty sessions dictionary"""
        # Store all active video processing sessions
        # Each session contains information about one video being processed
        self.sessions: dict[str, VideoSession] = {}
    
    def create_session(self, video_path: str) -> str:
        """Create a new video processing session for a given video file"""
        # Generate a unique identifier for this session
        session_id = str(uuid.uuid4())
        
        # Extract information about the video (duration, resolution, etc.)
        video_info = self._get_video_info(video_path)
        
        # Create a new session object with all the video information
        session = VideoSession(
            session_id=session_id,  # Unique identifier
            video_path=video_path,  # Path to the video file
            video_info=video_info,  # Video metadata (duration, resolution, etc.)
            cut_points=[],  # No cut points detected yet
            created_at=datetime.now(),  # Current timestamp
            status="uploaded"  # Initial status
        )
        
        # Store the session for later use
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[VideoSession]:
        """Retrieve a session by its unique identifier"""
        return self.sessions.get(session_id)
    
    def _get_video_info(self, video_path: str) -> VideoInfo:
        """Extract basic information about a video file (duration, resolution, etc.)"""
        # Open the video file using OpenCV
        cap = cv2.VideoCapture(video_path)
        
        # Check if the video file was opened successfully
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Extract video properties using OpenCV
        fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Video width in pixels
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Video height in pixels
        duration = frame_count / fps if fps > 0 else 0  # Calculate duration in seconds
        file_size = os.path.getsize(video_path)  # Get file size in bytes
        
        # Release the video capture object to free memory
        cap.release()
        
        # Create and return a VideoInfo object with all the extracted data
        return VideoInfo(
            filename=os.path.basename(video_path),  # Just the filename, not the full path
            duration=duration,
            frame_rate=fps,
            resolution=f"{width}x{height}",
            total_frames=frame_count,
            file_size=file_size
        )
    
    def detect_changes(self, session_id: str, sensitivity: float = 0.8, 
                      ignore_cursor: bool = True, min_segment_duration: float = 1.0) -> List[CutPoint]:
        """Detect scene changes in a video using PySceneDetect library"""
        # Get the session for this video
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        video_path = session.video_path
        
        # Use PySceneDetect to find scene changes in the video
        cut_points = self._detect_scenes_pyscenedetect(video_path, sensitivity, ignore_cursor, min_segment_duration)
        
        # Update the session with the detected cut points
        session.cut_points = cut_points
        session.status = "analyzed"  # Mark the session as analyzed
        
        return cut_points
    
    def _detect_scenes_pyscenedetect(self, video_path: str, sensitivity: float, 
                                   ignore_cursor: bool, min_segment_duration: float) -> List[CutPoint]:
        """Use PySceneDetect ContentDetector to find scene changes in the video"""
        
        # Calculate the detection threshold based on sensitivity setting
        # Higher sensitivity = lower threshold = more cut points detected
        threshold_range = settings.content_detector_threshold_max - settings.content_detector_threshold_min
        threshold = int(settings.content_detector_threshold_max - (sensitivity * threshold_range))
        threshold = max(settings.content_detector_threshold_min, min(settings.content_detector_threshold_max, threshold))
        
        # Initialize PySceneDetect components
        stats_manager = StatsManager()  # Manages statistics during detection
        scene_manager = SceneManager(stats_manager)  # Main scene detection manager
        content_detector = ContentDetector(threshold=threshold)  # Detector that finds content changes
        scene_manager.add_detector(content_detector)  # Add the detector to the manager
        
        # Open the video file using PySceneDetect
        video_manager = VideoManager([video_path])
        scene_manager.detect_scenes(video_manager)  # Run the scene detection
        
        # Get the list of detected scenes
        scene_list = scene_manager.get_scene_list()
        
        # Process the detected scenes with additional filtering and classification
        cut_points = self._process_scenes_with_cursor_masking(
            scene_list, video_path, ignore_cursor, min_segment_duration
        )
        
        return cut_points
    
    def _process_scenes_with_cursor_masking(self, scene_list: List, video_path: str, 
                                          ignore_cursor: bool, min_segment_duration: float) -> List[CutPoint]:
        """Process detected scenes with cursor masking and change classification"""
        
        cut_points = []
        cap = cv2.VideoCapture(video_path)  # Open video for frame analysis
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Process each detected scene
        for i, scene in enumerate(scene_list):
            start_frame = scene[0].get_frames()  # Frame number where scene starts
            start_time = scene[0].get_seconds()  # Time in seconds where scene starts
            
            # Skip scenes that are too short (to avoid very short segments)
            if i > 0:  # Skip first scene (start of video)
                duration = start_time - cut_points[-1].timestamp if cut_points else start_time
                if duration < min_segment_duration:
                    continue
            
            # Get the frame at the scene start for analysis
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # Apply cursor masking if enabled (to ignore mouse cursor movements)
            if ignore_cursor:
                frame = self._mask_cursor_region(frame)
            
            # Classify what type of change occurred at this point
            change_type, confidence = self._classify_change(frame, start_frame, fps)
            
            # Create a cut point object with all the information
            cut_point = CutPoint(
                frame_number=start_frame,
                timestamp=start_time,
                confidence=confidence,
                change_type=change_type,
                description=f"Scene {i+1} detected at {start_time:.2f}s",
                thumbnail=None  # Could generate thumbnail here in the future
            )
            
            cut_points.append(cut_point)
        
        cap.release()  # Release video capture
        return cut_points
    
    def _mask_cursor_region(self, frame: np.ndarray) -> np.ndarray:
        """Mask out cursor regions to ignore mouse movements during analysis"""
        height, width = frame.shape[:2]  # Get frame dimensions
        masked_frame = frame.copy()  # Create a copy to modify
        
        # Technique 1: Create circular masks at detected cursor positions
        cursor_positions = self._detect_cursor_positions(frame)
        for pos in cursor_positions:
            x, y = pos
            radius = settings.cursor_mask_size
            # Draw a gray circle to mask out the cursor area
            cv2.circle(masked_frame, (x, y), radius, (128, 128, 128), -1)
        
        # Technique 2: Use connected component analysis for cursor-like objects
        if len(cursor_positions) > 0:
            # Create a mask for cursor regions
            mask = np.zeros((height, width), dtype=np.uint8)
            for pos in cursor_positions:
                x, y = pos
                cv2.circle(mask, (x, y), settings.cursor_mask_size, 255, -1)
            
            # Apply the mask to hide cursor regions
            masked_frame = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mask))
            masked_frame += cv2.bitwise_and(np.full_like(frame, 128), frame, mask=mask)
        
        # Technique 3: Mask edges to ignore cursor movements near screen edges
        edge_width = settings.edge_mask_width
        if edge_width > 0:
            # Create edge mask
            edge_mask = np.ones((height, width), dtype=np.uint8) * 255
            edge_mask[:edge_width, :] = 0  # Top edge
            edge_mask[-edge_width:, :] = 0  # Bottom edge
            edge_mask[:, :edge_width] = 0  # Left edge
            edge_mask[:, -edge_width:] = 0  # Right edge
            
            # Apply edge mask
            masked_frame = cv2.bitwise_and(masked_frame, masked_frame, mask=edge_mask)
        
        return masked_frame
    
    def _detect_cursor_positions(self, frame: np.ndarray) -> List[Tuple[int, int]]:
        """Detect potential cursor positions in the frame using computer vision"""
        positions = []
        
        # Convert frame to grayscale for easier processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Find bright spots (potential cursor) using thresholding
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours (outlines) of bright objects
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze each contour to see if it could be a cursor
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > settings.min_cursor_component_area:  # Only consider large enough objects
                # Calculate the center point of the contour
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    positions.append((cx, cy))
        
        return positions
    
    def _classify_change(self, frame: np.ndarray, frame_number: int, fps: float) -> Tuple[str, float]:
        """Classify the type of change detected based on spatial analysis"""
        
        # Analyze the spatial distribution of changes in the frame
        height, width = frame.shape[:2]
        
        # Divide frame into a 3x3 grid for analysis
        grid_size = 3
        cell_height = height // grid_size
        cell_width = width // grid_size
        
        # Calculate variance (how much the image changes) in each grid cell
        variances = []
        for i in range(grid_size):
            for j in range(grid_size):
                y1 = i * cell_height
                y2 = (i + 1) * cell_height
                x1 = j * cell_width
                x2 = (j + 1) * cell_width
                
                cell = frame[y1:y2, x1:x2]
                if cell.size > 0:
                    gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
                    variance = np.var(gray_cell)  # Calculate variance (measure of change)
                    variances.append(variance)
        
        if not variances:
            return "unknown", 0.5
        
        # Calculate statistical measures of the changes
        max_variance = max(variances)  # Maximum change in any area
        avg_variance = np.mean(variances)  # Average change across the frame
        variance_std = np.std(variances)  # How spread out the changes are
        
        # Classify the change based on the spatial distribution patterns
        if max_variance < 1000:
            return "button_click", 0.7  # Small, localized change
        elif max_variance < 5000 and variance_std < 1000:
            return "dialog_open", 0.8  # Medium change, well-distributed
        elif max_variance > 10000:
            return "ui_update", 0.9  # Large change across the frame
        elif variance_std > 2000:
            return "form_input", 0.6  # Spread out changes
        else:
            return "general_change", 0.5  # Default classification
    
    def process_video(self, session_id: str, cut_points: List[CutPoint]) -> str:
        """Process video into segments based on detected cut points"""
        # Get the session for this video
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Create download directory for processed files
        download_dir = Path("..") / "download"
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # Process the video into segments
        video_path = session.video_path
        segments = self._create_segments(video_path, cut_points, download_dir)
        
        # Create a log file with processing information
        log_path = download_dir / "processing_log.json"
        self._create_log_file(session, cut_points, segments, log_path)
        
        # Create output folder information
        output_path = self._create_output_folder(download_dir, session_id)
        
        # Update session status
        session.status = "processed"
        return str(output_path)
    
    def _create_segments(self, video_path: str, cut_points: List[CutPoint], 
                         output_dir: Path) -> List[dict]:
        """Create video segments using FFmpeg command-line tool"""
        segments = []
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        # Check if FFmpeg is available on the system
        import subprocess
        import shutil
        
        # Try to find FFmpeg in the system PATH first
        ffmpeg_path = shutil.which("ffmpeg")
        
        # If not found in PATH, try a known installation location
        if not ffmpeg_path:
            known_ffmpeg_path = Path("C:/ffmpeg/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe")
            if known_ffmpeg_path.exists():
                ffmpeg_path = str(known_ffmpeg_path)
                print(f"✅ Found FFmpeg at: {ffmpeg_path}")
            else:
                print("⚠️ FFmpeg not found. Creating log file only without video segments.")
                # Create a note file explaining that FFmpeg is needed
                segments.append({
                    "filename": "ffmpeg_not_available.txt",
                    "start_time": 0.0,
                    "end_time": 0.0,
                    "duration": 0.0,
                    "path": str(output_dir / "ffmpeg_not_available.txt"),
                    "note": "FFmpeg not installed. Install FFmpeg to create video segments."
                })
                
                # Create a helpful note file
                with open(output_dir / "ffmpeg_not_available.txt", 'w') as f:
                    f.write("FFmpeg is not installed on this system.\n")
                    f.write("To create video segments, please install FFmpeg:\n")
                    f.write("1. Download from https://ffmpeg.org/download.html\n")
                    f.write("2. Add to system PATH\n")
                    f.write("3. Restart the application\n\n")
                    f.write("Cut points detected:\n")
                    for i, cp in enumerate(cut_points):
                        f.write(f"  Cut {i+1}: {cp.timestamp:.2f}s (Frame {cp.frame_number})\n")
                
                return segments
        
        # Add start and end points for complete video coverage
        all_points = [0.0] + [cp.timestamp for cp in cut_points]
        
        # Create a segment for each pair of cut points
        for i in range(len(all_points) - 1):
            start_time = all_points[i]
            end_time = all_points[i + 1]
            
            # Skip very short segments
            if end_time - start_time < 0.1:
                continue
            
            # Create filename for this segment
            segment_filename = f"segment_{i+1:03d}.mp4"
            segment_path = output_dir / segment_filename
            
            # Use FFmpeg to extract the video segment
            # FFmpeg is a powerful command-line tool for video processing
            cmd = [
                ffmpeg_path, "-i", video_path,  # Input video file
                "-ss", str(start_time),  # Start time
                "-t", str(end_time - start_time),  # Duration
                "-c", "copy",  # Copy without re-encoding (faster)
                "-avoid_negative_ts", "make_zero",  # Handle timing issues
                str(segment_path),  # Output file path
                "-y"  # Overwrite output file if it exists
            ]
            
            try:
                # Run the FFmpeg command
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Add segment information to our list
                segments.append({
                    "filename": segment_filename,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_time - start_time,
                    "path": str(segment_path)
                })
            except subprocess.CalledProcessError as e:
                print(f"Error creating segment {i+1}: {e}")
                # Add error information to segments
                segments.append({
                    "filename": f"segment_{i+1:03d}_error.txt",
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_time - start_time,
                    "path": str(output_dir / f"segment_{i+1:03d}_error.txt"),
                    "error": str(e)
                })
        
        return segments
    
    def _create_log_file(self, session: VideoSession, cut_points: List[CutPoint], 
                        segments: List[dict], log_path: Path):
        """Create a detailed log file with all processing information"""
        # Prepare log data with all relevant information
        log_data = {
            "session_id": session.session_id,
            "video_info": session.video_info.dict(),  # Video metadata
            "cut_points": [cp.dict() for cp in cut_points],  # All detected cut points
            "segments": segments,  # Information about created segments
            "processing_time": datetime.now().isoformat(),  # When processing was done
            "settings": {
                "cursor_masking": True,
                "min_segment_duration": 1.0
            }
        }
        
        # Write the log data to a JSON file
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def _create_output_folder(self, download_dir: Path, session_id: str) -> Path:
        """Create output folder and provide information about created files"""
        
        # Print information about the created files
        print(f"✅ Files exported to download folder: {download_dir}")
        print(f"✅ Download directory contains:")
        for file_path in download_dir.rglob("*"):
            if file_path.is_file():
                print(f"  - {file_path.name}")
        
        return download_dir 