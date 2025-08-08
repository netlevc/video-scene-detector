import React from 'react';
import { Loader, CheckCircle, AlertCircle } from 'lucide-react';

interface ProcessingStatusProps {
  isAnalyzing: boolean;
  isProcessing: boolean;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ isAnalyzing, isProcessing }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <div className="flex flex-col items-center space-y-4">
          {isAnalyzing ? (
            <>
              <Loader className="w-12 h-12 text-blue-500 animate-spin" />
              <h3 className="text-xl font-semibold text-gray-900">Analyzing Video</h3>
              <p className="text-gray-600 text-center">
                Detecting scene changes and cut points...
              </p>
            </>
          ) : isProcessing ? (
            <>
              <Loader className="w-12 h-12 text-green-500 animate-spin" />
              <h3 className="text-xl font-semibold text-gray-900">Processing Video</h3>
              <p className="text-gray-600 text-center">
                Creating video segments and preparing download...
              </p>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default ProcessingStatus; 