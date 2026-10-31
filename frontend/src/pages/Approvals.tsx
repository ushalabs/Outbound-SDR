import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { Archive, Check, Copy, Download, RefreshCw, RotateCcw, Search, X } from 'lucide-react'
import { api } from '@/lib/api'
import type { Draft, Page, Research } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { EmptyState, ErrorState, Loading } from '@/components/states'
import { Badge, Modal } from '@/components/common'
import { DraftEditor } from './Outreach'
import { ResearchContent, ResearchEvidence } from './Research'

export default function ApprovalsPage() {
  const [params] = useSearchParams(),
    client = useQueryClient()
  const [id, setId] = useState(params.get('draft') || ''),
    [status, setStatus] = useState('pending'),
    [search, setSearch] = useState(''),
    [page, setPage] = useState(1),
    [note, setNote] = useState(''),
    [message, setMessage] = useState(''),
    [confirm, setConfirm] = useState<string>()
  const counts = useQuery({
    queryKey: ['approval-counts'],
    queryFn: () => api<Record<string, number>>('/approvals/counts'),
    refetchInterval: 15000,
  })
  const query = useQuery({
    queryKey: ['approval-queue', status, search, page],
    queryFn: () =>
      api<Page<Draft>>(
        `/approvals?status=${status}&search=${encodeURIComponent(search)}&page=${page}`,
      ),
  })
  const detail = useQuery({
    queryKey: ['draft', id],
    queryFn: () => api<Draft>(`/outreach/${id}`),
    enabled: !!id,
  })
  const research = useQuery({
    queryKey: ['review-research', detail.data?.research_id],
    queryFn: () => api<Research>(`/research/${detail.data!.research_id}`),
    enabled: !!detail.data?.research_id,
  })
  function saved(draft: Draft) {
    client.setQueryData(['draft', draft.id], draft)
    void client.invalidateQueries()
    setConfirm(undefined)
    setNote('')
    setMessage('Review changes saved.')
  }
  const action = useMutation({
    mutationFn: (name: string) =>
      api<Draft>(`/approvals/${id}/action`, {
        method: 'POST',
        body: JSON.stringify({
          action: name,
          expected_version: detail.data?.current_version,
          note: note || null,
        }),
      }),
    onSuccess: saved,
  })
  const regenerate = useMutation({
    mutationFn: () =>
      api<Draft>(`/outreach/${id}/regenerate`, {
        method: 'POST',
        body: JSON.stringify({
          prospect_id: detail.data?.prospect_id,
          tone: detail.data?.tone,
          sender: detail.data?.sender_context,
        }),
      }),
    onSuccess: saved,
  })
  const exporter = useMutation({
    mutationFn: (copy: boolean) =>
      api<{ subject: string; body: string; version: number }>(`/approvals/${id}/export`).then(
        async (data) => {
          if (copy) {
            await navigator.clipboard.writeText(`Subject: ${data.subject}\n\n${data.body}`)
            setMessage('Approved draft copied. No email was sent.')
          } else {
            const url = URL.createObjectURL(
              new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }),
            )
            const a = document.createElement('a')
            a.href = url
            a.download = `approved-draft-${id}-v${data.version}.json`
            a.click()
            URL.revokeObjectURL(url)
            setMessage('Approved draft exported. No email was sent.')
          }
          void client.invalidateQueries({ queryKey: ['activity'] })
        },
      ),
  })
  const busy = action.isPending || regenerate.isPending
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">HUMAN JUDGMENT, EVERY TIME</div>
          <h1>Approval queue</h1>
          <p>Review the evidence. Approve a version. Keep the full history.</p>
        </div>
        <span className="subtle-chip">{counts.data?.pending ?? '—'} awaiting review</span>
      </div>
      {message && (
        <div className="notice success" role="status">
          {message}
          <button onClick={() => setMessage('')} aria-label="Dismiss message">
            <X size={14} />
          </button>
        </div>
      )}
      <div className="review-layout">
        <aside className="card review-queue">
          <label className="search-input block mb-4">
            <Search size={15} />
            <input
              aria-label="Search approval queue"
              placeholder="Search company or contact…"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
            />
          </label>
          <select
            aria-label="Filter approval status"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value)
              setPage(1)
            }}
          >
            {['pending', 'approved', 'rejected', 'archived'].map((s) => (
              <option key={s} value={s}>
                {s} ({counts.data?.[s] ?? '—'})
              </option>
            ))}
          </select>
          <div className="section-divider" />
          {query.isPending ? (
            <Loading />
          ) : query.error ? (
            <ErrorState error={query.error} retry={() => void query.refetch()} />
          ) : query.data.items.length === 0 ? (
            <EmptyState
              title="Queue is clear"
              description="No drafts match this status and search."
            />
          ) : (
            <div className="history-list">
              {query.data.items.map((d) => (
                <button
                  key={d.id}
                  className={`history-item ${id === d.id ? 'selected' : ''}`}
                  onClick={() => {
                    setId(d.id)
                    setNote('')
                    action.reset()
                    regenerate.reset()
                  }}
                >
                  <span>
                    <strong>{d.company_name}</strong>
                    <small>{d.versions[0]?.subject}</small>
                    <small>Version {d.current_version}</small>
                  </span>
                  <Badge value={d.status} />
                </button>
              ))}
            </div>
          )}
          <div className="queue-pagination">
            <Button
              size="sm"
              variant="ghost"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </Button>
            <span>{page}</span>
            <Button
              size="sm"
              variant="ghost"
              disabled={!query.data || page * 20 >= query.data.total}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </div>
        </aside>
        <div className="workspace-main">
          {!id ? (
            <section className="card">
              <EmptyState
                title="Ready for a second look"
                description="Choose a draft to review its wording, source evidence and version history."
                to="/outreach"
                action="Open outreach studio"
              />
            </section>
          ) : detail.isPending ? (
            <section className="card">
              <Loading />
            </section>
          ) : detail.error ? (
            <section className="card">
              <ErrorState error={detail.error} />
            </section>
          ) : (
            detail.data && (
              <>
                <section className="card">
                  <DraftEditor
                    key={`${id}-${detail.data.current_version}`}
                    draft={detail.data}
                    saved={saved}
                  >
                    {(blocked) => (
                      <>
                        <label className="block mt-4">
                          Reviewer note (optional)
                          <textarea
                            aria-label="Reviewer note"
                            rows={2}
                            value={note}
                            maxLength={2000}
                            onChange={(e) => setNote(e.target.value)}
                          />
                        </label>
                        {blocked && (
                          <p className="help mt-3">
                            Return to the current version and save edits before review actions.
                          </p>
                        )}
                        <div className="review-actions">
                          {detail.data.status === 'pending' && (
                            <>
                              <Button
                                disabled={blocked || busy}
                                onClick={() => setConfirm('approve')}
                              >
                                <Check size={14} />
                                Approve version {detail.data.current_version}
                              </Button>
                              <Button
                                variant="outline"
                                disabled={blocked || busy}
                                onClick={() => setConfirm('reject')}
                              >
                                <X size={14} />
                                Reject
                              </Button>
                            </>
                          )}
                          {detail.data.status === 'rejected' && (
                            <Button
                              disabled={blocked || busy}
                              onClick={() => action.mutate('reopen')}
                            >
                              <RotateCcw size={14} />
                              Reopen as new version
                            </Button>
                          )}
                          {detail.data.status !== 'archived' && (
                            <>
                              <Button
                                variant="outline"
                                disabled={blocked || busy}
                                onClick={() => regenerate.mutate()}
                              >
                                <RefreshCw size={14} />
                                {regenerate.isPending ? 'Regenerating…' : 'Regenerate'}
                              </Button>
                              <Button
                                variant="ghost"
                                disabled={blocked || busy}
                                onClick={() => setConfirm('archive')}
                              >
                                <Archive size={14} />
                                Archive
                              </Button>
                            </>
                          )}
                          {detail.data.status === 'approved' && (
                            <>
                              <Button
                                variant="outline"
                                disabled={blocked || exporter.isPending}
                                onClick={() => exporter.mutate(true)}
                              >
                                <Copy size={14} />
                                Copy approved
                              </Button>
                              <Button
                                variant="outline"
                                disabled={blocked || exporter.isPending}
                                onClick={() => exporter.mutate(false)}
                              >
                                <Download size={14} />
                                Export draft
                              </Button>
                            </>
                          )}
                        </div>
                        {(action.error || regenerate.error || exporter.error) && (
                          <p role="alert" className="field-error">
                            {(action.error || regenerate.error || exporter.error)?.message}
                          </p>
                        )}
                      </>
                    )}
                  </DraftEditor>
                </section>
                <section className="card mt-5">
                  <h2>Approval history</h2>
                  <div className="audit-timeline">
                    {detail.data.events.map((event) => (
                      <div className="audit-event" key={event.id}>
                        <span className="timeline-dot" />
                        <div>
                          <strong>
                            {event.action.replaceAll('_', ' ')} · version{' '}
                            {detail.data.versions.find((v) => v.id === event.version_id)?.version ??
                              '?'}
                          </strong>
                          <small>{new Date(event.created_at).toLocaleString()}</small>
                          {event.note && <p>{event.note}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
                {research.data && (
                  <section className="card mt-5">
                    <details>
                      <summary>Review supporting research & evidence</summary>
                      <ResearchContent research={research.data} />
                      <ResearchEvidence sources={research.data.sources ?? []} />
                    </details>
                  </section>
                )}
                {research.error && (
                  <section className="card mt-5">
                    <ErrorState error={research.error} />
                  </section>
                )}
              </>
            )
          )}
        </div>
      </div>
      {confirm && detail.data && (
        <Modal
          title={`${confirm[0].toUpperCase() + confirm.slice(1)} draft version ${detail.data.current_version}?`}
          close={() => setConfirm(undefined)}
        >
          <p className="help">
            This records your decision for the saved version. Approval prepares a draft for copying
            or export. It never sends an email.
          </p>
          {note && <p className="body-copy">Note: {note}</p>}
          <div className="dialog-actions">
            <Button variant="outline" onClick={() => setConfirm(undefined)}>
              Cancel
            </Button>
            <Button disabled={action.isPending} onClick={() => action.mutate(confirm)}>
              {action.isPending ? 'Saving…' : `Confirm ${confirm}`}
            </Button>
          </div>
          {action.error && <p className="field-error">{action.error.message}</p>}
        </Modal>
      )}
    </>
  )
}
