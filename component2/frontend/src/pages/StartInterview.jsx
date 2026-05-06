import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { interviewAPI, handleAPIError } from '../api';
import '../pages/StartInterview.css';

export default function StartInterview() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    candidateId: '',
    jobRole: '',
    numQuestions: 10
  });
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadJobs = async () => {
      try {
        const data = await interviewAPI.getAvailableJobs();
        setJobs(Object.keys(data.jobs || {}));
      } catch (err) {
        setError(handleAPIError(err));
      }
    };
    loadJobs();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.candidateId || !formData.jobRole) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      const session = await interviewAPI.startInterview(
        formData.candidateId,
        formData.jobRole,
        [],
        formData.numQuestions
      );
      
      // Navigate to interview with session data
      navigate(`/interview/${session.session_id}`, { state: { session } });
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <div className="start-interview">
        <h2>Start New Interview</h2>
        <p className="subtitle">Set up your interview parameters</p>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="form-card card">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="candidateId">Candidate ID *</label>
              <input
                type="text"
                id="candidateId"
                name="candidateId"
                placeholder="Enter your candidate ID (e.g., CAND-001)"
                value={formData.candidateId}
                onChange={handleChange}
                required
              />
              <small>Unique identifier for tracking your interviews</small>
            </div>

            <div className="form-group">
              <label htmlFor="jobRole">Job Role *</label>
              <select
                id="jobRole"
                name="jobRole"
                value={formData.jobRole}
                onChange={handleChange}
                required
              >
                <option value="">Select a job role</option>
                {jobs.map(job => (
                  <option key={job} value={job}>{job}</option>
                ))}
              </select>
              <small>Select the position you are interviewing for</small>
            </div>

            <div className="form-group">
              <label htmlFor="numQuestions">Number of Questions</label>
              <input
                type="number"
                id="numQuestions"
                name="numQuestions"
                min="5"
                max="20"
                value={formData.numQuestions}
                onChange={handleChange}
              />
              <small>Questions will include MCQ, Descriptive, and Coding problems</small>
            </div>

            <div className="form-info">
              <h4>Interview Structure</h4>
              <ul>
                <li>30% MCQ questions - Multiple choice with single answer</li>
                <li>40% Descriptive - Free-form answers evaluated by semantic similarity</li>
                <li>30% Coding - Programming problems with test case evaluation</li>
              </ul>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-large"
              disabled={loading}
            >
              {loading ? 'Starting Interview...' : 'Start Interview'}
            </button>
          </form>
        </div>

        <div className="info-section card">
          <h3>ℹ️ Interview Tips</h3>
          <ul>
            <li>Take your time to read questions carefully</li>
            <li>For MCQ, select the best possible answer</li>
            <li>For descriptive questions, provide detailed and accurate answers</li>
            <li>For coding problems, ensure your logic is correct and test cases pass</li>
            <li>Try to provide comprehensive answers within the time limit</li>
          </ul>
        </div>
      </div>
    </main>
  );
}
