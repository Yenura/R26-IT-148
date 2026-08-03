import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import '../pages/Results.css';

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const [result] = useState(location.state?.result || null);

  if (!result) {
    return (
      <main>
        <div className="alert alert-error">
          Results not found. Please take an interview first.
        </div>
      </main>
    );
  }

  const gradeColor = {
    'Excellent': '#27ae60',
    'Good': '#3498db',
    'Average': '#f39c12',
    'Below Average': '#e67e22',
    'Poor': '#e74c3c'
  };

  return (
    <main>
      <div className="results-container">
        <h2>Interview Results</h2>
        <p className="subtitle">Detailed analysis of your performance</p>

        {/* Score Card */}
        <div className="score-card card">
          <div className="score-display">
            <div className="score-circle">
              <div className="score-value">{result.interview_score.toFixed(1)}</div>
              <div className="score-max">/100</div>
            </div>
            <div className="grade-info">
              <div className="grade-badge" style={{backgroundColor: gradeColor[result.grade]}}>
                {result.grade}
              </div>
              <p className="grade-desc">
                {result.grade === 'Excellent' && 'Outstanding performance! You are a strong candidate.'}
                {result.grade === 'Good' && 'Strong performance with minor areas for improvement.'}
                {result.grade === 'Average' && 'Acceptable performance but has notable gaps.'}
                {result.grade === 'Below Average' && 'Needs significant improvement in key areas.'}
                {result.grade === 'Poor' && 'Consider further preparation before next interview.'}
              </p>
            </div>
          </div>
        </div>

        {/* Component Scores */}
        <div className="scores-grid">
          <div className="score-item">
            <h4>MCQ Score</h4>
            <div className="score-bar">
              <div className="score-bar-fill" style={{width: `${result.mcq_score}%`, backgroundColor: '#3498db'}}></div>
            </div>
            <p className="score-text">{result.mcq_score.toFixed(1)}/100</p>
          </div>

          <div className="score-item">
            <h4>Descriptive Score</h4>
            <div className="score-bar">
              <div className="score-bar-fill" style={{width: `${result.descriptive_score}%`, backgroundColor: '#27ae60'}}></div>
            </div>
            <p className="score-text">{result.descriptive_score.toFixed(1)}/100</p>
          </div>

          <div className="score-item">
            <h4>Coding Score</h4>
            <div className="score-bar">
              <div className="score-bar-fill" style={{width: `${result.coding_score}%`, backgroundColor: '#e74c3c'}}></div>
            </div>
            <p className="score-text">{result.coding_score.toFixed(1)}/100</p>
          </div>
        </div>

        {/* Summary */}
        <div className="summary-card card">
          <h3>Interview Summary</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="label">Job Role:</span>
              <span className="value">{result.job_role}</span>
            </div>
            <div className="summary-item">
              <span className="label">Candidate ID:</span>
              <span className="value">{result.candidate_id}</span>
            </div>
            <div className="summary-item">
              <span className="label">Session ID:</span>
              <span className="value">{result.session_id}</span>
            </div>
            <div className="summary-item">
              <span className="label">Interview ID:</span>
              <span className="value">{result.interview_id}</span>
            </div>
            <div className="summary-item">
              <span className="label">MCQ Questions:</span>
              <span className="value">{result.mcq_total}</span>
            </div>
            <div className="summary-item">
              <span className="label">Descriptive Questions:</span>
              <span className="value">{result.descriptive_total}</span>
            </div>
            <div className="summary-item">
              <span className="label">Coding Questions:</span>
              <span className="value">{result.coding_total}</span>
            </div>
            <div className="summary-item">
              <span className="label">Completed At:</span>
              <span className="value">{new Date(result.created_at).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Weak Areas */}
        {result.weak_topics && result.weak_topics.length > 0 && (
          <div className="weak-areas-card card">
            <h3>📊 Areas for Improvement</h3>
            <div className="weak-topics">
              {result.weak_topics.map((topic, idx) => (
                <div key={idx} className="topic-tag">
                  {topic}
                </div>
              ))}
            </div>
            <div className="recommendations">
              <h4>💡 Recommendations</h4>
              <ul>
                <li>Review fundamental concepts in weak topic areas</li>
                <li>Practice similar problems to build confidence</li>
                <li>Take mock interviews to improve time management</li>
                <li>Study best practices and optimization techniques</li>
              </ul>
            </div>
          </div>
        )}

        {/* Weights Used */}
        {result.weights_used && (
          <div className="weights-card card">
            <h3>Scoring Weights Used</h3>
            <div className="weights-display">
              <div className="weight-item">
                <span className="weight-label">MCQ</span>
                <div className="weight-bar">
                  <div className="weight-fill" style={{width: `${(result.weights_used.mcq || 0.25) * 100}%`, backgroundColor: '#3498db'}}></div>
                </div>
                <span className="weight-value">{((result.weights_used.mcq || 0.25) * 100).toFixed(0)}%</span>
              </div>
              <div className="weight-item">
                <span className="weight-label">Descriptive</span>
                <div className="weight-bar">
                  <div className="weight-fill" style={{width: `${(result.weights_used.descriptive || 0.35) * 100}%`, backgroundColor: '#27ae60'}}></div>
                </div>
                <span className="weight-value">{((result.weights_used.descriptive || 0.35) * 100).toFixed(0)}%</span>
              </div>
              <div className="weight-item">
                <span className="weight-label">Coding</span>
                <div className="weight-bar">
                  <div className="weight-fill" style={{width: `${(result.weights_used.coding || 0.40) * 100}%`, backgroundColor: '#e74c3c'}}></div>
                </div>
                <span className="weight-value">{((result.weights_used.coding || 0.40) * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-buttons">
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            ← Back to Dashboard
          </button>
          <button className="btn btn-success" onClick={() => navigate('/start')}>
            Take Another Interview →
          </button>
        </div>
      </div>
    </main>
  );
}
