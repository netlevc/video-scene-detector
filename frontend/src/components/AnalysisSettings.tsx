import React from 'react';
import { Settings, Play, Loader } from 'lucide-react';
import { AnalysisSettings as AnalysisSettingsType, CutPoint } from '../types';

interface AnalysisSettingsProps {
  settings: AnalysisSettingsType;
  onSettingsChange: (settings: AnalysisSettingsType) => void;
  onAnalyze: () => void;
  disabled: boolean;
  sessionId: string | null;
  onAnalysisComplete: (cutPoints: CutPoint[]) => void;
}

const AnalysisSettings: React.FC<AnalysisSettingsProps> = ({
  settings,
  onSettingsChange,
  onAnalyze,
  disabled,
  sessionId,
  onAnalysisComplete
}) => {
  const handleAnalyze = async () => {
    if (!sessionId) return;
    
    onAnalyze();
    
    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          sensitivity: settings.sensitivity,
          ignore_cursor: settings.ignoreCursor,
          min_segment_duration: settings.minSegmentDuration
        }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      onAnalysisComplete(data.cut_points);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Analysis failed. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Sensitivity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sensitivity: {settings.sensitivity.toFixed(1)}
          </label>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.1"
            value={settings.sensitivity}
            onChange={(e) => onSettingsChange({
              ...settings,
              sensitivity: parseFloat(e.target.value)
            })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            disabled={disabled}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Less Sensitive</span>
            <span>More Sensitive</span>
          </div>
        </div>

        {/* Ignore Cursor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ignore Cursor Movement
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={settings.ignoreCursor}
              onChange={(e) => onSettingsChange({
                ...settings,
                ignoreCursor: e.target.checked
              })}
              className="sr-only"
              disabled={disabled}
            />
            <div className={`
              relative inline-flex h-6 w-11 items-center rounded-full transition-colors
              ${settings.ignoreCursor ? 'bg-blue-600' : 'bg-gray-200'}
              ${disabled ? 'opacity-50' : ''}
            `}>
              <span className={`
                inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                ${settings.ignoreCursor ? 'translate-x-6' : 'translate-x-1'}
              `} />
            </div>
            <span className="ml-3 text-sm text-gray-700">
              {settings.ignoreCursor ? 'Enabled' : 'Disabled'}
            </span>
          </label>
        </div>

        {/* Min Segment Duration */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Min Segment Duration: {settings.minSegmentDuration}s
          </label>
          <input
            type="range"
            min="0.5"
            max="5.0"
            step="0.5"
            value={settings.minSegmentDuration}
            onChange={(e) => onSettingsChange({
              ...settings,
              minSegmentDuration: parseFloat(e.target.value)
            })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            disabled={disabled}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0.5s</span>
            <span>5.0s</span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="flex items-center space-x-2 text-gray-600">
          <Settings className="w-4 h-4" />
          <span className="text-sm">Analysis Settings</span>
        </div>
        
        <button
          onClick={handleAnalyze}
          disabled={disabled || !sessionId}
          className={`
            flex items-center space-x-2 px-6 py-2 rounded-lg font-medium transition-colors
            ${disabled || !sessionId 
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700'
            }
          `}
        >
          {disabled ? (
            <Loader className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          <span>{disabled ? 'Analyzing...' : 'Analyze Video'}</span>
        </button>
      </div>
    </div>
  );
};

export default AnalysisSettings; 