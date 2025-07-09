import axios, { AxiosInstance, AxiosResponse } from 'axios';

// Create axios instance with base configuration
const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 90000, // Increased timeout to 90 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include JWT token
api.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers = config.headers || {};
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface ResumeAnalysis {
  ats_score: number;
  suggestions: string[];
  strengths: string[];
  keywords: string[];
  improvements: string[];
}

export interface JobMatch {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  description: string;
  matchScore: number;
  datePosted: string;
  jobType: string;
  source: string;
  url?: string;
}

export interface JobApplication {
  id: string;
  job_title: string;
  company: string;
  location: string;
  status: string;
  date_applied: string;
  match_score: number;
}

export interface AnalyticsData {
  total_applications: number;
  interview_rate: number;
  response_rate: number;
  avg_response_time: number;
  monthly_applications: Array<{
    month: string;
    applications: number;
    interviews: number;
    offers: number;
  }>;
  application_status: Array<{
    name: string;
    value: number;
  }>;
}

// API functions
export const apiService = {
  // Health check
  async healthCheck(): Promise<any> {
    const response = await api.get('/health');
    return response.data;
  },

  // Resume analysis
  async analyzeResume(file: File): Promise<ResumeAnalysis> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Job search
  async searchJobs(params: {
    query?: string;
    location?: string;
    jobType?: string;
    minSalary?: string;
    company?: string;
    maxResults?: number;
  }): Promise<JobMatch[]> {
    const response = await api.get('/api/match', { params });
    return response.data;
  },

  // Job applications
  async createApplication(applicationData: {
    job_title: string;
    company: string;
    location: string;
    job_description?: string;
    job_url?: string;
    source?: string;
    job_type?: string;
    match_score?: number;
  }): Promise<any> {
    const response = await api.post('/api/applications', applicationData);
    return response.data;
  },

  async getApplications(userId: string = 'demo'): Promise<JobApplication[]> {
    const response = await api.get(`/api/applications?user_id=${userId}`);
    return response.data;
  },

  async updateApplication(applicationId: string, updates: Partial<JobApplication>): Promise<any> {
    const response = await api.patch(`/api/applications/${applicationId}`, updates);
    return response.data;
  },

  async deleteApplication(applicationId: string): Promise<any> {
    const response = await api.delete(`/api/applications/${applicationId}`);
    return response.data;
  },

  // Analytics
  async getAnalytics(userId: string = 'demo'): Promise<AnalyticsData> {
    const response = await api.get(`/api/analytics?user_id=${userId}`);
    return response.data;
  },

  // User profile
  async getUserProfile(userId: string): Promise<any> {
    const response = await api.get(`/api/users/${userId}`);
    return response.data;
  },

  async updateUserProfile(userId: string, profileData: any): Promise<any> {
    const response = await api.patch(`/api/users/${userId}`, profileData);
    return response.data;
  },

  // Settings
  async getUserSettings(userId: string): Promise<any> {
    const response = await api.get(`/api/users/${userId}/settings`);
    return response.data;
  },

  async updateUserSettings(userId: string, settings: any): Promise<any> {
    const response = await api.patch(`/api/users/${userId}/settings`, settings);
    return response.data;
  },

  // Job recommendations
  async getJobRecommendations(userId: string): Promise<JobMatch[]> {
    const response = await api.get(`/api/recommendations?user_id=${userId}`);
    return response.data;
  },

  // Resume optimization
  async optimizeResume(resumeData: any, jobDescription: string): Promise<any> {
    const response = await api.post('/api/resume/optimize', {
      resume_data: resumeData,
      job_description: jobDescription,
    });
    return response.data;
  },

  // Interview preparation
  async getInterviewQuestions(jobTitle: string, company: string): Promise<any> {
    const response = await api.get('/api/interview/questions', {
      params: { job_title: jobTitle, company }
    });
    return response.data;
  },

  // Market analysis
  async getMarketAnalysis(jobTitle: string, location: string): Promise<any> {
    const response = await api.get('/api/market/analysis', {
      params: { job_title: jobTitle, location }
    });
    return response.data;
  },

  // Salary analysis
  async getSalaryAnalysis(jobTitle: string, location: string): Promise<any> {
    const response = await api.get('/api/salary/analysis', {
      params: { job_title: jobTitle, location }
    });
    return response.data;
  },

  // Save a job for a user
  async saveJob(job: any, userId: string = 'demo'): Promise<any> {
    const response = await api.post(`/api/saved-jobs?user_id=${userId}`, job);
    return response.data;
  },

  // Fetch saved jobs for a user
  async getSavedJobs(userId: string = 'demo'): Promise<any[]> {
    const response = await api.get(`/api/saved-jobs?user_id=${userId}`);
    return response.data;
  },
};

// Export the axios instance for direct use if needed
export default api; 