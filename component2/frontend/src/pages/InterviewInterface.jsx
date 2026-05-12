import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { interviewAPI, handleAPIError } from '../api';
import '../pages/InterviewInterface.css';

export default function InterviewInterface() {
  const { sessionId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [session, setSession] = useState(location.state?.session || null);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes

  useEffect(() => {
    const fetchSession = async () => {
      if (!session && sessionId) {
        try {
          setLoading(true);
          const data = await interviewAPI.getSession(sessionId);
          setSession(data.session);
        } catch (err) {
          setError(handleAPIError(err));
        } finally {
          setLoading(false);
        }
      }
    };

    fetchSession();
  }, [sessionId, session]);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => prev > 0 ? prev - 1 : 0);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  if (!session) {
    return <main>
      <div className="alert alert-error">
        {loading ? 'Loading interview session...' : (error || 'Session not found')}
      </div>
    </main>;
  }

  if (!session.questions || session.questions.length === 0) {
    return <main>
      <div className="alert alert-error">
        No questions found for this session. Please restart the interview.
      </div>
    </main>;
  }

  const currentQuestion = session.questions[currentQIndex];
  const progress = ((currentQIndex + 1) / session.total_questions) * 100;

  const handleAnswerChange = (answer) => {
    setAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: answer
    }));
  };

  const handleNext = () => {
    if (currentQIndex < session.questions.length - 1) {
      setCurrentQIndex(currentQIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentQIndex > 0) {
      setCurrentQIndex(currentQIndex - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);

      const payloadAnswers = session.questions.map((question) => {
        const answer = answers[question.id];
        const baseAnswer = {
          question_id: question.id,
          question_type: question.question_type,
        };

        if (question.question_type === 'MCQ') {
          return {
            ...baseAnswer,
            selected_option: typeof answer === 'number' ? answer : parseInt(answer, 10),
          };
        }

        if (question.question_type === 'Descriptive') {
          return {
            ...baseAnswer,
            answer_text: answer || '',
          };
        }

        if (question.question_type === 'Coding') {
          return {
            ...baseAnswer,
            code_text: answer || '',
            language: 'Python',
          };
        }

        return {
          ...baseAnswer,
          answer_text: answer || '',
        };
      });

      const result = await interviewAPI.submitAnswers({
        candidate_id: session.candidate_id,
        session_id: session.session_id,
        job_role: session.job_role,
        answers: payloadAnswers
      });

      navigate(`/results/${result.interview_id}`, { state: { result } });
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <main>
      <div className="interview-container">
        {/* Header */}
        <div className="interview-header">
          <div className="header-left">
            <h2>{session.job_role} Interview</h2>
            <p>Question {currentQIndex + 1} of {session.total_questions}</p>
          </div>
          <div className="header-right">
            <div className="timer" style={{color: timeLeft < 120 ? '#e74c3c' : '#27ae60'}}>
              ⏱️ {formatTime(timeLeft)}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="progress-bar">
          <div className="progress-fill" style={{width: `${progress}%`}}></div>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {/* Question Section */}
        <div className="question-section card">
          <div className="question-meta">
            <span className="badge" style={{backgroundColor: 
              currentQuestion.question_type === 'MCQ' ? '#3498db' :
              currentQuestion.question_type === 'Coding' ? '#e74c3c' : '#27ae60'
            }}>
              {currentQuestion.question_type}
            </span>
            <span className="badge" style={{backgroundColor:
              currentQuestion.difficulty === 'Easy' ? '#27ae60' :
              currentQuestion.difficulty === 'Hard' ? '#e74c3c' : '#f39c12'
            }}>
              {currentQuestion.difficulty}
            </span>
          </div>

          <h3>{currentQuestion.question_text}</h3>

          {/* Answer Input */}
          <div className="answer-section">
            {currentQuestion.question_type === 'MCQ' && (
              <div className="mcq-options">
                {currentQuestion.options?.map((option, idx) => (
                  <label key={idx} className="option">
                    <input
                      type="radio"
                      name="mcq-answer"
                      value={idx}
                      checked={answers[currentQuestion.id] === idx}
                      onChange={() => handleAnswerChange(idx)}
                    />
                    <span>{option.text}</span>
                  </label>
                ))}
              </div>
            )}

            {currentQuestion.question_type === 'Descriptive' && (
              <textarea
                className="text-answer"
                placeholder="Type your answer here..."
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => handleAnswerChange(e.target.value)}
                rows="8"
              />
            )}

            {currentQuestion.question_type === 'Coding' && (
              <div>
                <textarea
                  className="code-answer"
                  placeholder="Write your Python code here..."
                  value={answers[currentQuestion.id] || ''}
                  onChange={(e) => handleAnswerChange(e.target.value)}
                  rows="10"
                />
                <div className="test-cases">
                  <h4>Test Cases:</h4>
                  {currentQuestion.test_cases?.slice(0, 2).map((tc, idx) => (
                    <div key={idx} className="test-case">
                      <p><strong>Test {idx + 1}:</strong> {JSON.stringify(tc.input)}</p>
                      <p><strong>Expected:</strong> {JSON.stringify(tc.expected_output)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <div className="navigation">
          <button 
            className="btn btn-secondary"
            onClick={handlePrev}
            disabled={currentQIndex === 0}
          >
            ← Previous
          </button>

          <div className="nav-center">
            {currentQIndex + 1} / {session.total_questions}
          </div>

          {currentQIndex === session.total_questions - 1 ? (
            <button 
              className="btn btn-success"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? 'Submitting...' : 'Submit Interview'}
            </button>
          ) : (
            <button 
              className="btn btn-primary"
              onClick={handleNext}
            >
              Next →
            </button>
          )}
        </div>
      </div>
    </main>
  );
}
