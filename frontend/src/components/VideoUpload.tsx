import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileVideo, AlertCircle } from 'lucide-react';
import { VideoInfo, UploadResponse } from '../types';

interface VideoUploadProps {
  onUpload: (sessionId: string, videoInfo: VideoInfo) => void;
  disabled?: boolean;
}

const VideoUpload: React.FC<VideoUploadProps> = ({ onUpload, disabled = false }) => {
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data: UploadResponse = await response.json();
      
      // Get video info from the response
      const videoInfoResponse = await fetch(`http://localhost:8000/api/preview/${data.session_id}`);
      if (videoInfoResponse.ok) {
        const previewData = await videoInfoResponse.json();
        onUpload(data.session_id, previewData.video_info);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'video/mp4': ['.mp4'],
      'video/avi': ['.avi'],
      'video/mov': ['.mov'],
      'video/wmv': ['.wmv']
    },
    maxFiles: 1,
    disabled
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive && !isDragReject ? 'border-blue-500 bg-blue-50' : ''}
          ${isDragReject ? 'border-red-500 bg-red-50' : 'border-gray-300 hover:border-gray-400'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          {isDragActive ? (
            <Upload className="w-12 h-12 text-blue-500" />
          ) : (
            <FileVideo className="w-12 h-12 text-gray-400" />
          )}
          
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-900">
              {isDragActive 
                ? 'Drop your video file here' 
                : 'Drag & drop a video file here'
              }
            </p>
            <p className="text-sm text-gray-500">
              or click to browse files
            </p>
            <p className="text-xs text-gray-400">
              Supported formats: MP4, AVI, MOV, WMV
            </p>
          </div>

          {isDragReject && (
            <div className="flex items-center space-x-2 text-red-500">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">Invalid file type</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoUpload; 