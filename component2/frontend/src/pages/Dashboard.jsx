import React, { useState, useEffect } from 'react';
import { interviewAPI } from '../api';
import '../pages/Dashboard.css';

export default function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const jobsData = await interviewAPI.getAvailableJobs();
        setJobs(jobsData.jobs || {});

        // Mock stats
        setStats({
          totalInterviews: 42,
          averageScore: 72.5,
          completionRate: 85
        });
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) return <main><div className="loader"></div></main>;
  if (error) return <main><div className="alert alert-error">{error}</div></main>;

  return (
    <main>
      <div className="dashboard">
        <h2>Interview System Dashboard</h2>
        <p className="subtitle">Component 2: AI Interview Generation & Evaluation</p>

        {/* Stats Section */}
        {stats && (
          <div className="stats-grid">
            <div className="stat-card">
              <h3>{stats.totalInterviews}</h3>
              <p>Total Interviews</p>
            </div>
            <div className="stat-card">
              <h3>{stats.averageScore.toFixed(1)}</h3>
              <p>Average Score</p>
            </div>
            <div className="stat-card">
              <h3>{stats.completionRate}%</h3>
              <p>Completion Rate</p>
            </div>
          </div>
        )}

        {/* Jobs Section */}
        <div className="card">
          <h3>Available Job Roles</h3>
          <div className="jobs-grid">
            {Object.entries(jobs).map(([role, skills]) => (
              <div key={role} className="job-card">
                <h4>{role}</h4>
                <p className="skills-label">Required Skills:</p>
                <ul className="skills-list">
                  {skills.slice(0, 4).map((skill, idx) => (
                    <li key={idx}>{skill}</li>
                  ))}
                  {skills.length > 4 && <li>+{skills.length - 4} more</li>}
                </ul>
                <a href="/start" className="btn btn-primary" style={{marginTop: '1rem'}}>
                  Start Interview
                </a>
              </div>
            ))}
          </div>
        </div>

        {/* Features */}
        <div className="card">
          <h3>Key Features</h3>
          <div className="features">
            <div className="feature">
              <span className="icon">❓</span>
              <h4>Smart Question Generation</h4>
              <p>AI-powered question selection based on job role and difficulty</p>
            </div>
            <div className="feature">
              <span className="icon">🔍</span>
              <h4>Semantic Evaluation</h4>
              <p>SBERT-based semantic similarity scoring for descriptive answers</p>
            </div>
            <div className="feature">
              <span className="icon">⚙️</span>
              <h4>Multi-Type Questions</h4>
              <p>MCQ, Descriptive, and Coding problems in one interview</p>
            </div>
            <div className="feature">
              <span className="icon">📊</span>
              <h4>Detailed Analysis</h4>
              <p>Comprehensive scoring with weak area identification</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
