import React, { useState } from 'react';
import { Scissors, Download, Clock, FileVideo } from 'lucide-react';
import { VideoInfo, CutPoint, ProcessingResponse, DownloadResponse } from '../types';

interface VideoTimelineProps {
  videoInfo: VideoInfo;
  cutPoints: CutPoint[];
  onCutPointsChange: (cutPoints: CutPoint[]) => void;
  onProcess: () => void;
  disabled: boolean;
  sessionId: string | null;
  onProcessingComplete: () => void;
}

const VideoTimeline: React.FC<VideoTimelineProps> = ({
  videoInfo,
  cutPoints,
  onCutPointsChange,
  onProcess,
  disabled,
  sessionId,
  onProcessingComplete
}) => {
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [downloadInfo, setDownloadInfo] = useState<DownloadResponse | null>(null);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleProcess = async () => {
    if (!sessionId) return;
    
    onProcess();
    setProcessingStatus('Processing video segments...');
    
    try {
      // Process the video
      const processResponse = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          cut_points: cutPoints
        }),
      });

      if (!processResponse.ok) {
        throw new Error('Processing failed');
      }

      const processData: ProcessingResponse = await processResponse.json();
      
      // Get download information
      const downloadResponse = await fetch(`http://localhost:8000/api/download/${sessionId}`);
      if (downloadResponse.ok) {
        const downloadData: DownloadResponse = await downloadResponse.json();
        setDownloadInfo(downloadData);
      }

      setProcessingStatus('Processing complete!');
      onProcessingComplete();
    } catch (error) {
      console.error('Processing error:', error);
      setProcessingStatus('Processing failed. Please try again.');
      onProcessingComplete();
    }
  };

  return (
    <div className="space-y-6">
      {/* Video Info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-3">
          <FileVideo className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">{videoInfo.filename}</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Duration:</span>
            <span className="ml-2 font-medium">{formatTime(videoInfo.duration)}</span>
          </div>
          <div>
            <span className="text-gray-500">Resolution:</span>
            <span className="ml-2 font-medium">{videoInfo.resolution}</span>
          </div>
          <div>
            <span className="text-gray-500">Frame Rate:</span>
            <span className="ml-2 font-medium">{videoInfo.frame_rate.toFixed(1)} fps</span>
          </div>
          <div>
            <span className="text-gray-500">File Size:</span>
            <span className="ml-2 font-medium">{(videoInfo.file_size / (1024 * 1024)).toFixed(1)} MB</span>
          </div>
        </div>
      </div>

      {/* Cut Points */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Detected Cut Points ({cutPoints.length})
          </h3>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>Total Duration: {formatTime(videoInfo.duration)}</span>
          </div>
        </div>

        <div className="space-y-2 max-h-64 overflow-y-auto">
          {cutPoints.map((point, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-600">{index + 1}</span>
                </div>
                <div>
                  <div className="font-medium text-gray-900">
                    {formatTime(point.timestamp)}
                  </div>
                  <div className="text-sm text-gray-500">
                    Frame {point.frame_number} • {point.change_type} • {Math.round(point.confidence * 100)}% confidence
                  </div>
                </div>
              </div>
              <div className="text-sm text-gray-500">
                {point.description}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Processing Section */}
      <div className="border-t border-gray-200 pt-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-gray-600">
            <Scissors className="w-4 h-4" />
            <span className="text-sm">Video Processing</span>
          </div>
          
          <button
            onClick={handleProcess}
            disabled={disabled || cutPoints.length === 0}
            className={`
              flex items-center space-x-2 px-6 py-2 rounded-lg font-medium transition-colors
              ${disabled || cutPoints.length === 0
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
              }
            `}
          >
            <Download className="w-4 h-4" />
            <span>{disabled ? 'Processing...' : 'Process & Download'}</span>
          </button>
        </div>

        {processingStatus && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">{processingStatus}</p>
          </div>
        )}

        {downloadInfo && (
          <div className="mt-4 p-4 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Download className="w-5 h-5 text-green-600" />
              <h4 className="font-medium text-green-800">Files Ready!</h4>
            </div>
            <p className="text-sm text-green-700 mb-3">
              Location: {downloadInfo.output_directory}
            </p>
            <div className="text-sm text-green-700">
              <p className="font-medium mb-1">Files created:</p>
              <ul className="space-y-1">
                {downloadInfo.files.map((file, index) => (
                  <li key={index} className="flex justify-between">
                    <span>{file.name}</span>
                    <span>{(file.size / 1024).toFixed(1)} KB</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoTimeline; 