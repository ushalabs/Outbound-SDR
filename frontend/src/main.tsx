import React, { lazy, Suspense } from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import { BrowserRouter, NavLink, Route, Routes, Link } from 'react-router-dom'
import {
  Activity,
  ArrowUpRight,
  CheckCheck,
  ChevronRight,
  CircleCheck,
  FileText,
  LayoutDashboard,
  Search,
  Sparkles,
  Users,
  Zap,
} from 'lucide-react'
import { api } from './lib/api'
import type { DatabaseStatus } from './lib/types'
import { EmptyState, Loading } from './components/states'
const ProspectsPage = lazy(() => import('./pages/Prospects'))
const ResearchPage = lazy(() => import('./pages/Research'))
const OutreachPage = lazy(() => import('./pages/Outreach'))
const ApprovalsPage = lazy(() => import('./pages/Approvals'))
const ActivityPage = lazy(() => import('./pages/Activity'))
const DashboardPage = lazy(() => import('./pages/Dashboard'))
import './index.css'

const navigation = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/prospects', label: 'Prospects', icon: Users },
  { path: '/research', label: 'Research', icon: Search },
  { path: '/outreach', label: 'Outreach', icon: FileText },
  { path: '/approvals', label: 'Approvals', icon: CheckCheck },
  { path: '/activity', label: 'Activity', icon: Activity },
]
const queryClient = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 10000 } } })

function Shell() {
  const counts = useQuery({
    queryKey: ['approval-counts'],
    queryFn: () => api<Record<string, number>>('/approvals/counts'),
    refetchInterval: 15000,
  })
  const health = useQuery({
    queryKey: ['health'],
    queryFn: () => api<{ status: string }>('/health'),
    refetchInterval: 30000,
  })
  const database = useQuery({
    queryKey: ['database'],
    queryFn: () => api<DatabaseStatus>('/system/database'),
    refetchInterval: 30000,
  })
  return (
    <div className="app-frame">
      <aside className="sidebar">
        <Link className="brand" to="/" aria-label="Outbound home">
          <Zap fill="currentColor" size={23} />
        </Link>
        <div className="nav-divider" />
        <nav aria-label="Main navigation">
          {navigation.map(({ path, label, icon: Icon }) => (
            <NavLink
              end={path === '/'}
              key={path}
              to={path}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              title={label}
            >
              <Icon size={21} />
              <span>{label}</span>
              {path === '/approvals' && !!counts.data?.pending && (
                <span className="nav-count">{counts.data.pending}</span>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          <span className="avatar">TA</span>
          <span className="sidebar-caption">THINK AI</span>
        </div>
      </aside>
      <div className="main-wrap">
        <header className="topbar">
          <Link to="/" className="wordmark">
            outbound<span> / </span>
            <small>SDR WORKSPACE</small>
          </Link>
          <div className="topbar-right">
            <span className={`connection ${health.isSuccess ? 'online' : ''}`}>
              <span />
              {health.isSuccess
                ? 'Backend online'
                : health.isError
                  ? 'Backend unavailable'
                  : 'Connecting'}
            </span>
            <span className="local-label" title={database.error?.message}>
              {database.isSuccess
                ? 'Neon connected'
                : database.isError
                  ? 'Database unavailable'
                  : 'Connecting to Neon'}
            </span>
            <span className="avatar light">TA</span>
          </div>
        </header>
        <main>
          <Suspense fallback={<Loading />}>
            <Routes>
              {navigation.map(({ path }) => (
                <Route
                  key={path}
                  path={path}
                  element={
                    path === '/prospects' ? (
                      <ProspectsPage />
                    ) : path === '/research' ? (
                      <ResearchPage />
                    ) : path === '/outreach' ? (
                      <OutreachPage />
                    ) : path === '/approvals' ? (
                      <ApprovalsPage />
                    ) : path === '/activity' ? (
                      <ActivityPage />
                    ) : (
                      <DashboardPage />
                    )
                  }
                />
              ))}
              <Route
                path="*"
                element={
                  <EmptyState
                    title="Page not found"
                    description="Return to your workspace."
                    to="/"
                    action="Open overview"
                  />
                }
              />
            </Routes>
          </Suspense>
          <footer>
            <span>
              <Sparkles size={13} /> THINK AI WORKS
            </span>
            <span>
              Research. Personalize. Review.
              <ChevronRight size={13} />
            </span>
          </footer>
        </main>
        <div className="safety-bar">
          <CircleCheck size={14} />
          <span>Human approval required</span>
          <span className="dot" />
          Drafts only · Email sending disabled
          <ArrowUpRight size={13} />
        </div>
      </div>
    </div>
  )
}
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
