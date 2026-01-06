/**
 * Resume Upload Page - Complete Integration
 */
import React from 'react';
import ResumeUpload from '@/components/ResumeUpload';

const ResumeUploadPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold gradient-text">
            Upload Your Resume
          </h1>
          <p className="text-muted-foreground text-lg">
            Let AI analyze your resume and match you with the perfect jobs
          </p>
        </div>

        {/* Upload Component */}
        <ResumeUpload />

        {/* Benefits Section */}
        <div className="grid md:grid-cols-3 gap-4 mt-8">
          <div className="glass p-6 rounded-lg space-y-2">
            <div className="text-3xl">🤖</div>
            <h3 className="font-semibold">AI-Powered Parsing</h3>
            <p className="text-sm text-muted-foreground">
              Advanced AI extracts skills, experience, and qualifications from your resume
            </p>
          </div>

          <div className="glass p-6 rounded-lg space-y-2">
            <div className="text-3xl">📊</div>
            <h3 className="font-semibold">Smart Matching</h3>
            <p className="text-sm text-muted-foreground">
              Get scored matches (0-100) for every job with detailed reasoning
            </p>
          </div>

          <div className="glass p-6 rounded-lg space-y-2">
            <div className="text-3xl">⚡</div>
            <h3 className="font-semibold">Auto-Apply</h3>
            <p className="text-sm text-muted-foreground">
              Automatically apply to high-scoring jobs with custom cover letters
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeUploadPage;
