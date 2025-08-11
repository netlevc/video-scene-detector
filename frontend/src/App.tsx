// This is the main React component for the Video Scene Detector frontend
// It manages the overall application state and coordinates between different components

import React, { useState } from 'react';  // React library for building user interfaces
import VideoUpload from './components/VideoUpload';  // Component for handling video file uploads
import AnalysisSettings from './components/AnalysisSettings';  // Component for analysis configuration
import VideoTimeline from './components/VideoTimeline';  // Component for displaying cut points
import ProcessingStatus from './components/ProcessingStatus';  // Component for showing processing status
import { VideoInfo, CutPoint } from './types';  // Type definitions for video data

function App() {
  // State variables to track the current state of the application
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);  // Unique ID for the current video session
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);  // Information about the uploaded video
  const [cutPoints, setCutPoints] = useState<CutPoint[]>([]);  // Array of detected cut points in the video
  const [isAnalyzing, setIsAnalyzing] = useState(false);  // Whether video analysis is currently running
  const [isProcessing, setIsProcessing] = useState(false);  // Whether video processing is currently running
  
  // Settings for video analysis (sensitivity, cursor handling, etc.)
  const [analysisSettings, setAnalysisSettings] = useState({
    sensitivity: 0.8,  // How sensitive the scene detection should be (0.1 to 1.0)
    ignoreCursor: true,  // Whether to ignore mouse cursor movements
    minSegmentDuration: 1.0  // Minimum length of video segments in seconds
  });

  // Function called when a video is successfully uploaded
  const handleVideoUpload = (sessionId: string, info: VideoInfo) => {
    setCurrentSessionId(sessionId);  // Store the session ID
    setVideoInfo(info);  // Store video information
    setCutPoints([]);  // Clear any previous cut points
  };

  // Function called when video analysis is completed
  const handleAnalysisComplete = (points: CutPoint[]) => {
    setCutPoints(points);  // Store the detected cut points
    setIsAnalyzing(false);  // Mark analysis as complete
  };

  // Function called when video processing is completed
  const handleProcessingComplete = () => {
    setIsProcessing(false);  // Mark processing as complete
  };

  return (
    // Main application container with styling
    <div className="min-h-screen bg-gray-50">  {/* Full screen height with light gray background */}
      <div className="container mx-auto px-4 py-8">  {/* Centered container with padding */}
        
        {/* Application header with title and description */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Video Scene Detector
          </h1>
          <p className="text-lg text-gray-600">
            Automatically cut screen recordings into segments based on UI changes
          </p>
        </header>

        {/* Main content area with spacing between sections */}
        <div className="max-w-6xl mx-auto space-y-8">
          
          {/* Video Upload Section - Always visible */}
          <div className="bg-white rounded-lg shadow-md p-6">  {/* White card with shadow */}
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Upload Video
            </h2>
            <VideoUpload 
              onUpload={handleVideoUpload}  // Function to call when video is uploaded
              disabled={isAnalyzing || isProcessing}  // Disable upload during processing
            />
          </div>

          {/* Analysis Settings Section - Only shown after video is uploaded */}
          {videoInfo && (  // Only render if we have video information
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Analysis Settings
              </h2>
              <AnalysisSettings
                settings={analysisSettings}  // Current analysis settings
                onSettingsChange={setAnalysisSettings}  // Function to update settings
                onAnalyze={() => setIsAnalyzing(true)}  // Function to start analysis
                disabled={isAnalyzing || isProcessing}  // Disable during processing
                sessionId={currentSessionId}  // Session ID for API calls
                onAnalysisComplete={handleAnalysisComplete}  // Function called when analysis completes
              />
            </div>
          )}

          {/* Video Timeline Section - Only shown after analysis is complete */}
          {videoInfo && cutPoints.length > 0 && (  // Only render if we have video info and cut points
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Detected Cut Points
              </h2>
              <VideoTimeline
                videoInfo={videoInfo}  // Video information to display
                cutPoints={cutPoints}  // Detected cut points to show
                onCutPointsChange={setCutPoints}  // Function to update cut points
                onProcess={() => setIsProcessing(true)}  // Function to start processing
                disabled={isProcessing}  // Disable during processing
                sessionId={currentSessionId}  // Session ID for API calls
                onProcessingComplete={handleProcessingComplete}  // Function called when processing completes
              />
            </div>
          )}

          {/* Processing Status Section - Only shown during analysis or processing */}
          {(isAnalyzing || isProcessing) && (  // Only render during processing
            <ProcessingStatus
              isAnalyzing={isAnalyzing}  // Whether analysis is running
              isProcessing={isProcessing}  // Whether processing is running
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;  // Export the component so it can be used elsewhere 