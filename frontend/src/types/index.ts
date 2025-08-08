export interface VideoInfo {
  filename: string;
  duration: number;
  frame_rate: number;
  resolution: string;
  total_frames: number;
  file_size: number;
}

export interface CutPoint {
  frame_number: number;
  timestamp: number;
  confidence: number;
  change_type: string;
  description: string;
  thumbnail?: string;
}

export interface AnalysisSettings {
  sensitivity: number;
  ignoreCursor: boolean;
  minSegmentDuration: number;
}

export interface UploadResponse {
  session_id: string;
  filename: string;
  file_size: number;
}

export interface AnalysisResponse {
  session_id: string;
  video_info: VideoInfo;
  cut_points: CutPoint[];
}

export interface ProcessingResponse {
  session_id: string;
  zip_file_path: string;
  segments_count: number;
}

export interface DownloadResponse {
  session_id: string;
  output_directory: string;
  files: Array<{
    name: string;
    path: string;
    size: number;
  }>;
  message: string;
} 