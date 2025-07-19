import React from 'react';
import { CheckCircle, AlertCircle, FileText, Database, Brain } from 'lucide-react';

interface ProcessingResult {
  success: boolean;
  message: string;
  chunks_created?: number;
  files_processed?: number;
  error?: string;
}

interface ResultsDisplayProps {
  result: ProcessingResult;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  return (
    <div className={`glass-effect rounded-2xl p-8 ${
      result.success ? 'border-green-400/30' : 'border-red-400/30'
    }`}>
      <div className="flex items-center mb-6">
        {result.success ? (
          <CheckCircle className="w-6 h-6 text-green-400 mr-3" />
        ) : (
          <AlertCircle className="w-6 h-6 text-red-400 mr-3" />
        )}
        <h2 className="text-2xl font-semibold text-white">
          {result.success ? 'Processing Complete!' : 'Processing Failed'}
        </h2>
      </div>

      <div className="space-y-4">
        <p className="text-white/90 text-lg">
          {result.message}
        </p>

        {result.success && (
          <div className="grid md:grid-cols-3 gap-4 mt-6">
            <div className="bg-white/10 rounded-lg p-4 text-center">
              <FileText className="w-8 h-8 text-blue-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">
                {result.files_processed || 0}
              </div>
              <div className="text-white/70">Files Processed</div>
            </div>
            
            <div className="bg-white/10 rounded-lg p-4 text-center">
              <Brain className="w-8 h-8 text-purple-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">
                {result.chunks_created || 0}
              </div>
              <div className="text-white/70">Chunks Created</div>
            </div>
            
            <div className="bg-white/10 rounded-lg p-4 text-center">
              <Database className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">
                ✓
              </div>
              <div className="text-white/70">Stored in Supabase</div>
            </div>
          </div>
        )}

        {result.error && (
          <div className="mt-4 p-4 bg-red-500/20 border border-red-400/30 rounded-lg">
            <p className="text-red-200 font-medium">Error Details:</p>
            <p className="text-red-100 mt-1">{result.error}</p>
          </div>
        )}

        {result.success && (
          <div className="mt-6 p-4 bg-green-500/20 border border-green-400/30 rounded-lg">
            <p className="text-green-200 font-medium">Next Steps:</p>
            <ul className="text-green-100 mt-2 space-y-1">
              <li>• Your files have been processed and stored in the vector database</li>
              <li>• You can now use the enhanced query system to search your knowledge base</li>
              <li>• All content is available for AI-powered retrieval and generation</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsDisplay;