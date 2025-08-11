// This file contains TypeScript type definitions for the Video Scene Detector frontend
// These types define the structure of data that flows between the frontend and backend
// TypeScript uses these to ensure data consistency and provide better code completion

// Information about a video file (received from the backend)
export interface VideoInfo {
  filename: string;      // Name of the video file
  duration: number;      // Length of the video in seconds
  frame_rate: number;    // Frames per second (FPS)
  resolution: string;    // Video resolution (e.g., "1920x1080")
  total_frames: number;  // Total number of frames in the video
  file_size: number;     // Size of the file in bytes
}

// A detected cut point where a scene change occurs
export interface CutPoint {
  frame_number: number;  // Which frame number the cut point is at
  timestamp: number;     // Time in seconds when the cut point occurs
  confidence: number;    // How confident the system is (0.0 to 1.0)
  change_type: string;   // Type of change detected (e.g., "button_click", "dialog_open")
  description: string;   // Human-readable description of the change
  thumbnail?: string;    // Optional image showing the frame (not currently used)
}

// Settings for video analysis that the user can configure
export interface AnalysisSettings {
  sensitivity: number;           // How sensitive the detection should be (0.1 to 1.0)
  ignoreCursor: boolean;         // Whether to ignore mouse cursor movements
  minSegmentDuration: number;    // Minimum length of video segments in seconds
}

// Response from the server when a video is uploaded
export interface UploadResponse {
  session_id: string;  // Unique identifier for this video processing session
  filename: string;    // Name of the uploaded file
  file_size: number;   // Size of the uploaded file in bytes
}

// Response from the server when video analysis is completed
export interface AnalysisResponse {
  session_id: string;     // Session identifier
  video_info: VideoInfo;  // Information about the video
  cut_points: CutPoint[]; // Array of detected cut points
}

// Response from the server when video processing is completed
export interface ProcessingResponse {
  session_id: string;      // Session identifier
  zip_file_path: string;   // Path to the folder containing processed segments
  segments_count: number;  // Number of video segments that were created
}

// Response from the server with information about processed files
export interface DownloadResponse {
  session_id: string;      // Session identifier
  output_directory: string; // Path to the folder containing processed files
  files: Array<{           // Array of processed files
    name: string;          // Name of the file
    path: string;          // Full path to the file
    size: number;          // Size of the file in bytes
  }>;
  message: string;         // Human-readable message about the processing results
} 