import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { ArrowUpRight, FileText, RefreshCw, Save } from 'lucide-react'
import { api } from '@/lib/api'
import type { Draft, Page, Research } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { EmptyState, ErrorState, Loading } from '@/components/states'
import { ProspectPicker } from '@/components/prospect-picker'
import { Badge } from '@/components/common'

export function DraftEditor({
  draft,
  saved,
  children,
}: {
  draft: Draft
  saved: (draft: Draft) => void
  children?: React.ReactNode | ((blocked: boolean) => React.ReactNode)
}) {
  const current = draft.versions.find((v) => v.version === draft.current_version)!
  const [number, setNumber] = useState(draft.current_version),
    [subject, setSubject] = useState(current.subject),
    [body, setBody] = useState(current.body)
  const [preview, setPreview] = useState(false)
  const version = draft.versions.find((v) => v.version === number)!
  const historical = number !== draft.current_version
  const dirty = subject !== current.subject || body !== current.body
  const mutation = useMutation({
    mutationFn: () =>
      api<Draft>(`/outreach/${draft.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ subject, body, expected_version: draft.current_version }),
      }),
    onSuccess: saved,
  })
  const references = (version.context.references ?? []) as { source_id: string; quote: string }[]
  const retrieval = (version.context.retrieval ?? []) as {
    source_id: string
    source_title: string
    source_url: string | null
    source_kind: string
  }[]
  function switchVersion(value: number) {
    const v = draft.versions.find((item) => item.version === value)!
    setNumber(value)
    setSubject(v.subject)
    setBody(v.body)
  }
  return (
    <>
      <div className="card-title">
        <div>
          <h2>Email draft</h2>
          <p className="help">
            {draft.company_name}
            {draft.contact_name ? ` · ${draft.contact_name}` : ''}
          </p>
          {historical && <p className="help">Previous version · read only</p>}
        </div>
        <Badge value={draft.status} />
      </div>
      <div className="editor-toolbar">
        <select
          aria-label="Draft version"
          value={number}
          onChange={(e) => switchVersion(Number(e.target.value))}
        >
          {draft.versions.map((v) => (
            <option key={v.id} value={v.version}>
              Version {v.version}
              {v.version === draft.current_version ? ' · current' : ''}
            </option>
          ))}
        </select>
        <div className="segmented">
          <button className={!preview ? 'selected' : ''} onClick={() => setPreview(false)}>
            Edit
          </button>
          <button className={preview ? 'selected' : ''} onClick={() => setPreview(true)}>
            Preview
          </button>
        </div>
      </div>
      {preview ? (
        <div className="email-preview">
          <small>Subject</small>
          <h3>{subject}</h3>
          <div className="section-divider" />
          <p>{body}</p>
        </div>
      ) : (
        <div className="email-editor">
          <label>
            Subject
            <input
              aria-label="Subject"
              value={subject}
              maxLength={300}
              disabled={historical || draft.status === 'archived'}
              onChange={(e) => setSubject(e.target.value)}
            />
          </label>
          <label>
            Email body
            <textarea
              aria-label="Email body"
              rows={13}
              value={body}
              maxLength={10000}
              disabled={historical || draft.status === 'archived'}
              onChange={(e) => setBody(e.target.value)}
            />
          </label>
        </div>
      )}
      {mutation.error && (
        <p role="alert" className="field-error">
          {mutation.error.message}
        </p>
      )}
      <div className="editor-actions">
        <span className="help">
          {dirty && !historical
            ? 'Unsaved edits · save before reviewing'
            : `Saved version ${number}`}{' '}
          · Email sending disabled
        </span>
        <Button
          disabled={
            historical ||
            !dirty ||
            !subject.trim() ||
            !body.trim() ||
            mutation.isPending ||
            draft.status === 'archived'
          }
          onClick={() => mutation.mutate()}
        >
          <Save size={14} />
          {mutation.isPending ? 'Saving…' : 'Save new version'}
        </Button>
      </div>
      {references.length > 0 && (
        <div className="provenance">
          <h3>Sources used</h3>
          {references.map((ref, i) => {
            const source = retrieval.find((r) => r.source_id === ref.source_id)
            return (
              <div key={i} className="citation">
                “{ref.quote}”
                {source?.source_url ? (
                  <a
                    className="source-link block mt-1"
                    href={source.source_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {source.source_title} ↗
                  </a>
                ) : (
                  <span className="help block mt-1">User-provided evidence</span>
                )}
              </div>
            )
          })}
        </div>
      )}
      {typeof children === 'function' ? children(historical || dirty) : children}
    </>
  )
}

interface Sender {
  name: string
  company: string
  value_proposition: string
}
export default function OutreachPage() {
  const [params, setParams] = useSearchParams(),
    client = useQueryClient()
  const prospect = params.get('prospect') || '',
    [draftId, setDraftId] = useState(params.get('draft') || '')
  const [tone, setTone] = useState('professional'),
    [sender, setSender] = useState<Sender>(() => {
      try {
        const saved = JSON.parse(localStorage.getItem('outbound-sender') || '{}')
        return {
          name: saved.name || '',
          company: saved.company || '',
          value_proposition: saved.value_proposition || '',
        }
      } catch {
        return { name: '', company: '', value_proposition: '' }
      }
    })
  const list = useQuery({
    queryKey: ['drafts', prospect],
    queryFn: () => api<Page<Draft>>(`/outreach${prospect ? `?prospect_id=${prospect}` : ''}`),
  })
  const detail = useQuery({
    queryKey: ['draft', draftId],
    queryFn: () => api<Draft>(`/outreach/${draftId}`),
    enabled: !!draftId,
  })
  const research = useQuery({
    queryKey: ['research-preview', prospect],
    queryFn: () => api<Page<Research>>(`/research?prospect_id=${prospect}&page_size=100`),
    enabled: !!prospect,
  })
  const valid =
    !!prospect &&
    sender.name.trim() &&
    sender.company.trim() &&
    sender.value_proposition.trim().length >= 10
  function saved(draft: Draft) {
    setDraftId(draft.id)
    client.setQueryData(['draft', draft.id], draft)
    void client.invalidateQueries()
    localStorage.setItem('outbound-sender', JSON.stringify(sender))
  }
  const generate = useMutation({
    mutationFn: () =>
      api<Draft>('/outreach/generate', {
        method: 'POST',
        body: JSON.stringify({ prospect_id: prospect, tone, sender }),
      }),
    onSuccess: saved,
  })
  const regenerate = useMutation({
    mutationFn: () =>
      api<Draft>(`/outreach/${draftId}/regenerate`, {
        method: 'POST',
        body: JSON.stringify({ prospect_id: detail.data?.prospect_id, tone, sender }),
      }),
    onSuccess: saved,
  })
  const latest = research.data?.items.find((r) => r.status === 'completed')
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Outreach</h1>
        </div>
        <Button asChild variant="outline">
          <Link to="/approvals">
            Review queue
            <ArrowUpRight size={15} />
          </Link>
        </Button>
      </div>
      <div className="workspace-grid">
        <aside className="card workspace-controls">
          <h2>New email</h2>
          <ProspectPicker
            value={prospect}
            onChange={(id) => {
              setParams(id ? { prospect: id } : {})
              setDraftId('')
            }}
          />
          <label className="block mt-4">
            Tone
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              <option value="professional">Professional</option>
              <option value="concise">Concise</option>
              <option value="friendly">Friendly</option>
            </select>
          </label>
          <div className="section-divider" />
          <h3>Your business</h3>
          <p className="help">Describe the service you want to offer this prospect</p>
          {(
            [
              ['name', 'Your name'],
              ['company', 'Your company'],
            ] as const
          ).map(([field, label]) => (
            <label key={field} className="block mt-3">
              {label}
              <input
                value={sender[field]}
                maxLength={200}
                onChange={(e) => setSender({ ...sender, [field]: e.target.value })}
              />
            </label>
          ))}
          <label className="block mt-3">
            Your value proposition
            <textarea
              rows={4}
              value={sender.value_proposition}
              maxLength={2000}
              onChange={(e) => setSender({ ...sender, value_proposition: e.target.value })}
              placeholder="What service do you offer, and who is it for?"
            />
          </label>
          <Button
            className="w-full mt-4"
            disabled={!valid || generate.isPending}
            onClick={() => generate.mutate()}
          >
            <FileText size={14} />
            {generate.isPending ? 'Writing email…' : 'Write email'}
          </Button>
          {generate.error && (
            <p className="field-error" role="alert">
              {generate.error.message}
            </p>
          )}
          {prospect && (
            <div className="source-card">
              <h3>Research readiness</h3>
              {latest ? (
                <>
                  <Badge value="completed" />
                  <p className="help mt-2">
                    {new Date(latest.created_at).toLocaleString()} · {latest.model}
                  </p>
                </>
              ) : (
                <p className="help">Complete research and embeddings before drafting.</p>
              )}
              <Link className="source-link mt-2" to={`/research?prospect=${prospect}`}>
                Inspect research & embeddings ↗
              </Link>
            </div>
          )}
          <div className="section-divider" />
          <div className="card-title">
            <h3>Saved drafts</h3>
            <span className="help">{list.data?.total ?? '—'}</span>
          </div>
          {list.isPending ? (
            <Loading />
          ) : list.error ? (
            <ErrorState error={list.error} />
          ) : list.data.items.length === 0 ? (
            <p className="help">No saved drafts yet.</p>
          ) : (
            <div className="history-list">
              {list.data.items.map((draft) => (
                <button
                  key={draft.id}
                  className={`history-item ${draftId === draft.id ? 'selected' : ''}`}
                  onClick={() => setDraftId(draft.id)}
                >
                  <span>
                    {draft.versions[0]?.subject || 'Draft'}
                    <small>
                      v{draft.current_version} · {new Date(draft.updated_at).toLocaleDateString()}
                    </small>
                  </span>
                  <Badge value={draft.status} />
                </button>
              ))}
            </div>
          )}
        </aside>
        <section className="card workspace-main">
          {generate.isPending ? (
            <div className="state" role="status">
              <FileText />
              <h3>Writing email…</h3>
            </div>
          ) : !draftId ? (
            <EmptyState
              title="No draft selected"
              description="Choose a prospect and describe your offer to write an introductory email."
            />
          ) : detail.isPending ? (
            <Loading />
          ) : detail.error ? (
            <ErrorState error={detail.error} retry={() => void detail.refetch()} />
          ) : (
            detail.data && (
              <DraftEditor
                key={`${detail.data.id}-${detail.data.current_version}`}
                draft={detail.data}
                saved={saved}
              >
                <div className="dialog-actions">
                  <Button
                    variant="outline"
                    disabled={
                      !sender.name ||
                      !sender.company ||
                      sender.value_proposition.length < 10 ||
                      regenerate.isPending ||
                      detail.data.status === 'archived'
                    }
                    onClick={() => regenerate.mutate()}
                  >
                    <RefreshCw size={14} />
                    {regenerate.isPending ? 'Regenerating…' : 'Regenerate new version'}
                  </Button>
                  <Button asChild>
                    <Link to={`/approvals?draft=${draftId}`}>
                      <FileText size={14} />
                      Open for review
                    </Link>
                  </Button>
                </div>
                {regenerate.error && (
                  <p className="field-error" role="alert">
                    {regenerate.error.message}
                  </p>
                )}
              </DraftEditor>
            )
          )}
        </section>
      </div>
    </>
  )
}
