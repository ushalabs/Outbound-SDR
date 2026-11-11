import React, { lazy, Suspense } from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import { BrowserRouter, NavLink, Route, Routes, Link } from 'react-router-dom'
import {
  Activity,
  CheckCheck,
  ChevronRight,
  CircleCheck,
  FileText,
  LayoutDashboard,
  Search,
  Users,
  ArrowUpRight,
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
      <header className="app-header">
        <Link className="brand" to="/" aria-label="Outbound home">
          <span className="brand-mark">
            <Zap size={20} />
          </span>
          <span>
            Outbound<small>SDR Agent</small>
          </span>
        </Link>
        <nav aria-label="Main navigation">
          {navigation.map(({ path, label, icon: Icon }) => (
            <NavLink
              end={path === '/'}
              key={path}
              to={path}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              title={label}
            >
              <Icon size={16} />
              <span>{label}</span>
              {path === '/approvals' && !!counts.data?.pending && (
                <span className="nav-count">{counts.data.pending}</span>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="header-actions">
          <Link
            className="round-action"
            to="/prospects"
            aria-label="Search prospects"
            title="Search prospects"
          >
            <Search />
          </Link>
          <Link
            className="round-action"
            to="/approvals"
            aria-label="Open review queue"
            title="Review queue"
          >
            <CheckCheck />
            {Boolean(counts.data?.pending) && <i className="notification-dot" />}
          </Link>
          <span className="workspace-mark" title="Think AI Works">
            TA
          </span>
        </div>
      </header>
      <div className="main-wrap">
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
            <span className="footer-connections">
              <span className={`connection ${health.isSuccess ? 'online' : ''}`}>
                <i />
                {health.isSuccess
                  ? 'Backend online'
                  : health.isError
                    ? 'Backend unavailable'
                    : 'Connecting'}
              </span>
              <span title={database.error?.message}>
                {database.isSuccess
                  ? 'Neon connected'
                  : database.isError
                    ? 'Database unavailable'
                    : 'Connecting to Neon'}
              </span>
            </span>
            <nav className="workflow-trail" aria-label="Outreach workflow">
              <Link to="/research">
                <b>01</b> Evidence
              </Link>
              <ChevronRight size={13} />
              <Link to="/outreach">
                <b>02</b> Draft
              </Link>
              <ChevronRight size={13} />
              <Link to="/approvals">
                <b>03</b> Review
              </Link>
            </nav>
          </footer>
        </main>
        <div className="safety-bar">
          <CircleCheck size={14} />
          <span>Human approval required</span>
          <span className="dot" />
          Drafts only · Email sending disabled
          <span className="safety-brand">
            Think AI Works <ArrowUpRight />
          </span>
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
