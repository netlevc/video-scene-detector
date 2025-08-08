import React, { useState } from 'react';
import VideoUpload from './components/VideoUpload';
import AnalysisSettings from './components/AnalysisSettings';
import VideoTimeline from './components/VideoTimeline';
import ProcessingStatus from './components/ProcessingStatus';
import { VideoInfo, CutPoint } from './types';

function App() {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [cutPoints, setCutPoints] = useState<CutPoint[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisSettings, setAnalysisSettings] = useState({
    sensitivity: 0.8,
    ignoreCursor: true,
    minSegmentDuration: 1.0
  });

  const handleVideoUpload = (sessionId: string, info: VideoInfo) => {
    setCurrentSessionId(sessionId);
    setVideoInfo(info);
    setCutPoints([]);
  };

  const handleAnalysisComplete = (points: CutPoint[]) => {
    setCutPoints(points);
    setIsAnalyzing(false);
  };

  const handleProcessingComplete = () => {
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Video Scene Detector
          </h1>
          <p className="text-lg text-gray-600">
            Automatically cut screen recordings into segments based on UI changes
          </p>
        </header>

        <div className="max-w-6xl mx-auto space-y-8">
          {/* Video Upload Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Upload Video
            </h2>
            <VideoUpload 
              onUpload={handleVideoUpload}
              disabled={isAnalyzing || isProcessing}
            />
          </div>

          {/* Analysis Settings */}
          {videoInfo && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Analysis Settings
              </h2>
              <AnalysisSettings
                settings={analysisSettings}
                onSettingsChange={setAnalysisSettings}
                onAnalyze={() => setIsAnalyzing(true)}
                disabled={isAnalyzing || isProcessing}
                sessionId={currentSessionId}
                onAnalysisComplete={handleAnalysisComplete}
              />
            </div>
          )}

          {/* Video Timeline */}
          {videoInfo && cutPoints.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Detected Cut Points
              </h2>
              <VideoTimeline
                videoInfo={videoInfo}
                cutPoints={cutPoints}
                onCutPointsChange={setCutPoints}
                onProcess={() => setIsProcessing(true)}
                disabled={isProcessing}
                sessionId={currentSessionId}
                onProcessingComplete={handleProcessingComplete}
              />
            </div>
          )}

          {/* Processing Status */}
          {(isAnalyzing || isProcessing) && (
            <ProcessingStatus
              isAnalyzing={isAnalyzing}
              isProcessing={isProcessing}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App; 