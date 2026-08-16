import { useState, useEffect, Suspense, lazy } from 'react'
import { Routes, Route, NavLink, Navigate, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, FileSearch, MessagesSquare, Trophy,
  Search, TrendingUp, ListOrdered, Brain, Sparkles, Layers,
  Sun, Moon, Briefcase, BarChart3, Route as RouteIcon, Target, Award,
  Menu, X, User, LogOut, ChevronDown
} from 'lucide-react'
import { useTheme } from './context/ThemeContext'

const Landing        = lazy(() => import('./pages/Landing'))
const CompanyLogin   = lazy(() => import('./pages/auth/CompanyLogin'))
const CompanyRegister= lazy(() => import('./pages/auth/CompanyRegister'))
const CandidateLogin = lazy(() => import('./pages/auth/CandidateLogin'))
const CandidateRegister = lazy(() => import('./pages/auth/CandidateRegister'))
const CandidateDashboard = lazy(() => import('./pages/CandidateDashboard'))
const CompanyDashboard   = lazy(() => import('./pages/CompanyDashboard'))
const ApplicantPipeline = lazy(() => import('./pages/ApplicantPipeline'))
const JobBoard      = lazy(() => import('./pages/JobBoard'))
const JobDetail     = lazy(() => import('./pages/JobDetail'))
const InterviewPage = lazy(() => import('./pages/Interview'))
const CVMatchPage   = lazy(() => import('./pages/CVMatch'))
const RankingPage   = lazy(() => import('./pages/Ranking'))
const SkillGapPage  = lazy(() => import('./pages/SkillGap'))
const CareerPathPage= lazy(() => import('./pages/CareerPath'))
const ProgressPage  = lazy(() => import('./pages/Progress'))
const LeaderboardPage = lazy(() => import('./pages/Leaderboard'))
const ProfilePage   = lazy(() => import('./pages/Profile'))
const CompanyProfilePage = lazy(() => import('./pages/CompanyProfile'))

const Loading = () => (
  <div style={{ padding: 60, textAlign: 'center', color: 'var(--text-muted)' }}>
    <Brain size={36} className="spin" style={{ color: 'var(--color-primary)', marginBottom: 12 }} />
    <div style={{ fontSize: 14, fontWeight: 600 }}>Loading AI Recruitment Intelligence...</div>
  </div>
)

function PrivateRoute({ children, role }) {
  const token = localStorage.getItem('recruitai.token')
  const userRole = localStorage.getItem('recruitai.role')
  const userId = localStorage.getItem('recruitai.user_id')
  if (!token || !userId) return <Navigate to="/login/candidate" />
  if (role && userRole !== role) return <Navigate to="/" />
  return children
}

