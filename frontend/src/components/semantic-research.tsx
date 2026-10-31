import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Database, ExternalLink, Search } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from './ui/button'
interface Match {
  chunk_id: string
  text: string
  source_url: string | null
  source_kind: string
  source_title: string
  company_name: string
  similarity: number
}
export function SemanticResearch({
  researchId,
  prospectId,
}: {
  researchId: string
  prospectId: string | null
}) {
  const [query, setQuery] = useState('')
  const client = useQueryClient()
  const state = useQuery({
    queryKey: ['embeddings', researchId],
    queryFn: () =>
      api<{
        total: number
        completed: number
        failed: number
        stale: number
        errors: string[]
        models: string[]
      }>(`/research/${researchId}/embeddings`),
  })
  const embed = useMutation({
    mutationFn: () => api(`/research/${researchId}/embeddings`, { method: 'POST' }),
    onSuccess: () => void client.invalidateQueries({ queryKey: ['embeddings', researchId] }),
    onError: () => void client.invalidateQueries({ queryKey: ['embeddings', researchId] }),
  })
  const search = useMutation({
    mutationFn: () =>
      api<{ items: Match[]; message: string | null }>('/semantic/search', {
        method: 'POST',
        body: JSON.stringify({ query, prospect_id: prospectId }),
      }),
  })
  return (
    <section className="card mt-5">
      <div className="card-title">
        <h2>Semantic evidence search</h2>
        <Database size={17} className="text-primary" />
      </div>
      <p className="help">
        Find relevant passages from the latest company research using real Gemini embeddings and
        pgvector cosine similarity.
      </p>
      <div className="embedding-controls">
        <span className="help">
          {state.data
            ? `${state.data.completed} / ${state.data.total} chunks embedded${state.data.failed ? ` · ${state.data.failed} failed` : ''}${state.data.stale ? ` · ${state.data.stale} stale` : ''}`
            : state.error
              ? state.error.message
              : 'Loading embedding status…'}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={embed.isPending}
          onClick={() => embed.mutate()}
        >
          {embed.isPending
            ? 'Generating embeddings…'
            : state.data?.completed
              ? 'Re-embed research'
              : 'Generate embeddings'}
        </Button>
      </div>
      {state.data?.errors.map((e) => (
        <p className="field-error" key={e}>
          {e}
        </p>
      ))}
      {embed.error && (
        <p role="alert" className="field-error">
          {embed.error.message}
        </p>
      )}
      <form
        className="semantic-form"
        onSubmit={(e) => {
          e.preventDefault()
          search.mutate()
        }}
      >
        <input
          aria-label="Semantic research query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What does this company focus on?"
          minLength={3}
          maxLength={1000}
          required
        />
        <Button disabled={search.isPending || query.trim().length < 3}>
          <Search size={14} />
          {search.isPending ? 'Searching…' : 'Search evidence'}
        </Button>
      </form>
      {search.error && (
        <p role="alert" className="field-error">
          {search.error.message}
        </p>
      )}
      {search.data?.message && <p className="help mt-4">{search.data.message}</p>}
      {search.data?.items.map((match) => (
        <div className="source-card" key={match.chunk_id}>
          <div className="card-title">
            <h3>{match.company_name}</h3>
            <span className="help">Cosine similarity {match.similarity.toFixed(3)}</span>
          </div>
          <p className="evidence">{match.text}</p>
          {match.source_url ? (
            <a className="source-link" href={match.source_url} target="_blank" rel="noreferrer">
              {match.source_title}
              <ExternalLink size={12} />
            </a>
          ) : (
            <span className="help">User-provided notes</span>
          )}
        </div>
      ))}
      {!!search.data?.items.length && prospectId && (
        <Button asChild className="mt-4" variant="outline">
          <Link to={`/outreach?prospect=${prospectId}`}>Compose with this company context</Link>
        </Button>
      )}
    </section>
  )
}
