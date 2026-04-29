import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Search, MapPin, TrendingUp,
  BookOpen, Trophy, Brain, ChevronRight
} from 'lucide-react'
import Dashboard    from './pages/Dashboard'
import Analyze      from './pages/Analyze'
import Report       from './pages/Report'
import CareerPath   from './pages/CareerPath'
import Progress     from './pages/Progress'
import Leaderboard  from './pages/Leaderboard'

const NAV = [
  { to: '/',            icon: LayoutDashboard, label: 'Dashboard'    },
  { to: '/analyze',     icon: Search,          label: 'Analyze CV'   },
  { to: '/report',      icon: Brain,           label: 'Gap Report'   },
  { to: '/career',      icon: MapPin,          label: 'Career Path'  },
  { to: '/progress',    icon: TrendingUp,      label: 'My Progress'  },
  { to: '/leaderboard', icon: Trophy,          label: 'Leaderboard'  },
]

export default function App() {
  const loc = useLocation()

  return (
    <div className="app-shell">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <Brain size={22} />
          <span>SkillGap AI</span>
        </div>

        <span className="nav-section-label">Component 4</span>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}

        <div style={{ marginTop: 'auto', padding: '16px 8px 0' }}>
          <div style={{
            background: 'linear-gradient(135deg,rgba(108,99,255,.15),rgba(140,130,255,.08))',
            border: '1px solid rgba(108,99,255,.25)',
            borderRadius: '10px',
            padding: '14px',
            fontSize: '11px',
            color: 'var(--text-muted)',
            lineHeight: 1.6
          }}>
            <strong style={{ color: 'var(--accent-light)', display: 'block', marginBottom: 4 }}>
              Skill Gap & Career Dev
            </strong>
            AI-Driven Recruitment Ecosystem — Component 4
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="main-content">
        <Routes>
          <Route path="/"            element={<Dashboard   />} />
          <Route path="/analyze"     element={<Analyze     />} />
          <Route path="/report"      element={<Report      />} />
          <Route path="/report/:id"  element={<Report      />} />
          <Route path="/career"      element={<CareerPath  />} />
          <Route path="/progress"    element={<Progress    />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
        </Routes>
      </main>
    </div>
  )
}
