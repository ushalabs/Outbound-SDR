import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  CalendarDays,
  CheckCheck,
  ChevronRight,
  Clock3,
  FileText,
  Plus,
  Users,
} from 'lucide-react'
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
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

const chartStyle = {
  background: '#242426',
  color: '#f5f5f5',
  border: '1px solid #ffffff14',
  borderRadius: 12,
  fontSize: 12,
}
const statusColors = ['#baed45', '#9b6df4', '#6b4d97', '#99999f', '#57575d']
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
function DailyBars({
  daily,
  field,
}: {
  daily: Day[]
  field: 'research' | 'generated' | 'approved'
}) {
  const days = daily.slice(-30)
  const max = Math.max(1, ...days.map((d) => d[field]))
  return (
    <div
      className={`daily-bars bars-${field}`}
      role="img"
      aria-label={`${field} daily counts: ${days.map((d) => `${d.date}: ${d[field]}`).join(', ')}`}
    >
      {days.map((d) => (
        <span key={d.date} title={`${dateLabel(d.date)}: ${d[field]}`}>
          <i style={{ height: `${(d[field] / max) * 100}%` }} />
        </span>
      ))}
    </div>
  )
}
function DraftCalendar({ daily }: { daily: Day[] }) {
  const days = daily.slice(-35)
  const start = days.length ? new Date(`${days[0].date}T12:00:00`).getDay() : 0
  const max = Math.max(1, ...days.map((d) => d.generated))
  return (
    <>
      <div className="calendar-weekdays">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
          <span key={day}>{day}</span>
        ))}
      </div>
      <div className="draft-calendar" aria-label="Drafts generated per day">
        {Array.from({ length: start }, (_, i) => (
          <span className="calendar-spacer" key={`pad-${i}`} />
        ))}
        {days.map((d) => (
          <div
            key={d.date}
            tabIndex={0}
            className={`calendar-cell ${d.generated ? 'has-drafts' : ''}`}
            style={{
              background: d.generated
                ? `rgba(153, 96, 255, ${0.35 + (d.generated / max) * 0.65})`
                : undefined,
            }}
            title={`${dateLabel(d.date)} · ${d.generated} drafts generated · ${d.approved} approved decisions · ${d.rejected} rejected decisions`}
            aria-label={`${dateLabel(d.date)}: ${d.generated} drafts generated`}
          />
        ))}
      </div>
      <div className="calendar-legend">
        <span>
          {days.length
            ? `${dateLabel(days[0].date)} – ${dateLabel(days[days.length - 1].date)}`
            : 'No days in range'}
        </span>
        <span>
          Less <i />
          <i />
          <i />
          <i /> More
        </span>
      </div>
    </>
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
  const data = query.data
  const totals = data?.totals
  return (
    <>
      <div className="page-heading dashboard-heading">
        <div>
          <h1>Overview</h1>
        </div>
        <div className="period-controls" role="group" aria-label="Dashboard date range">
          {(
            [
              ['7', 'Week'],
              ['30', 'Month'],
              ['90', 'Quarter'],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value}
              className={period === value ? 'selected' : ''}
              aria-label={`Last ${value} days`}
              aria-pressed={period === value}
              onClick={() => setPeriod(value)}
            >
              {label}
            </button>
          ))}
          <button
            className={period === 'custom' ? 'selected' : ''}
            aria-label="Custom range"
            aria-pressed={period === 'custom'}
            onClick={() => setPeriod('custom')}
          >
            <CalendarDays />
          </button>
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
      ) : !data || !totals ? (
        <div className="dashboard-skeleton" role="status" aria-label="Loading dashboard">
          <div />
          <div />
          <div />
        </div>
      ) : (
        <>
          <section className="metrics-overview" aria-label="Pipeline summary">
            <div className="primary-metric">
              <div className="metric-label">
                Total prospects <span className="period-caption">{data.range.days} days</span>
              </div>
              <div className="primary-number">
                <strong data-testid="total-prospects">{totals.prospects.toLocaleString()}</strong>
              </div>
              <div className="growth-caption">
                {data.prospect_growth_pct === null ? (
                  'No prior-period baseline'
                ) : (
                  <>
                    {data.prospect_growth_pct >= 0 ? <ArrowUpRight /> : <ArrowDownRight />}{' '}
                    {Math.abs(data.prospect_growth_pct)}% vs previous {data.range.days} days
                  </>
                )}
              </div>
              <div className="metric-actions">
                <Button asChild>
                  <Link to="/prospects">
                    Add prospects <Plus />
                  </Link>
                </Button>
                <Button variant="outline" asChild>
                  <Link to="/research">
                    Research <ArrowUpRight />
                  </Link>
                </Button>
              </div>
            </div>
            <div className="summary-metric">
              <span className="metric-label">Research completed</span>
              <strong>{totals.research_runs.toLocaleString()}</strong>
              <span className="metric-detail">
                <i className="series-dot violet" /> {totals.researched} prospects researched
              </span>
              <DailyBars daily={data.daily} field="research" />
            </div>
            <div className="summary-metric">
              <span className="metric-label">Drafts generated</span>
              <strong>{totals.generated.toLocaleString()}</strong>
              <DailyBars daily={data.daily} field="generated" />
            </div>
            <div className="summary-metric">
              <span className="metric-label">Approved drafts</span>
              <strong>{totals.approved.toLocaleString()}</strong>
              <DailyBars daily={data.daily} field="approved" />
            </div>
          </section>
          <div className="dashboard-panels">
            <section className="card pipeline-card">
              <div className="card-title">
                <h2>
                  <Activity /> Pipeline momentum
                </h2>
                <Link className="round-action" to="/research" aria-label="Open company research">
                  <ArrowUpRight />
                </Link>
              </div>
              <div className="chart-key">
                <span>
                  <i className="series-dot lime" /> Prospects
                </span>
                <span>
                  <i className="series-dot grey" /> Research runs
                </span>
              </div>
              <div className="pipeline-plot">
                <ResponsiveContainer width="100%" height={190} minWidth={0}>
                  <ComposedChart
                    data={data.daily}
                    margin={{ top: 16, right: 8, left: -28, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="prospect-area" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#baed45" stopOpacity={0.24} />
                        <stop offset="100%" stopColor="#baed45" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid vertical={false} stroke="#ffffff09" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={dateLabel}
                      axisLine={false}
                      tickLine={false}
                      minTickGap={38}
                      tick={{ fontSize: 11, fill: '#97979e' }}
                    />
                    <YAxis
                      allowDecimals={false}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 11, fill: '#97979e' }}
                    />
                    <Tooltip
                      contentStyle={chartStyle}
                      labelFormatter={(label) => dateLabel(String(label ?? ''))}
                    />
                    <Area
                      type="monotone"
                      isAnimationActive={false}
                      dataKey="prospects"
                      name="Prospects added"
                      stroke="#baed45"
                      strokeWidth={2}
                      fill="url(#prospect-area)"
                    />
                    <Line
                      type="monotone"
                      isAnimationActive={false}
                      dataKey="research"
                      name="Completed research"
                      stroke="#939399"
                      strokeWidth={1.5}
                      strokeDasharray="4 4"
                      dot={false}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
                {totals.prospects === 0 && totals.research_runs === 0 && (
                  <span className="plot-zero-note">No pipeline activity in this period</span>
                )}
              </div>
              <div className="panel-foot">
                <span>
                  <i className="series-dot lime" /> {totals.qualified} qualified prospects
                </span>
                <Link to="/prospects">
                  View pipeline <ArrowUpRight />
                </Link>
              </div>
            </section>
            <section className="card outreach-calendar-card">
              <div className="card-title">
                <h2>
                  <CalendarDays /> Outreach activity
                </h2>
                <Link className="round-action" to="/outreach" aria-label="Open outreach">
                  <ArrowUpRight />
                </Link>
              </div>
              <DraftCalendar daily={data.daily} />
              <div className="decision-counts">
                <span>
                  <i className="series-dot violet" />
                  {totals.generated} generated
                </span>
                <span>
                  <i className="series-dot lime" />
                  {data.daily.reduce((sum, d) => sum + d.approved, 0)} approved
                </span>
                <span>{data.daily.reduce((sum, d) => sum + d.rejected, 0)} rejected</span>
              </div>
            </section>
            <section className="card dashboard-activity">
              <div className="card-title">
                <h2>
                  <Clock3 /> Recent activity
                </h2>
                <Link className="round-action" to="/activity" aria-label="View all activity">
                  <ArrowUpRight />
                </Link>
              </div>
              {data.recent_activity.length ? (
                <div className="compact-events">
                  {data.recent_activity.slice(0, 5).map((event) => (
                    <Link key={event.id} to={activityLink(event)} className="compact-event">
                      <span className="event-icon">
                        <Activity />
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
                      <ChevronRight />
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="activity-start">
                  <p>No activity in this period</p>
                  {(
                    [
                      ['/prospects', '01', 'Add your prospects'],
                      ['/research', '02', 'Research a company'],
                      ['/outreach', '03', 'Write your first draft'],
                    ] as const
                  ).map(([path, step, label]) => (
                    <Link to={path} key={path}>
                      <b>{step}</b>
                      {label}
                      <ArrowUpRight />
                    </Link>
                  ))}
                </div>
              )}
            </section>
          </div>
          <div className="dashboard-details">
            <section className="card breakdown-card">
              <div className="card-title">
                <h2>
                  <Users /> Prospect breakdown
                </h2>
                <span className="help">Selected period</span>
              </div>
              <div className="breakdown-columns">
                <div>
                  <h3>Prospect status</h3>
                  {data.statuses.length ? (
                    <div className="status-legend">
                      {data.statuses.map((status, i) => (
                        <div key={status.name}>
                          <span>
                            <i
                              className="series-dot"
                              style={{ background: statusColors[i % statusColors.length] }}
                            />
                            {status.name}
                          </span>
                          <strong>{status.value}</strong>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="help">No prospects in this period</p>
                  )}
                </div>
                <div>
                  <h3>Company industries</h3>
                  {data.industries.length ? (
                    <div className="industry-list">
                      {data.industries.map((industry, i) => (
                        <div key={industry.name}>
                          <span>
                            <i
                              className="series-dot"
                              style={{ background: statusColors[i % statusColors.length] }}
                            />
                            {industry.name}
                          </span>
                          <strong>{industry.value}</strong>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="help">Industries appear as you add companies</p>
                  )}
                </div>
                <div className="coverage-detail">
                  <h3>Research coverage</h3>
                  <strong>
                    {data.research_coverage_pct === null ? '—' : `${data.research_coverage_pct}%`}
                  </strong>
                  <div className="progress-track">
                    <span style={{ width: `${data.research_coverage_pct ?? 0}%` }} />
                  </div>
                  <p className="help">
                    {totals.researched} of {totals.prospects} prospects
                  </p>
                  <span className="help">
                    {totals.unqualified} unqualified ·{' '}
                    {data.qualification_pct === null
                      ? 'No qualification baseline'
                      : `${data.qualification_pct}% qualified`}
                  </span>
                </div>
              </div>
            </section>
            <section className="card review-summary">
              <div className="card-title">
                <h2>
                  <CheckCheck /> Ready for review
                </h2>
                <Link className="round-action" to="/approvals" aria-label="Manage approvals">
                  <ArrowUpRight />
                </Link>
              </div>
              <div className="review-summary-body">
                <Link to="/approvals">
                  <strong data-testid="pending-approvals">{totals.pending.toLocaleString()}</strong>
                  <span>drafts awaiting your decision</span>
                </Link>
                <div>
                  <span>Avg. approval time</span>
                  <strong>
                    {data.approval_turnaround_minutes === null
                      ? '—'
                      : data.approval_turnaround_minutes < 1
                        ? '<1m'
                        : `${Math.round(data.approval_turnaround_minutes)}m`}
                  </strong>
                </div>
              </div>
              <div className="panel-foot">
                <span>{totals.approved} approved drafts</span>
                <span>{totals.rejected} rejected</span>
                <FileText />
              </div>
            </section>
          </div>
          <div className="data-caption">
            <span>
              {dateLabel(data.range.start)} – {dateLabel(data.range.end)} · {data.range.timezone}
            </span>
          </div>
        </>
      )}
    </>
  )
}
