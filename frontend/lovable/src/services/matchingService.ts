/**
 * Profile Matching Service
 * Handles API calls for resume parsing and job matching
 */

import { apiClient } from '@/lib/api';

export interface MatchResult {
  match_score: number;
  reasoning: string;
  strengths: string[];
  concerns: string[];
  recommendation: 'Apply' | 'Review' | 'Skip';
}

export interface ProfileMatchResponse {
  status: string;
  match_score: number;
  reasoning: string;
  strengths: string[];
  concerns: string[];
  recommendation: string;
  extracted_skills: string[];
  experience_count: number;
}

export interface BatchMatchResponse {
  status: string;
  total_jobs: number;
  matched_jobs: number;
  min_score: number;
  results: Array<{
    title: string;
    company: string;
    description: string;
    location?: string;
    match: MatchResult;
  }>;
}

export interface Job {
  id?: string;
  title: string;
  company: string;
  description: string;
  location?: string;
  url?: string;
}

/**
 * Match a single resume against a job description
 */
export const matchProfile = async (
  resumeFilePath: string,
  jobDescription: string,
  jobTitle: string = '',
  companyName: string = '',
  aiProvider: string = 'gemini',
  apiKey?: string
): Promise<ProfileMatchResponse> => {
  const formData = new FormData();
  formData.append('resume_file_path', resumeFilePath);
  formData.append('job_description', jobDescription);
  formData.append('job_title', jobTitle);
  formData.append('company_name', companyName);
  formData.append('ai_provider', aiProvider);
  if (apiKey) {
    formData.append('api_key', apiKey);
  }

  return await apiClient.postFormData<ProfileMatchResponse>(
    '/api/match-profile',
    formData
  );
};

/**
 * Match a resume against multiple jobs and get sorted results
 */
export const batchMatchJobs = async (
  resumeFilePath: string,
  jobs: Job[],
  minScore: number = 0,
  aiProvider: string = 'gemini',
  apiKey?: string
): Promise<BatchMatchResponse> => {
  const formData = new FormData();
  formData.append('resume_file_path', resumeFilePath);
  formData.append('jobs', JSON.stringify(jobs));
  formData.append('min_score', minScore.toString());
  formData.append('ai_provider', aiProvider);
  if (apiKey) {
    formData.append('api_key', apiKey);
  }

  return await apiClient.postFormData<BatchMatchResponse>(
    '/api/batch-match',
    formData
  );
};

/**
 * Get match score color based on score value
 */
export const getMatchScoreColor = (score: number): string => {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-yellow-600';
  if (score >= 40) return 'text-orange-600';
  return 'text-red-600';
};

/**
 * Get match score badge color
 */
export const getMatchScoreBadge = (score: number): string => {
  if (score >= 80) return 'bg-green-100 text-green-800 border-green-200';
  if (score >= 60) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  if (score >= 40) return 'bg-orange-100 text-orange-800 border-orange-200';
  return 'bg-red-100 text-red-800 border-red-200';
};

/**
 * Format match recommendation for display
 */
export const formatRecommendation = (recommendation: string): string => {
  const recommendations: Record<string, string> = {
    Apply: '✅ Recommended',
    Review: '⚠️ Review',
    Skip: '❌ Not Recommended'
  };
  return recommendations[recommendation] || recommendation;
};
