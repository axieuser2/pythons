import React from 'react';
import { Loader2, FileText, Database, Brain, Zap } from 'lucide-react';

const ProcessingStatus: React.FC = () => {
  const steps = [
    { icon: FileText, label: 'Reading files', description: 'Extracting content from uploaded files' },
    { icon: Brain, label: 'Processing content', description: 'Creating intelligent chunks and extracting key information' },
    { icon: Zap, label: 'Generating embeddings', description: 'Converting text to vector embeddings using OpenAI' },
    { icon: Database, label: 'Storing in Supabase', description: 'Saving processed data to vector database' },
  ];

  return (
    <div className="glass-effect rounded-2xl p-8">
      <div className="flex items-center mb-6">
        <Loader2 className="w-6 h-6 text-white mr-3 animate-spin" />
        <h2 className="text-2xl font-semibold text-white">Processing Files</h2>
      </div>

      <div className="space-y-6">
        {steps.map((step, index) => (
          <div key={index} className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                <step.icon className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-white mb-1">
                {step.label}
              </h3>
              <p className="text-white/70">
                {step.description}
              </p>
            </div>
            <div className="flex-shrink-0">
              <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 p-4 bg-white/10 rounded-lg">
        <p className="text-white/80 text-center">
          This may take a few minutes depending on file size and content complexity...
        </p>
      </div>
    </div>
  );
};

export default ProcessingStatus;