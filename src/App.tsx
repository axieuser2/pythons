import React, { useState, useCallback } from 'react';
import { Upload, FileText, Database, CheckCircle, AlertCircle, Loader2, Brain, Zap } from 'lucide-react';
import FileUploader from './components/FileUploader';
import ProcessingStatus from './components/ProcessingStatus';
import ResultsDisplay from './components/ResultsDisplay';

interface ProcessingResult {
  success: boolean;
  message: string;
  chunks_created?: number;
  files_processed?: number;
  error?: string;
}

function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ProcessingResult | null>(null);

  const handleFilesSelected = useCallback((selectedFiles: File[]) => {
    setFiles(selectedFiles);
    setResult(null);
  }, []);

  const handleProcess = async () => {
    if (files.length === 0) return;

    setIsProcessing(true);
    setResult(null);

    try {
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append(`file_${index}`, file);
      });

      const response = await fetch('/api/process-files', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        success: false,
        message: 'Failed to process files',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClear = () => {
    setFiles([]);
    setResult(null);
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="p-4 rounded-full glass-effect">
              <Brain className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            RAG File Processor
          </h1>
          <p className="text-xl text-white/80 max-w-2xl mx-auto">
            Upload your documents and automatically process them into a searchable knowledge base
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <div className="grid gap-8">
            {/* File Upload Section */}
            <div className="glass-effect rounded-2xl p-8">
              <div className="flex items-center mb-6">
                <Upload className="w-6 h-6 text-white mr-3" />
                <h2 className="text-2xl font-semibold text-white">Upload Files</h2>
              </div>
              
              <FileUploader 
                onFilesSelected={handleFilesSelected}
                selectedFiles={files}
              />

              {files.length > 0 && (
                <div className="mt-6 flex gap-4">
                  <button
                    onClick={handleProcess}
                    disabled={isProcessing}
                    className="flex items-center px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Zap className="w-5 h-5 mr-2" />
                        Process Files
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleClear}
                    disabled={isProcessing}
                    className="px-6 py-3 border border-white/30 text-white rounded-lg font-semibold hover:bg-white/10 transition-colors disabled:opacity-50"
                  >
                    Clear All
                  </button>
                </div>
              )}
            </div>

            {/* Processing Status */}
            {isProcessing && (
              <ProcessingStatus />
            )}

            {/* Results */}
            {result && (
              <ResultsDisplay result={result} />
            )}

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-6">
              <div className="glass-effect rounded-xl p-6 text-center">
                <FileText className="w-8 h-8 text-white mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Multiple Formats</h3>
                <p className="text-white/70">Support for TXT, PDF, Word, and CSV files</p>
              </div>
              
              <div className="glass-effect rounded-xl p-6 text-center">
                <Database className="w-8 h-8 text-white mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Vector Storage</h3>
                <p className="text-white/70">Automatic embedding and Supabase integration</p>
              </div>
              
              <div className="glass-effect rounded-xl p-6 text-center">
                <Brain className="w-8 h-8 text-white mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Smart Processing</h3>
                <p className="text-white/70">AI-powered chunking and content extraction</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;