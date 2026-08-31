import { useState, useEffect, useCallback, useRef, useMemo, Suspense, lazy } from 'react'
import { Routes, Route, NavLink, Navigate, useNavigate, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, FileSearch, MessagesSquare, Trophy,
  Search, TrendingUp, ListOrdered, Brain, Sparkles, Layers,
  Sun, Moon, Briefcase, BarChart3, Route as RouteIcon, Target, Award,
  Menu, X, User, LogOut, ChevronDown
} from 'lucide-react'
import { useTheme } from './context/ThemeContext'
import GlobalBackground from './components/GlobalBackground'
import ErrorBoundary from './components/ErrorBoundary'

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
const ProgressPage  = lazy(() => import('./pages/Progress'))
const LeaderboardPage = lazy(() => import('./pages/Leaderboard'))
const ProfilePage   = lazy(() => import('./pages/Profile'))
const CompanyProfilePage = lazy(() => import('./pages/CompanyProfile'))

const Loading = () => (
  <div style={{ padding: 60, textAlign: 'center' }}>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14, maxWidth: 320, margin: '0 auto' }}>
      <div className="skeleton" style={{ height: 28, width: '60%', margin: '0 auto', borderRadius: 8 }} />
      <div className="skeleton" style={{ height: 16, width: '85%', margin: '0 auto', borderRadius: 6 }} />
      <div className="skeleton" style={{ height: 16, width: '45%', margin: '0 auto', borderRadius: 6 }} />
    </div>
  </div>
)

function PrivateRoute({ children, role }) {
  const token = localStorage.getItem('recruitai.token')
  const userRole = localStorage.getItem('recruitai.role')

  if (!token) {
    return <Navigate to={role === 'company' ? '/login/company' : '/login/candidate'} replace />
  }
  if (role && userRole && userRole !== role) {
    return <Navigate to={userRole === 'company' ? '/company/dashboard' : '/candidate/dashboard'} replace />
  }
  return children
}

