import os
import cv2
import numpy as np
from typing import List, Optional, Tuple
from datetime import datetime
import uuid
import json
from pathlib import Path

# PySceneDetect imports
from scenedetect import SceneManager, ContentDetector
from scenedetect.stats_manager import StatsManager
from scenedetect.video_manager import VideoManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.scene_manager import save_images

from ..models.video import VideoInfo, CutPoint, ChangeType, VideoSession
from ..core.config import settings


class VideoProcessor:
    def __init__(self):
        self.sessions: dict[str, VideoSession] = {}
    
    def create_session(self, video_path: str) -> str:
        """Create a new video processing session"""
        session_id = str(uuid.uuid4())
        
        # Get video info
        video_info = self._get_video_info(video_path)
        
        # Create session
        session = VideoSession(
            session_id=session_id,
            video_path=video_path,
            video_info=video_info,
            cut_points=[],
            created_at=datetime.now(),
            status="uploaded"
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[VideoSession]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def _get_video_info(self, video_path: str) -> VideoInfo:
        """Extract video information"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        file_size = os.path.getsize(video_path)
        
        cap.release()
        
        return VideoInfo(
            filename=os.path.basename(video_path),
            duration=duration,
            frame_rate=fps,
            resolution=f"{width}x{height}",
            total_frames=frame_count,
            file_size=file_size
        )
    
    def detect_changes(self, session_id: str, sensitivity: float = 0.8, 
                      ignore_cursor: bool = True, min_segment_duration: float = 1.0) -> List[CutPoint]:
        """Detect scene changes using PySceneDetect"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        video_path = session.video_path
        
        # Use PySceneDetect for scene detection
        cut_points = self._detect_scenes_pyscenedetect(video_path, sensitivity, ignore_cursor, min_segment_duration)
        
        # Update session
        session.cut_points = cut_points
        session.status = "analyzed"
        
        return cut_points
    
    def _detect_scenes_pyscenedetect(self, video_path: str, sensitivity: float, 
                                   ignore_cursor: bool, min_segment_duration: float) -> List[CutPoint]:
        """Detect scenes using PySceneDetect ContentDetector"""
        
        # Calculate threshold based on sensitivity
        threshold_range = settings.content_detector_threshold_max - settings.content_detector_threshold_min
        threshold = int(settings.content_detector_threshold_max - (sensitivity * threshold_range))
        threshold = max(settings.content_detector_threshold_min, min(settings.content_detector_threshold_max, threshold))
        
        # Initialize PySceneDetect with the new API
        stats_manager = StatsManager()
        scene_manager = SceneManager(stats_manager)
        content_detector = ContentDetector(threshold=threshold)
        scene_manager.add_detector(content_detector)
        
        # Open video using the newer PySceneDetect API
        video_manager = VideoManager([video_path])
        scene_manager.detect_scenes(video_manager)
        
        # Get scene list
        scene_list = scene_manager.get_scene_list()
        
        # Process scenes with cursor masking and classification
        cut_points = self._process_scenes_with_cursor_masking(
            scene_list, video_path, ignore_cursor, min_segment_duration
        )
        
        return cut_points
    
    def _process_scenes_with_cursor_masking(self, scene_list: List, video_path: str, 
                                          ignore_cursor: bool, min_segment_duration: float) -> List[CutPoint]:
        """Process detected scenes with enhanced cursor masking and classification"""
        
        cut_points = []
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        for i, scene in enumerate(scene_list):
            start_frame = scene[0].get_frames()
            start_time = scene[0].get_seconds()
            
            # Skip if scene is too short
            if i > 0:  # Skip first scene (start of video)
                duration = start_time - cut_points[-1].timestamp if cut_points else start_time
                if duration < min_segment_duration:
                    continue
            
            # Get frame for analysis
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # Apply cursor masking if enabled
            if ignore_cursor:
                frame = self._mask_cursor_region(frame)
            
            # Classify the change
            change_type, confidence = self._classify_change(frame, start_frame, fps)
            
            # Create cut point
            cut_point = CutPoint(
                frame_number=start_frame,
                timestamp=start_time,
                confidence=confidence,
                change_type=change_type,
                description=f"Scene {i+1} detected at {start_time:.2f}s",
                thumbnail=None  # Could generate thumbnail here
            )
            
            cut_points.append(cut_point)
        
        cap.release()
        return cut_points
    
    def _mask_cursor_region(self, frame: np.ndarray) -> np.ndarray:
        """Enhanced cursor masking with multiple techniques"""
        height, width = frame.shape[:2]
        masked_frame = frame.copy()
        
        # Technique 1: Circular masks at cursor positions
        cursor_positions = self._detect_cursor_positions(frame)
        for pos in cursor_positions:
            x, y = pos
            radius = settings.cursor_mask_size
            cv2.circle(masked_frame, (x, y), radius, (128, 128, 128), -1)
        
        # Technique 2: Connected component analysis for cursor-like objects
        if len(cursor_positions) > 0:
            # Create mask for cursor regions
            mask = np.zeros((height, width), dtype=np.uint8)
            for pos in cursor_positions:
                x, y = pos
                cv2.circle(mask, (x, y), settings.cursor_mask_size, 255, -1)
            
            # Apply mask
            masked_frame = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mask))
            masked_frame += cv2.bitwise_and(np.full_like(frame, 128), frame, mask=mask)
        
        # Technique 3: Edge masking to ignore cursor edges
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
        """Detect potential cursor positions in the frame"""
        positions = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Find bright spots (potential cursor)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > settings.min_cursor_component_area:
                # Get centroid
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    positions.append((cx, cy))
        
        return positions
    
    def _classify_change(self, frame: np.ndarray, frame_number: int, fps: float) -> Tuple[str, float]:
        """Classify the type of change detected"""
        
        # Analyze spatial distribution of changes
        height, width = frame.shape[:2]
        
        # Divide frame into 3x3 grid
        grid_size = 3
        cell_height = height // grid_size
        cell_width = width // grid_size
        
        # Calculate variance in each cell
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
                    variance = np.var(gray_cell)
                    variances.append(variance)
        
        if not variances:
            return "unknown", 0.5
        
        # Calculate metrics
        max_variance = max(variances)
        avg_variance = np.mean(variances)
        variance_std = np.std(variances)
        
        # Classify based on spatial distribution
        if max_variance < 1000:
            return "button_click", 0.7
        elif max_variance < 5000 and variance_std < 1000:
            return "dialog_open", 0.8
        elif max_variance > 10000:
            return "ui_update", 0.9
        elif variance_std > 2000:
            return "form_input", 0.6
        else:
            return "general_change", 0.5
    
    def process_video(self, session_id: str, cut_points: List[CutPoint]) -> str:
        """Process video into segments"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Create download directory
        download_dir = Path("..") / "download"
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # Process video segments
        video_path = session.video_path
        segments = self._create_segments(video_path, cut_points, download_dir)
        
        # Create log file
        log_path = download_dir / "processing_log.json"
        self._create_log_file(session, cut_points, segments, log_path)
        
        # Create output folder info
        output_path = self._create_output_folder(download_dir, session_id)
        
        session.status = "processed"
        return str(output_path)
    
    def _create_segments(self, video_path: str, cut_points: List[CutPoint], 
                         output_dir: Path) -> List[dict]:
        """Create video segments using FFmpeg"""
        segments = []
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        # Check if FFmpeg is available
        import subprocess
        import shutil
        
        # Try to find FFmpeg in PATH first
        ffmpeg_path = shutil.which("ffmpeg")
        
        # If not found in PATH, try the known installation location
        if not ffmpeg_path:
            known_ffmpeg_path = Path("C:/ffmpeg/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe")
            if known_ffmpeg_path.exists():
                ffmpeg_path = str(known_ffmpeg_path)
                print(f"✅ Found FFmpeg at: {ffmpeg_path}")
            else:
                print("⚠️ FFmpeg not found. Creating log file only without video segments.")
                # Create a simple log entry indicating FFmpeg is not available
                segments.append({
                    "filename": "ffmpeg_not_available.txt",
                    "start_time": 0.0,
                    "end_time": 0.0,
                    "duration": 0.0,
                    "path": str(output_dir / "ffmpeg_not_available.txt"),
                    "note": "FFmpeg not installed. Install FFmpeg to create video segments."
                })
                
                # Create a note file
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
        
        # Add start and end points
        all_points = [0.0] + [cp.timestamp for cp in cut_points]
        
        for i in range(len(all_points) - 1):
            start_time = all_points[i]
            end_time = all_points[i + 1]
            
            if end_time - start_time < 0.1:  # Skip very short segments
                continue
            
            segment_filename = f"segment_{i+1:03d}.mp4"
            segment_path = output_dir / segment_filename
            
            # Use FFmpeg to extract segment
            cmd = [
                ffmpeg_path, "-i", video_path,
                "-ss", str(start_time),
                "-t", str(end_time - start_time),
                "-c", "copy",  # Copy without re-encoding
                "-avoid_negative_ts", "make_zero",
                str(segment_path),
                "-y"  # Overwrite output file
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                
                segments.append({
                    "filename": segment_filename,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_time - start_time,
                    "path": str(segment_path)
                })
            except subprocess.CalledProcessError as e:
                print(f"Error creating segment {i+1}: {e}")
                # Add error info to segments
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
        """Create processing log file"""
        log_data = {
            "session_id": session.session_id,
            "video_info": session.video_info.dict(),
            "cut_points": [cp.dict() for cp in cut_points],
            "segments": segments,
            "processing_time": datetime.now().isoformat(),
            "settings": {
                "cursor_masking": True,
                "min_segment_duration": 1.0
            }
        }
        
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def _create_output_folder(self, download_dir: Path, session_id: str) -> Path:
        """Create output folder with all processed content"""
        
        # Just return the download directory path
        print(f"✅ Files exported to download folder: {download_dir}")
        print(f"✅ Download directory contains:")
        for file_path in download_dir.rglob("*"):
            if file_path.is_file():
                print(f"  - {file_path.name}")
        
        return download_dir 