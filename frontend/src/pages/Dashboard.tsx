import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  CheckCheck,
  ChevronRight,
  Clock3,
  FileText,
  Layers3,
  Plus,
  Search,
  Users,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from '@/lib/api'
import type { ActivityEvent } from '@/lib/types'
import { activityLink, eventLabel } from '@/lib/activity'
import { Button } from '@/components/ui/button'
import { ErrorState } from '@/components/states'

interface Day {
  date: string
  prospects: number
  research: number
  generated: number
  approved: number
  rejected: number
}
interface Analytics {
  range: { start: string; end: string; days: number; timezone: string }
  totals: {
    prospects: number
    researched: number
    qualified: number
    unqualified: number
    pending: number
    approved: number
    rejected: number
    generated: number
    research_runs: number
  }
  prospect_growth_pct: number | null
  previous_prospects: number
  research_coverage_pct: number | null
  qualification_pct: number | null
  approval_turnaround_minutes: number | null
  daily: Day[]
  statuses: { name: string; value: number }[]
  industries: { name: string; value: number }[]
  recent_activity: ActivityEvent[]
}
const colors = ['#D92D20', '#F97066', '#FDA29B', '#7A271A', '#FEE4E2']
const chartStyle = {
  borderRadius: 10,
  border: '1px solid #EAECF0',
  fontSize: 11,
  boxShadow: '0 8px 20px #10182810',
}
function dateLabel(value: string) {
  return new Date(`${value}T12:00:00`).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  })
}
function today() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
function SmallEmpty({ text }: { text: string }) {
  return (
    <div className="chart-empty">
      <span className="chart-empty-icon">
        <Layers3 size={20} />
      </span>
      <p>{text}</p>
    </div>
  )
}
export default function DashboardPage() {
  const [period, setPeriod] = useState('30'),
    [start, setStart] = useState(''),
    [end, setEnd] = useState(today())
  const lower =
    period === 'custom'
      ? start
      : (() => {
          const d = new Date(`${end}T12:00:00`)
          d.setDate(d.getDate() - Number(period) + 1)
          return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
        })()
  const query = useQuery({
    queryKey: ['analytics', lower, end],
    queryFn: () => api<Analytics>(`/analytics?start=${lower}&end=${end}`),
    enabled: !!lower && !!end,
    refetchInterval: 30000,
  })
  const data = query.data,
    totals = data?.totals
  return (
    <>
      <div className="page-heading dashboard-heading">
        <div>
          <div className="eyebrow">YOUR PIPELINE, IN FOCUS</div>
          <h1>
            Workspace overview<span className="heading-dot">.</span>
          </h1>
          <p>A clear view of the work behind your next conversation.</p>
        </div>
        <div className="actions">
          <label className="date-select">
            <CalendarDays size={14} />
            <select
              aria-label="Dashboard date range"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="custom">Custom range</option>
            </select>
          </label>
          <Button asChild>
            <Link to="/prospects">
              <Plus size={15} />
              Build pipeline
            </Link>
          </Button>
        </div>
      </div>
      {period === 'custom' && (
        <div className="custom-date-row">
          <label>
            From
            <input
              type="date"
              aria-label="Start date"
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </label>
          <label>
            Through
            <input
              type="date"
              aria-label="End date"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
            />
          </label>
          <span className="help">Up to 366 days · Asia/Karachi</span>
        </div>
      )}
      {query.error ? (
        <section className="card">
          <ErrorState error={query.error} retry={() => void query.refetch()} />
        </section>
      ) : !data ? (
        <div className="dashboard-skeleton" role="status" aria-label="Loading dashboard">
          <div />
          <div />
          <div />
        </div>
      ) : (
        <>
          <section className="overview-panel">
            <div className="overview-left">
              <div className="hero-card">
                <div className="hero-top">
                  <span>
                    <Users size={15} />
                    TOTAL PROSPECTS
                  </span>
                  <span className="hero-period">{data.range.days} days</span>
                </div>
                <div className="hero-number" data-testid="total-prospects">
                  {totals!.prospects.toLocaleString()}
                </div>
                <div className="hero-caption">Prospects added in the selected period</div>
                <div className="hero-bottom">
                  <span className="hero-growth">
                    {data.prospect_growth_pct === null ? (
                      <>
                        <span className="growth-line" />
                        No prior-period baseline
                      </>
                    ) : (
                      <>
                        {data.prospect_growth_pct >= 0 ? (
                          <ArrowUpRight size={14} />
                        ) : (
                          <ArrowDownRight size={14} />
                        )}{' '}
                        {Math.abs(data.prospect_growth_pct)}% vs previous {data.range.days} days
                      </>
                    )}
                  </span>
                  <Link to="/prospects" aria-label="Manage prospects">
                    <ArrowUpRight size={21} />
                  </Link>
                </div>
              </div>
              <div className="hero-support">
                <div className="prospect-spark">
                  <div className="small-card-heading">
                    <span>Prospect trend</span>
                    <span>
                      {dateLabel(data.range.start)} – {dateLabel(data.range.end)}
                    </span>
                  </div>
                  {totals!.prospects ? (
                    <ResponsiveContainer width="100%" height={68} minWidth={0}>
                      <BarChart data={data.daily}>
                        <Tooltip
                          labelFormatter={(label) => dateLabel(String(label ?? ''))}
                          contentStyle={chartStyle}
                        />
                        <Bar
                          isAnimationActive={false}
                          dataKey="prospects"
                          name="Prospects added"
                          fill="#D92D20"
                          radius={[3, 3, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="empty-spark">Your first prospect starts the trend.</div>
                  )}
                  <div className="spark-caption">
                    <span className="legend-dot" />
                    Real additions, day by day
                  </div>
                </div>
                <div className="coverage-card">
                  <div className="small-card-heading">
                    <span>Research coverage</span>
                    <Search size={14} />
                  </div>
                  <strong>
                    {data.research_coverage_pct === null ? '—' : `${data.research_coverage_pct}%`}
                  </strong>
                  <p>
                    {totals!.researched} of {totals!.prospects} prospects researched
                  </p>
                  <div className="progress-track">
                    <span style={{ width: `${data.research_coverage_pct ?? 0}%` }} />
                  </div>
                </div>
              </div>
            </div>
            <div className="overview-right">
              <div className="card-title">
                <div>
                  <div className="eyebrow">FROM DRAFT TO DECISION</div>
                  <h2>Outreach activity</h2>
                </div>
                <span className="chart-total">
                  {totals!.generated}
                  <small>drafts generated</small>
                </span>
              </div>
              <div className="chart-key">
                <span>
                  <i style={{ background: '#D92D20' }} />
                  Generated drafts
                </span>
                <span>
                  <i style={{ background: '#FDA29B' }} />
                  Approved versions
                </span>
                <span>
                  <i style={{ background: '#7A271A' }} />
                  Rejected versions
                </span>
              </div>
              {data.daily.some((d) => d.generated || d.approved || d.rejected) ? (
                <ResponsiveContainer width="100%" height={227} minWidth={0}>
                  <BarChart data={data.daily} barGap={3}>
                    <CartesianGrid stroke="#F2F4F7" vertical={false} />
                    <XAxis
                      dataKey="date"
                      tickFormatter={dateLabel}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: '#667085' }}
                      minTickGap={35}
                    />
                    <YAxis
                      allowDecimals={false}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: '#667085' }}
                      width={25}
                    />
                    <Tooltip
                      contentStyle={chartStyle}
                      labelFormatter={(label) => dateLabel(String(label ?? ''))}
                    />
                    <Bar
                      isAnimationActive={false}
                      dataKey="generated"
                      name="Generated drafts"
                      fill="#D92D20"
                      radius={[3, 3, 0, 0]}
                    />
                    <Bar
                      isAnimationActive={false}
                      dataKey="approved"
                      name="Approved versions"
                      fill="#FDA29B"
                      radius={[3, 3, 0, 0]}
                    />
                    <Bar
                      isAnimationActive={false}
                      dataKey="rejected"
                      name="Rejected versions"
                      fill="#7A271A"
                      radius={[3, 3, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <SmallEmpty text="Draft generation and review decisions will appear here." />
              )}
              <div className="chart-footnote">
                <span>Version decisions · {data.range.timezone}</span>
                <Link to="/outreach">
                  Open studio
                  <ChevronRight size={12} />
                </Link>
              </div>
            </div>
          </section>
          <div className="dashboard-bottom">
            <section className="card pipeline-card">
              <div className="card-title">
                <div>
                  <div className="eyebrow">CONSISTENT INPUT. BETTER CONTEXT.</div>
                  <h2>Pipeline momentum</h2>
                </div>
                <Link to="/research" aria-label="Open company research" className="icon-link">
                  <ArrowUpRight size={18} />
                </Link>
              </div>
              <p className="help">Prospect additions and completed research runs</p>
              {totals!.prospects || totals!.research_runs ? (
                <ResponsiveContainer width="100%" height={235} minWidth={0}>
                  <ComposedChart
                    data={data.daily}
                    margin={{ top: 25, right: 5, left: -20, bottom: 0 }}
                  >
                    <CartesianGrid vertical={false} stroke="#F2F4F7" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={dateLabel}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: '#667085' }}
                      minTickGap={45}
                    />
                    <YAxis
                      allowDecimals={false}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: '#667085' }}
                    />
                    <Tooltip
                      contentStyle={chartStyle}
                      labelFormatter={(label) => dateLabel(String(label ?? ''))}
                    />
                    <Legend
                      iconType="circle"
                      iconSize={6}
                      wrapperStyle={{ fontSize: 10, paddingTop: 15 }}
                    />
                    <Bar
                      isAnimationActive={false}
                      dataKey="prospects"
                      name="Prospects added"
                      fill="#FDA29B"
                      radius={[3, 3, 0, 0]}
                      maxBarSize={15}
                    />
                    <Line
                      isAnimationActive={false}
                      dataKey="research"
                      name="Completed research"
                      stroke="#D92D20"
                      strokeWidth={2}
                      dot={{ r: 2.5, fill: '#fff', strokeWidth: 1.5 }}
                      activeDot={{ r: 5 }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              ) : (
                <SmallEmpty text="Add prospects and complete research to see your pipeline take shape." />
              )}
              <div className="pipeline-summary">
                <div>
                  <span>Qualified prospects</span>
                  <strong>{totals!.qualified}</strong>
                  <small>
                    {data.qualification_pct === null
                      ? 'No prospect cohort yet'
                      : `${data.qualification_pct}% of period prospects`}
                  </small>
                </div>
                <div>
                  <span>Research completed</span>
                  <strong>{totals!.research_runs}</strong>
                  <small>Runs finished in this period</small>
                </div>
                <div>
                  <span>Unqualified</span>
                  <strong>{totals!.unqualified}</strong>
                  <small>Current prospect status</small>
                </div>
              </div>
              <div className="industry-block">
                <div className="card-title">
                  <h3>Company industries</h3>
                  <span className="help">Distinct companies</span>
                </div>
                {data.industries.length ? (
                  <div className="industry-list">
                    {data.industries.map((industry, i) => (
                      <div key={industry.name}>
                        <span>
                          <i style={{ background: colors[i % colors.length] }} />
                          {industry.name}
                        </span>
                        <strong>{industry.value}</strong>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="help">Industry distribution appears when companies are added.</p>
                )}
              </div>
            </section>
            <div className="dashboard-right-stack">
              <div className="review-stat-row">
                <Link to="/approvals" className="review-stat primary">
                  <CheckCheck size={17} />
                  <span>Pending review</span>
                  <strong data-testid="pending-approvals">{totals!.pending}</strong>
                  <ArrowUpRight size={14} />
                </Link>
                <div className="review-stat">
                  <Clock3 size={17} />
                  <span>Avg. approval time</span>
                  <strong>
                    {data.approval_turnaround_minutes === null
                      ? '—'
                      : data.approval_turnaround_minutes < 1
                        ? '<1m'
                        : `${Math.round(data.approval_turnaround_minutes)}m`}
                  </strong>
                  <small>
                    {data.approval_turnaround_minutes === null
                      ? 'Awaiting decisions'
                      : 'Per approved version'}
                  </small>
                </div>
              </div>
              <section className="card status-card">
                <div className="card-title">
                  <h2>Prospect status</h2>
                  <Users size={16} className="text-primary" />
                </div>
                {data.statuses.length ? (
                  <div className="status-distribution">
                    <ResponsiveContainer width={110} height={110}>
                      <PieChart>
                        <Pie
                          isAnimationActive={false}
                          data={data.statuses}
                          dataKey="value"
                          innerRadius={36}
                          outerRadius={50}
                          paddingAngle={3}
                          stroke="none"
                        >
                          {data.statuses.map((s, i) => (
                            <Cell key={s.name} fill={colors[i % colors.length]} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={chartStyle} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="status-legend">
                      {data.statuses.map((s, i) => (
                        <div key={s.name}>
                          <span>
                            <i style={{ background: colors[i % colors.length] }} />
                            {s.name}
                          </span>
                          <strong>{s.value}</strong>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="help mt-4 mb-3">
                    No prospects in this period. Your real status distribution will appear here.
                  </p>
                )}
                <div className="status-footer">
                  <span>
                    <FileText size={12} />
                    {totals!.approved} approved drafts
                  </span>
                  <span>{totals!.rejected} rejected</span>
                </div>
              </section>
              <section className="card dashboard-activity">
                <div className="card-title">
                  <h2>Recent activity</h2>
                  <Link to="/activity" className="view-all">
                    View all
                    <ArrowRight size={12} />
                  </Link>
                </div>
                {data.recent_activity.length ? (
                  data.recent_activity.map((event) => (
                    <Link key={event.id} to={activityLink(event)} className="compact-event">
                      <span className="event-icon">
                        <Activity size={13} />
                      </span>
                      <div>
                        <strong>{eventLabel(event.event_type)}</strong>
                        <small>
                          {new Date(event.created_at).toLocaleString(undefined, {
                            month: 'short',
                            day: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit',
                          })}
                        </small>
                      </div>
                      <ChevronRight size={12} />
                    </Link>
                  ))
                ) : (
                  <div className="activity-empty">
                    <Activity size={23} />
                    <p>No activity recorded in this period.</p>
                    <Link to="/prospects">
                      Start with a prospect
                      <ArrowUpRight size={12} />
                    </Link>
                  </div>
                )}
              </section>
            </div>
          </div>
          <div className="data-caption">
            <span className="connection online">
              <span />
              Connected to live workspace data
            </span>
            <span>
              {dateLabel(data.range.start)} – {dateLabel(data.range.end)} · Counts follow the
              selected period
            </span>
          </div>
        </>
      )}
    </>
  )
}
