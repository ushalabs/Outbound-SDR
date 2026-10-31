import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Page, Prospect } from '@/lib/types'
export function ProspectPicker({
  value,
  onChange,
}: {
  value: string
  onChange: (id: string) => void
}) {
  const [search, setSearch] = useState('')
  const query = useQuery({
    queryKey: ['prospect-picker', search],
    queryFn: () =>
      api<Page<Prospect>>(`/prospects?page_size=100&search=${encodeURIComponent(search)}`),
  })
  const current = useQuery({
    queryKey: ['prospect', value],
    queryFn: () => api<Prospect>(`/prospects/${value}`),
    enabled: !!value,
  })
  const choices = [...(query.data?.items ?? [])]
  if (current.data && !choices.some((p) => p.id === value)) choices.unshift(current.data)
  return (
    <div className="picker">
      <label>
        Find a prospect
        <input
          placeholder="Search your prospects…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </label>
      <label>
        Select prospect
        <select value={value} onChange={(e) => onChange(e.target.value)}>
          <option value="">Choose a prospect</option>
          {choices.map((p) => (
            <option key={p.id} value={p.id}>
              {p.company.name}
              {p.full_name ? ` · ${p.full_name}` : ''}
            </option>
          ))}
        </select>
      </label>
      {query.error && <p className="field-error">{query.error.message}</p>}
      {query.data?.total === 0 && (
        <p className="help">No prospects found. Add or import a prospect first.</p>
      )}
    </div>
  )
}