export default function App() {
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const role = localStorage.getItem('recruitai.role')
  const [mobileMenu, setMobileMenu] = useState(false)
  const [userMenu, setUserMenu] = useState(false)
  const [userName, setUserName] = useState('')
  const [userAvatar, setUserAvatar] = useState('')

  useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'))
      return
    }
    const observer = new IntersectionObserver(
      (entries) => entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target) } }),
      { threshold: 0.15 }
    )
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el))
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const name = localStorage.getItem('recruitai.name') || ''
    setUserName(name)
    const avatar = localStorage.getItem('recruitai.avatar') || ''
    setUserAvatar(avatar)
  }, [role, location.pathname])

  const candidateLinks = [
    { to: '/candidate/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/candidate/jobs', icon: Briefcase, label: 'Job Board' },
    { to: '/candidate/interview', icon: MessagesSquare, label: 'AI Interview' },
    { to: '/pipeline/cv-match', icon: FileSearch, label: 'CV Match' },
    { to: '/pipeline/skill-gap', icon: Target, label: 'Skill Gap' },
    { to: '/pipeline/progress', icon: TrendingUp, label: 'Progress' },
  ]

  const companyLinks = [
    { to: '/company/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/pipeline/ranking', icon: ListOrdered, label: 'Candidate Ranking' },
    { to: '/pipeline/leaderboard', icon: Award, label: 'Leaderboard' },
  ]

  const navLinks = role === 'candidate' ? candidateLinks : role === 'company' ? companyLinks : []

  const handleLogout = useCallback(() => {
    localStorage.removeItem('recruitai.token')
    localStorage.removeItem('recruitai.role')
    localStorage.removeItem('recruitai.user_id')
    localStorage.removeItem('recruitai.name')
    localStorage.removeItem('recruitai.avatar')
    setUserMenu(false)
    navigate('/')
  }, [navigate])

  const profileLink = role === 'candidate' ? '/profile' : role === 'company' ? '/company/profile' : null

  const userMenuRef = useRef(null)
  useEffect(() => {
    if (!userMenu) return
    const handleClick = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setUserMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [userMenu])

  useEffect(() => {
    const path = location.pathname
    let title = 'RecruitAI'
    if (path.includes('/candidate/dashboard')) title = 'Candidate Dashboard | RecruitAI'
    else if (path.includes('/company/dashboard')) title = 'Company Dashboard | RecruitAI'
    else if (path.includes('/candidate/jobs')) title = 'Job Board | RecruitAI'
    else if (path.includes('/interview')) title = 'AI Interview | RecruitAI'
    else if (path.includes('/cv-match')) title = 'CV Match | RecruitAI'
    else if (path.includes('/skill-gap')) title = 'Skill Gap Analysis | RecruitAI'
    else if (path.includes('/ranking')) title = 'Candidate Ranking | RecruitAI'
    else if (path.includes('/leaderboard')) title = 'Leaderboard | RecruitAI'
    else if (path.includes('/progress')) title = 'Progress Tracking | RecruitAI'
    else if (path.includes('/profile')) title = 'Profile | RecruitAI'
    else if (path.includes('/login')) title = 'Login | RecruitAI'
    else if (path.includes('/register')) title = 'Register | RecruitAI'
    document.title = title
  }, [location.pathname])

  return (
    <div className="app-root">
      <GlobalBackground />
      {/* Top Navbar */}
      {navLinks.length > 0 && (
        <nav className="navbar" aria-label="Main Navigation">
          <div className="navbar-inner">
            <div className="navbar-left">
              <div
                className="navbar-logo"
                onClick={() => navigate(role === 'candidate' ? '/candidate/dashboard' : '/company/dashboard')}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && navigate(role === 'candidate' ? '/candidate/dashboard' : '/company/dashboard')}
                title="Go to dashboard"
              >
                <div style={{
                  width: 32,
                  height: 32,
                  borderRadius: 'var(--radius-md)',
                  background: 'linear-gradient(135deg, #2563eb, #6366f1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 2px 8px rgba(37, 99, 235, 0.4)',
                  flexShrink: 0
                }}>
                  <Brain size={19} color="#ffffff" strokeWidth={2.5} />
                </div>
                <span className="navbar-brand">RecruitAI</span>
                <span style={{
                  fontSize: '10px',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-full)',
                  background: role === 'company' ? 'var(--color-purple-muted)' : 'var(--color-primary-muted)',
                  color: role === 'company' ? 'var(--color-purple)' : 'var(--color-primary)',
                  border: `1px solid ${role === 'company' ? 'rgba(139, 92, 246, 0.25)' : 'rgba(59, 130, 246, 0.25)'}`,
                }}>
                  {role === 'company' ? 'Recruiter' : 'Candidate'}
                </span>
              </div>
              <div className="navbar-links">
                {navLinks.map((l) => (
                  <NavLink
                    key={l.to}
                    to={l.to}
                    className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}
                  >
                    <l.icon size={15} />
                    <span>{l.label}</span>
                  </NavLink>
                ))}
              </div>
            </div>

            <div className="navbar-right" style={{ gap: 10 }}>
              <button
                className="btn-ghost btn-sm"
                onClick={toggleTheme}
                title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
                aria-label="Toggle theme"
                style={{ width: 44, height: 44, padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              >
                {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
              </button>

              {profileLink && (
                <div
                  ref={userMenuRef}
                  className="navbar-user"
                  onClick={() => setUserMenu(!userMenu)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      setUserMenu(!userMenu)
                    }
                    if (e.key === 'Escape') setUserMenu(false)
                  }}
                  role="button"
                  tabIndex={0}
                  aria-expanded={userMenu}
                  aria-haspopup="true"
                >
                  {userAvatar ? (
                    <img src={userAvatar} alt="User Avatar" className="navbar-avatar" />
                  ) : (
                    <div className="navbar-avatar navbar-avatar-fallback">
                      {(userName || (role === 'company' ? 'C' : 'U'))[0].toUpperCase()}
                    </div>
                  )}
                  <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 600, maxWidth: 110, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {userName || (role === 'company' ? 'Employer' : 'Candidate')}
                  </span>
                  <ChevronDown size={13} style={{ color: 'var(--color-fg-muted)' }} />

                  {userMenu && (
                    <div className="navbar-dropdown" onClick={(e) => e.stopPropagation()}>
                      <div className="navbar-dropdown-label">
                        <div style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 180 }}>{userName || 'Account'}</div>
                        <div style={{ textTransform: 'capitalize', color: 'var(--color-fg-muted)', fontSize: 'var(--p-text-xs)' }}>{role} Profile</div>
                      </div>
                      <button onClick={() => { navigate(profileLink); setUserMenu(false) }}>
                        <User size={14} /> Profile & Settings
                      </button>
                      <button onClick={handleLogout} style={{ color: 'var(--color-danger)' }}>
                        <LogOut size={14} /> Sign Out
                      </button>
                    </div>
                  )}
                </div>
              )}

              <button
                className="navbar-hamburger"
                onClick={() => setMobileMenu(!mobileMenu)}
                aria-label="Toggle navigation menu"
                aria-expanded={mobileMenu}
              >
                {mobileMenu ? <X size={20} /> : <Menu size={20} />}
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenu && (
            <div className="navbar-mobile">
              <div style={{ padding: '8px 16px 12px', borderBottom: '1px solid var(--color-border-subtle)', marginBottom: 8 }}>
                <span style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-full)',
                  background: role === 'company' ? 'var(--color-purple-muted)' : 'var(--color-primary-muted)',
                  color: role === 'company' ? 'var(--color-purple)' : 'var(--color-primary)',
                }}>
                  {role === 'company' ? 'Recruiter Portal' : 'Candidate Portal'}
                </span>
              </div>
              {navLinks.map((l) => (
                <NavLink
                  key={l.to}
                  to={l.to}
                  className={({ isActive }) => `navbar-mobile-link ${isActive ? 'active' : ''}`}
                  onClick={() => setMobileMenu(false)}
                >
                  <l.icon size={18} /> {l.label}
                </NavLink>
              ))}
              {profileLink && (
                <button className="navbar-mobile-link" onClick={() => { navigate(profileLink); setMobileMenu(false) }}>
                  <User size={18} /> Profile & Settings
                </button>
              )}
              <button className="navbar-mobile-link" onClick={handleLogout} style={{ color: 'var(--color-danger)' }}>
                <LogOut size={18} /> Sign Out
              </button>
            </div>
          )}
        </nav>
      )}

      {/* Main Content Shell */}
      <div className="app-shell">
        <main className="main-content">
          <ErrorBoundary>
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

              {/* Seamless Universal Route Aliases */}
              <Route path="/pipeline/cv-match" element={<PrivateRoute><CVMatchPage /></PrivateRoute>} />
              <Route path="/candidate/cv-match" element={<PrivateRoute><CVMatchPage /></PrivateRoute>} />
              <Route path="/cv-match" element={<PrivateRoute><CVMatchPage /></PrivateRoute>} />

              <Route path="/pipeline/ranking" element={<PrivateRoute><RankingPage /></PrivateRoute>} />
              <Route path="/company/ranking" element={<PrivateRoute><RankingPage /></PrivateRoute>} />
              <Route path="/candidate/ranking" element={<PrivateRoute><RankingPage /></PrivateRoute>} />
              <Route path="/ranking" element={<PrivateRoute><RankingPage /></PrivateRoute>} />

              <Route path="/pipeline/skill-gap" element={<PrivateRoute><SkillGapPage /></PrivateRoute>} />
              <Route path="/candidate/skill-gap" element={<PrivateRoute><SkillGapPage /></PrivateRoute>} />
              <Route path="/skill-gap" element={<PrivateRoute><SkillGapPage /></PrivateRoute>} />

              <Route path="/pipeline/career-path" element={<Navigate to="/pipeline/cv-match" replace />} />
              <Route path="/career-path" element={<Navigate to="/pipeline/cv-match" replace />} />

              <Route path="/pipeline/progress" element={<PrivateRoute><ProgressPage /></PrivateRoute>} />
              <Route path="/candidate/progress" element={<PrivateRoute><ProgressPage /></PrivateRoute>} />
              <Route path="/progress" element={<PrivateRoute><ProgressPage /></PrivateRoute>} />

              <Route path="/pipeline/leaderboard" element={<PrivateRoute><LeaderboardPage /></PrivateRoute>} />
              <Route path="/company/leaderboard" element={<PrivateRoute><LeaderboardPage /></PrivateRoute>} />
              <Route path="/candidate/leaderboard" element={<PrivateRoute><LeaderboardPage /></PrivateRoute>} />
              <Route path="/leaderboard" element={<PrivateRoute><LeaderboardPage /></PrivateRoute>} />

              <Route path="/jobs" element={<PrivateRoute><JobBoard /></PrivateRoute>} />
              <Route path="/interview" element={<PrivateRoute><InterviewPage /></PrivateRoute>} />

              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </Suspense>
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}
