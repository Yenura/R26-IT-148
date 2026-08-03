import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import './index.css';

// Pages
import Dashboard from './pages/Dashboard';
import StartInterview from './pages/StartInterview';
import InterviewInterface from './pages/InterviewInterface';
import Results from './pages/Results';

function App() {
  return (
    <Router>
      <div className="app-container">
        <nav className="navbar">
          <div className="navbar-brand">
            <h1>🎯 Interview System</h1>
            <p>Component 2: AI Interview Generation & Evaluation</p>
          </div>
          <ul className="nav-links">
            <li><a href="/">Dashboard</a></li>
            <li><a href="/start">Start Interview</a></li>
          </ul>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/start" element={<StartInterview />} />
          <Route path="/interview/:sessionId" element={<InterviewInterface />} />
          <Route path="/results/:interviewId" element={<Results />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
