import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Activity, ArrowUpRight } from 'lucide-react'
import { api } from '@/lib/api'
import type { ActivityEvent, Page } from '@/lib/types'
import { activityLink, eventLabel } from '@/lib/activity'
import { Button } from '@/components/ui/button'
import { EmptyState, ErrorState, Loading } from '@/components/states'
export default function ActivityPage() {
  const [page, setPage] = useState(1),
    [type, setType] = useState('')
  const query = useQuery({
    queryKey: ['activity', page, type],
    queryFn: () => api<Page<ActivityEvent>>(`/activity?page=${page}&event_type=${type}`),
    refetchInterval: 15000,
  })
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">A RECORD OF REAL WORK</div>
          <h1>Workspace activity</h1>
          <p>Your persisted research, prospect and review history.</p>
        </div>
        <select
          className="activity-filter"
          aria-label="Filter activity"
          value={type}
          onChange={(e) => {
            setType(e.target.value)
            setPage(1)
          }}
        >
          <option value="">All activity</option>
          {[
            'prospect.created',
            'research.completed',
            'research.failed',
            'research.embedded',
            'draft.created',
            'draft.approved',
            'draft.rejected',
            'draft.exported',
            'import.completed',
          ].map((t) => (
            <option value={t} key={t}>
              {eventLabel(t)}
            </option>
          ))}
        </select>
      </div>
      <section className="card">
        {query.isPending ? (
          <Loading />
        ) : query.error ? (
          <ErrorState error={query.error} retry={() => void query.refetch()} />
        ) : !query.data.items.length ? (
          <EmptyState
            title="Your activity will appear here"
            description="Add a prospect, complete research or review a draft to build your workspace history."
            to="/prospects"
            action="Open prospects"
          />
        ) : (
          <div className="activity-list">
            {query.data.items.map((event) => (
              <Link key={event.id} to={activityLink(event)} className="activity-row">
                <span className="activity-icon">
                  <Activity size={16} />
                </span>
                <div>
                  <strong>{eventLabel(event.event_type)}</strong>
                  <p>
                    {event.entity_type === 'draft' && event.details.version
                      ? `Version ${event.details.version} · `
                      : ''}
                    {new Date(event.created_at).toLocaleString()}
                  </p>
                </div>
                <ArrowUpRight size={15} />
              </Link>
            ))}
          </div>
        )}
        <div className="pagination">
          <span>{query.data?.total ?? '—'} recorded events</span>
          <div className="actions">
            <Button
              size="sm"
              variant="outline"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </Button>
            <span>{page}</span>
            <Button
              size="sm"
              variant="outline"
              disabled={!query.data || page * 30 >= query.data.total}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      </section>
    </>
  )
}
