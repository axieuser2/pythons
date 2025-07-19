import React, { useCallback, useState } from 'react';
import { Upload, X, FileText, File, Database, Table } from 'lucide-react';

interface FileUploaderProps {
  onFilesSelected: (files: File[]) => void;
  selectedFiles: File[];
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFilesSelected, selectedFiles }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    const validFiles = droppedFiles.filter(file => 
      file.type.includes('text') || 
      file.type.includes('pdf') || 
      file.type.includes('word') ||
      file.type.includes('document') ||
      file.type.includes('csv') ||
      file.name.endsWith('.txt') ||
      file.name.endsWith('.pdf') ||
      file.name.endsWith('.doc') ||
      file.name.endsWith('.docx') ||
      file.name.endsWith('.csv')
    );

    if (validFiles.length > 0) {
      onFilesSelected([...selectedFiles, ...validFiles]);
    }
  }, [selectedFiles, onFilesSelected]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      onFilesSelected([...selectedFiles, ...newFiles]);
    }
  }, [selectedFiles, onFilesSelected]);

  const removeFile = useCallback((index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    onFilesSelected(newFiles);
  }, [selectedFiles, onFilesSelected]);

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return <File className="w-5 h-5 text-red-400" />;
      case 'doc':
      case 'docx':
        return <FileText className="w-5 h-5 text-blue-400" />;
      case 'csv':
        return <Table className="w-5 h-5 text-green-400" />;
      case 'txt':
      default:
        return <FileText className="w-5 h-5 text-gray-400" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Drop Zone */}
      <div
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
          dragActive 
            ? 'border-white bg-white/10 scale-105' 
            : 'border-white/30 hover:border-white/50 hover:bg-white/5'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          accept=".txt,.pdf,.doc,.docx,.csv"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="space-y-4">
          <div className="flex justify-center">
            <div className={`p-4 rounded-full transition-all duration-300 ${
              dragActive ? 'bg-white/20 scale-110' : 'bg-white/10'
            }`}>
              <Upload className={`w-8 h-8 text-white transition-transform duration-300 ${
                dragActive ? 'scale-110' : ''
              }`} />
            </div>
          </div>
          
          <div>
            <p className="text-xl font-semibold text-white mb-2">
              Drop files here or click to browse
            </p>
            <p className="text-white/70">
              Supports TXT, PDF, Word documents, and CSV files
            </p>
          </div>
          
          <div className="flex justify-center space-x-4 text-sm text-white/60">
            <span className="flex items-center">
              <FileText className="w-4 h-4 mr-1" />
              TXT
            </span>
            <span className="flex items-center">
              <File className="w-4 h-4 mr-1" />
              PDF
            </span>
            <span className="flex items-center">
              <FileText className="w-4 h-4 mr-1" />
              DOC/DOCX
            </span>
            <span className="flex items-center">
              <Table className="w-4 h-4 mr-1" />
              CSV
            </span>
          </div>
        </div>
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">
            Selected Files ({selectedFiles.length})
          </h3>
          
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-white/10 rounded-lg backdrop-blur-sm"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  {getFileIcon(file.name)}
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium truncate">
                      {file.name}
                    </p>
                    <p className="text-white/60 text-sm">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 hover:bg-white/20 rounded-full transition-colors"
                >
                  <X className="w-4 h-4 text-white/70 hover:text-white" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploader;