/**
 * Component 2: Interview API Client
 * Handles all HTTP communication with backend
 */

import axios from 'axios';

const API_BASE = 'http://localhost:8002/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  }
});

// ====================================================================
// Interview Endpoints
// ====================================================================

export const interviewAPI = {
  /**
   * Start a new interview session
   *
   * Response includes session metadata and assigned coding profile:
   * - coding_profile: full | sql | scripting | none
   */
  startInterview: async (candidateId, jobRole, requiredSkills, numQuestions = 10) => {
    const response = await api.post('/interview/start', {
      candidate_id: candidateId,
      job_role: jobRole,
      required_skills: requiredSkills,
      num_questions: numQuestions
    });
    return response.data;
  },

  /**
   * Submit interview answers
   */
  submitAnswers: async (interviewData) => {
    const response = await api.post('/interview/submit', interviewData);
    return response.data;
  },

  /**
   * Run candidate code against test cases (no scoring)
   */
  runCode: async (code_text, test_cases) => {
    const response = await api.post('/interview/code/run', { code_text, test_cases });
    return response.data;
  },

  /**
   * Get interview result
   */
  getResult: async (interviewId) => {
    const response = await api.get(`/interview/result/${interviewId}`);
    return response.data;
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/interview/session/${sessionId}`);
    return response.data;
  },

  /**
   * Get question bank for a job role
   */
  getQuestionBank: async (jobRole) => {
    const response = await api.get(`/interview/questions/${jobRole}`);
    return response.data;
  },

  /**
   * Get available jobs
   */
  getAvailableJobs: async () => {
    const response = await api.get('/interview/jobs');
    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async () => {
    const response = await api.get('/interview/health');
    return response.data;
  }
};

// ====================================================================
// Error Handling
// ====================================================================

export const handleAPIError = (error) => {
  if (error.response) {
    return error.response.data.message || 'An error occurred';
  } else if (error.request) {
    return 'No response from server';
  } else {
    return error.message;
  }
};

export default api;