export default function App() {
  const { theme, toggleTheme } = useTheme()
  const role = localStorage.getItem('recruitai.role')
  const navigate = useNavigate()
  const [mobileMenu, setMobileMenu] = useState(false)
  const [userMenu, setUserMenu] = useState(false)
  const [userName, setUserName] = useState('')
  const [userAvatar, setUserAvatar] = useState('')

  useEffect(() => {
    const name = localStorage.getItem('recruitai.name') || ''
    setUserName(name)
    const avatar = localStorage.getItem('recruitai.avatar') || ''
    setUserAvatar(avatar)
  }, [role])

  const candidateLinks = [
    { to: '/candidate/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/candidate/jobs', icon: Briefcase, label: 'Jobs' },
    { to: '/candidate/interview', icon: MessagesSquare, label: 'Interview' },
    { to: '/pipeline/cv-match', icon: FileSearch, label: 'CV Match' },
    { to: '/pipeline/skill-gap', icon: Target, label: 'Skill Gap' },
    { to: '/pipeline/progress', icon: TrendingUp, label: 'Progress' },
  ]

  const companyLinks = [
    { to: '/company/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/pipeline/ranking', icon: ListOrdered, label: 'Ranking' },
    { to: '/pipeline/leaderboard', icon: Award, label: 'Leaderboard' },
  ]

  const navLinks = role === 'candidate' ? candidateLinks : role === 'company' ? companyLinks : []

  const handleLogout = () => {
    localStorage.clear()
    setUserMenu(false)
    window.location.href = '/'
  }

  const profileLink = role === 'candidate' ? '/profile' : role === 'company' ? '/company/profile' : null

  return (
    <div className="app-root">
      {/* Top Navbar */}
      {navLinks.length > 0 && (
        <nav className="navbar">
          <div className="navbar-inner">
            <div className="navbar-left">
              <div className="navbar-logo" onClick={() => navigate(role === 'candidate' ? '/candidate/dashboard' : '/company/dashboard')}>
                <Brain size={22} style={{ color: 'var(--color-primary)' }} />
                <span className="navbar-brand">RecruitAI</span>
              </div>
              <div className="navbar-links">
                {navLinks.map((l) => (
                  <NavLink key={l.to} to={l.to} className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}>
                    <l.icon size={15} />
                    <span>{l.label}</span>
                  </NavLink>
                ))}
              </div>
            </div>

            <div className="navbar-right" style={{ gap: 10 }}>
              <button className="btn-ghost btn-sm" onClick={toggleTheme} title={theme === 'dark' ? 'Light mode' : 'Dark mode'}>
                {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              </button>

              {profileLink && (
                <div className="navbar-user" onClick={() => setUserMenu(!userMenu)}>
                  {userAvatar ? (
                    <img src={userAvatar} alt="" className="navbar-avatar" />
                  ) : (
                    <div className="navbar-avatar navbar-avatar-fallback">
                      {(userName || 'U')[0].toUpperCase()}
                    </div>
                  )}
                  <ChevronDown size={14} />
                  {userMenu && (
                    <div className="navbar-dropdown">
                      <div className="navbar-dropdown-label">{userName || 'User'}</div>
                      <button onClick={() => { navigate(profileLink); setUserMenu(false) }}>
                        <User size={14} /> Profile
                      </button>
                      <button onClick={handleLogout}>
                        <LogOut size={14} /> Sign Out
                      </button>
                    </div>
                  )}
                </div>
              )}

              <button className="navbar-hamburger" onClick={() => setMobileMenu(!mobileMenu)}>
                {mobileMenu ? <X size={20} /> : <Menu size={20} />}
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenu && (
            <div className="navbar-mobile">
              {navLinks.map((l) => (
                <NavLink key={l.to} to={l.to} className={({ isActive }) => `navbar-mobile-link ${isActive ? 'active' : ''}`}
                  onClick={() => setMobileMenu(false)}>
                  <l.icon size={18} /> {l.label}
                </NavLink>
              ))}
              {profileLink && (
                <button className="navbar-mobile-link" onClick={() => { navigate(profileLink); setMobileMenu(false) }}>
                  <User size={18} /> Profile
                </button>
              )}
              <button className="navbar-mobile-link" onClick={handleLogout}>
                <LogOut size={18} /> Sign Out
              </button>
            </div>
          )}
        </nav>
      )}

      {/* Main Content shell */}
      <div className="app-shell">
        <main className="main-content">
          <Suspense fallback={<Loading />}>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/login/company" element={<CompanyLogin />} />
              <Route path="/register/company" element={<CompanyRegister />} />
              <Route path="/login/candidate" element={<CandidateLogin />} />
              <Route path="/register/candidate" element={<CandidateRegister />} />

              <Route path="/candidate/dashboard" element={<PrivateRoute role="candidate"><CandidateDashboard /></PrivateRoute>} />
              <Route path="/candidate/jobs" element={<PrivateRoute role="candidate"><JobBoard /></PrivateRoute>} />
              <Route path="/candidate/jobs/:id" element={<PrivateRoute role="candidate"><JobDetail /></PrivateRoute>} />
              <Route path="/candidate/interview" element={<PrivateRoute role="candidate"><InterviewPage /></PrivateRoute>} />
              <Route path="/profile" element={<PrivateRoute role="candidate"><ProfilePage /></PrivateRoute>} />

              <Route path="/company/dashboard" element={<PrivateRoute role="company"><CompanyDashboard /></PrivateRoute>} />
              <Route path="/company/jobs/:id" element={<PrivateRoute role="company"><JobDetail /></PrivateRoute>} />
              <Route path="/company/pipeline/:jobId" element={<PrivateRoute role="company"><ApplicantPipeline /></PrivateRoute>} />
              <Route path="/company/profile" element={<PrivateRoute role="company"><CompanyProfilePage /></PrivateRoute>} />

              <Route path="/pipeline/cv-match" element={<PrivateRoute><CVMatchPage /></PrivateRoute>} />
              <Route path="/candidate/cv-match" element={<PrivateRoute><CVMatchPage /></PrivateRoute>} />
              <Route path="/cv-match" element={<PrivateRoute><CVMatchPage /></PrivateRoute>} />
              <Route path="/pipeline/ranking" element={<PrivateRoute><RankingPage /></PrivateRoute>} />
              <Route path="/pipeline/skill-gap" element={<PrivateRoute><SkillGapPage /></PrivateRoute>} />
              <Route path="/pipeline/career-path" element={<Navigate to="/pipeline/cv-match" replace />} />
              <Route path="/pipeline/progress" element={<PrivateRoute><ProgressPage /></PrivateRoute>} />
              <Route path="/pipeline/leaderboard" element={<PrivateRoute><LeaderboardPage /></PrivateRoute>} />

              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </div>
  )
}
