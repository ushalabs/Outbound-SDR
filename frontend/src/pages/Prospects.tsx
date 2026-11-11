import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import {
  ArrowDownUp,
  Building2,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  FileUp,
  Globe,
  Pencil,
  Plus,
  Search,
  Trash2,
  X,
} from 'lucide-react'
import { api } from '@/lib/api'
import { Badge, Modal } from '@/components/common'
import type { Company, Page, Prospect, ProspectStatus } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { EmptyState, ErrorState, Loading } from '@/components/states'

const statuses: ProspectStatus[] = ['new', 'researching', 'researched', 'qualified', 'unqualified']
const formSchema = z.object({
  company_name: z.string().trim().min(1, 'Company name is required'),
  website_url: z.string().trim().min(1, 'Website is required'),
  full_name: z.string(),
  email: z.union([z.email(), z.literal('')]),
  job_title: z.string(),
  industry: z.string(),
  location: z.string(),
  linkedin_url: z.string(),
  source_url: z.string(),
  notes: z.string(),
  status: z.enum(statuses),
  do_not_contact: z.boolean(),
})
type FormValues = z.infer<typeof formSchema>
const defaults: FormValues = {
  company_name: '',
  website_url: '',
  full_name: '',
  email: '',
  job_title: '',
  industry: '',
  location: '',
  linkedin_url: '',
  source_url: '',
  notes: '',
  status: 'new',
  do_not_contact: false,
}
function ProspectForm({
  prospect,
  close,
  saved,
}: {
  prospect?: Prospect
  close: () => void
  saved: () => void
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: prospect
      ? {
          ...defaults,
          ...Object.fromEntries(
            Object.keys(defaults).map((k) => [
              k,
              prospect[k as keyof Prospect] ?? defaults[k as keyof FormValues],
            ]),
          ),
          company_name: prospect.company.name,
          website_url: prospect.company.website_url,
          industry: prospect.company.industry ?? '',
        }
      : defaults,
  })
  const mutation = useMutation({
    mutationFn: (data: FormValues) =>
      api(prospect ? `/prospects/${prospect.id}` : '/prospects', {
        method: prospect ? 'PATCH' : 'POST',
        body: JSON.stringify({ ...data, source: prospect?.source ?? 'manual' }),
      }),
    onSuccess: saved,
  })
  const fields: [keyof FormValues, string][] = [
    ['company_name', 'Company name'],
    ['website_url', 'Company website'],
    ['full_name', 'Contact name (if known)'],
    ['email', 'Email (if known)'],
    ['job_title', 'Job title'],
    ['industry', 'Industry'],
    ['location', 'Location'],
    ['linkedin_url', 'LinkedIn URL'],
    ['source_url', 'Source URL'],
  ]
  return (
    <Modal title={prospect ? 'Edit prospect' : 'Add prospect'} close={close}>
      <form onSubmit={handleSubmit((data) => mutation.mutate(data))}>
        <p className="help mb-5">
          Only add information you know. Company records can have no named contact.
        </p>
        <div className="form-grid">
          {fields.map(([name, label]) => (
            <label key={name}>
              {label}
              <input {...register(name)} autoComplete="off" />
              {errors[name] && <span className="field-error">{errors[name]?.message}</span>}
            </label>
          ))}
          <label>
            Status
            <select {...register('status')}>
              {statuses.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </label>
          <label className="full-width">
            Notes
            <textarea rows={3} {...register('notes')} />
          </label>
        </div>
        <label className="checkbox-line">
          <input type="checkbox" {...register('do_not_contact')} />
          Do not contact / opted out
        </label>
        {mutation.error && (
          <p role="alert" className="field-error">
            {mutation.error.message}
          </p>
        )}
        <div className="dialog-actions">
          <Button type="button" variant="outline" onClick={close}>
            Cancel
          </Button>
          <Button disabled={mutation.isPending}>
            {mutation.isPending ? 'Saving…' : 'Save prospect'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
interface ImportPreview {
  headers: string[]
  mapping: Record<string, string>
  rows: { row: number; duplicate: boolean; data: FormValues }[]
  errors: { row: number; message: string }[]
  duplicates: number
  total_rows: number
}
interface ImportResult {
  imported_rows: number
  duplicates: number
  total_rows: number
  errors: { row: number; message: string }[]
}
function CsvDialog({ close, saved }: { close: () => void; saved: () => void }) {
  const [text, setText] = useState(''),
    [filename, setFilename] = useState(''),
    [mapping, setMapping] = useState<Record<string, string>>({}),
    [result, setResult] = useState<ImportResult>()
  const [fileError, setFileError] = useState('')
  const preview = useMutation({
    mutationFn: (map: Record<string, string>) =>
      api<ImportPreview>('/imports/preview', {
        method: 'POST',
        body: JSON.stringify({ csv_text: text, mapping: map }),
      }),
    onSuccess: (value) => setMapping(value.mapping),
  })
  const importer = useMutation({
    mutationFn: () =>
      api<ImportResult>('/imports/csv', {
        method: 'POST',
        body: JSON.stringify({ csv_text: text, mapping, filename, confirm: true }),
      }),
    onSuccess: (value) => {
      setResult(value)
      saved()
    },
  })
  async function loadFile(file?: File) {
    setFileError('')
    preview.reset()
    setResult(undefined)
    setMapping({})
    if (!file) return
    if (file.size > 2_000_000 || !file.name.toLowerCase().endsWith('.csv')) {
      setFileError('Choose a .csv file up to 2 MB.')
      return
    }
    const content = await file.text()
    setText(content)
    setFilename(file.name)
    try {
      const columns = await api<{ headers: string[]; mapping: Record<string, string> }>(
        '/imports/columns',
        {
          method: 'POST',
          body: JSON.stringify({ csv_text: content }),
        },
      )
      setMapping(columns.mapping)
    } catch (error) {
      setFileError(error instanceof Error ? error.message : 'CSV header could not be read.')
    }
  }
  return (
    <Modal title="Import prospects from CSV" close={close}>
      <p className="help">
        Up to 1,000 rows / 2 MB. Required fields: company_name and website_url. Preview validates
        every row before importing.
      </p>
      <label className="file-picker">
        <FileUp size={25} />
        <span>{filename || 'Choose a CSV file'}</span>
        <input
          aria-label="CSV file"
          type="file"
          accept=".csv"
          onChange={(e) => void loadFile(e.target.files?.[0])}
        />
      </label>
      {fileError && <p className="field-error">{fileError}</p>}
      {Object.keys(mapping).length > 0 && (
        <>
          <h3>Map columns</h3>
          <div className="form-grid">
            {Object.entries(mapping).map(([header, field]) => (
              <label key={header}>
                {header}
                <select
                  value={field}
                  onChange={(e) => {
                    setMapping({ ...mapping, [header]: e.target.value })
                    preview.reset()
                  }}
                >
                  <option value="ignore">Ignore column</option>
                  {Object.keys(defaults).map((key) => (
                    <option key={key}>{key}</option>
                  ))}
                </select>
              </label>
            ))}
          </div>
          <Button
            className="mt-4"
            variant="outline"
            disabled={preview.isPending}
            onClick={() => preview.mutate(mapping)}
          >
            {preview.isPending ? 'Validating…' : 'Preview import'}
          </Button>
        </>
      )}
      {preview.data && !result && (
        <div className="preview-block">
          <h3>Import preview</h3>
          <p className="help">
            {preview.data.total_rows} rows · {preview.data.rows.filter((r) => !r.duplicate).length}{' '}
            ready · {preview.data.duplicates} duplicates · {preview.data.errors.length} invalid
          </p>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Row</th>
                  <th>Company</th>
                  <th>Contact</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                {preview.data.rows.slice(0, 30).map((row) => (
                  <tr key={row.row}>
                    <td>{row.row}</td>
                    <td>{row.data.company_name}</td>
                    <td>{row.data.full_name || 'No contact supplied'}</td>
                    <td>{row.duplicate ? 'Duplicate · skipped' : 'Ready'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {preview.data.rows.length > 30 && (
            <p className="help">First 30 rows shown. All rows are validated.</p>
          )}
          {preview.data.errors.map((e) => (
            <p className="field-error" key={e.row}>
              Row {e.row}: {e.message}
            </p>
          ))}
        </div>
      )}
      {(preview.error || importer.error) && (
        <p role="alert" className="field-error">
          {(preview.error || importer.error)?.message}
        </p>
      )}
      {result && (
        <div role="status" className="notice success">
          Import saved: {result.imported_rows} imported, {result.duplicates} duplicates,{' '}
          {result.errors.length} invalid rows.
        </div>
      )}
      <div className="dialog-actions">
        <Button variant="outline" onClick={close}>
          {result ? 'Done' : 'Cancel'}
        </Button>
        {preview.data && !result && (
          <Button
            disabled={importer.isPending || !preview.data.rows.some((r) => !r.duplicate)}
            onClick={() => importer.mutate()}
          >
            {importer.isPending ? 'Importing…' : 'Confirm import'}
          </Button>
        )}
      </div>
    </Modal>
  )
}
interface DiscoveryResult {
  company_name: string
  website_url: string
  source: string
  source_url: string
  evidence: string
  title: string
  name_source: string
}
function DiscoveryDialog({ close, saved }: { close: () => void; saved: () => void }) {
  const [urls, setUrls] = useState(''),
    [selected, setSelected] = useState<DiscoveryResult[]>([])
  const preview = useMutation({
    mutationFn: () =>
      api<{
        results: DiscoveryResult[]
        errors: { url: string; message: string }[]
        limitation: string
      }>('/discovery/preview', {
        method: 'POST',
        body: JSON.stringify({
          urls: urls
            .split('\n')
            .map((v) => v.trim())
            .filter(Boolean),
        }),
      }),
    onSuccess: (result) => setSelected(result.results),
  })
  const importer = useMutation({
    mutationFn: () =>
      api('/discovery/import', {
        method: 'POST',
        body: JSON.stringify({
          prospects: selected.map(({ company_name, website_url, source, source_url }) => ({
            company_name,
            website_url,
            source,
            source_url,
          })),
          confirm: true,
        }),
      }),
    onSuccess: () => {
      saved()
      close()
    },
  })
  return (
    <Modal title="Discover from public sources" close={close}>
      <p className="help">
        Supply up to three public company or directory page URLs, one per line. We respect access
        policies and only extract page-supported company information. No contacts are guessed.
      </p>
      <label className="mt-4 block">
        Source URLs
        <textarea
          rows={3}
          value={urls}
          onChange={(e) => setUrls(e.target.value)}
          placeholder="https://company.com/about"
        />
      </label>
      <Button
        className="mt-4"
        disabled={preview.isPending || !urls.trim()}
        onClick={() => preview.mutate()}
      >
        {preview.isPending ? 'Checking sources…' : 'Fetch source preview'}
      </Button>
      {preview.data && (
        <div className="preview-block">
          <p className="help">{preview.data.limitation}</p>
          {selected.map((row, i) => (
            <div className="source-card" key={`${row.source_url}-${row.website_url}`}>
              <label>
                Confirm company name
                <input
                  value={row.company_name}
                  onChange={(e) =>
                    setSelected(
                      selected.map((r, index) =>
                        index === i ? { ...r, company_name: e.target.value } : r,
                      ),
                    )
                  }
                />
              </label>
              <p className="help">Name from {row.name_source}.</p>
              <a className="source-link" href={row.source_url} target="_blank" rel="noreferrer">
                {row.source_url}
                <ExternalLink size={12} />
              </a>
              <p className="evidence">{row.evidence}</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelected(selected.filter((_, index) => index !== i))}
              >
                Remove from import
              </Button>
            </div>
          ))}
          {preview.data.errors.map((e) => (
            <p className="field-error" key={e.url}>
              {e.url}: {e.message}
            </p>
          ))}
        </div>
      )}
      {(preview.error || importer.error) && (
        <p role="alert" className="field-error">
          {(preview.error || importer.error)?.message}
        </p>
      )}
      <div className="dialog-actions">
        <Button variant="outline" onClick={close}>
          Cancel
        </Button>
        <Button disabled={!selected.length || importer.isPending} onClick={() => importer.mutate()}>
          {importer.isPending ? 'Saving…' : 'Confirm company import'}
        </Button>
      </div>
    </Modal>
  )
}
function CompanyDialog({ id, close }: { id: string; close: () => void }) {
  const query = useQuery({
    queryKey: ['company', id],
    queryFn: () => api<{ company: Company; prospects: Prospect[] }>(`/companies/${id}`),
  })
  return (
    <Modal title="Company details" close={close}>
      {query.isPending ? (
        <Loading />
      ) : query.error ? (
        <ErrorState error={query.error} />
      ) : (
        <>
          <h3>{query.data.company.name}</h3>
          <a
            className="source-link"
            href={query.data.company.website_url}
            target="_blank"
            rel="noreferrer"
          >
            {query.data.company.domain}
            <ExternalLink size={13} />
          </a>
          <p className="help">Industry: {query.data.company.industry || 'Not supplied'}</p>
          <h3 className="mt-5">Associated prospects ({query.data.prospects.length})</h3>
          {query.data.prospects.map((p) => (
            <div className="list-item" key={p.id}>
              <span>
                {p.full_name || 'Contact not identified'}
                <small>{p.job_title || p.email || 'Company-level prospect'}</small>
              </span>
              <Badge value={p.status} />
            </div>
          ))}
        </>
      )}
    </Modal>
  )
}

export default function ProspectsPage() {
  const client = useQueryClient()
  const [search, setSearch] = useState(''),
    [status, setStatus] = useState(''),
    [sort, setSort] = useState('created_at'),
    [direction, setDirection] = useState('desc'),
    [page, setPage] = useState(1)
  const [modal, setModal] = useState<'add' | 'edit' | 'csv' | 'discovery' | null>(null),
    [editing, setEditing] = useState<Prospect>(),
    [deleting, setDeleting] = useState<Prospect>(),
    [companyId, setCompanyId] = useState<string>()
  const [selected, setSelected] = useState<string[]>([]),
    [message, setMessage] = useState('')
  const params = new URLSearchParams({ search, status, sort, direction, page: String(page) })
  if (!status) params.delete('status')
  const query = useQuery({
    queryKey: ['prospects', search, status, sort, direction, page],
    queryFn: () => api<Page<Prospect>>(`/prospects?${params}`),
  })
  function refresh() {
    void client.invalidateQueries()
    setSelected([])
  }
  function saved() {
    refresh()
    setMessage('Prospect changes saved.')
    if (modal !== 'csv') setModal(null)
  }
  const remove = useMutation({
    mutationFn: () => api(`/prospects/${deleting?.id}?confirm=true`, { method: 'DELETE' }),
    onSuccess: () => {
      setDeleting(undefined)
      setMessage('Prospect deleted.')
      refresh()
    },
  })
  const bulk = useMutation({
    mutationFn: (action: string) =>
      api('/prospects/bulk', {
        method: 'POST',
        body: JSON.stringify({
          ids: selected,
          action,
          status: action === 'status' ? 'qualified' : undefined,
        }),
      }),
    onSuccess: () => {
      setMessage('Selected prospects updated.')
      refresh()
    },
  })
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Prospects</h1>
        </div>
        <div className="actions">
          <Button variant="outline" onClick={() => setModal('discovery')}>
            <Globe size={16} />
            Discover
          </Button>
          <Button variant="outline" onClick={() => setModal('csv')}>
            <FileUp size={16} />
            Import CSV
          </Button>
          <Button onClick={() => setModal('add')}>
            <Plus size={16} />
            Add prospect
          </Button>
        </div>
      </div>
      {message && (
        <div className="notice success" role="status">
          {message}
          <button onClick={() => setMessage('')} aria-label="Dismiss message">
            <X size={14} />
          </button>
        </div>
      )}
      <section className="card table-card">
        <div className="table-toolbar">
          <label className="search-input">
            <Search size={16} />
            <input
              aria-label="Search prospects"
              placeholder="Name, company, or email"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
            />
          </label>
          <div className="filters">
            <select
              aria-label="Filter status"
              value={status}
              onChange={(e) => {
                setStatus(e.target.value)
                setPage(1)
              }}
            >
              <option value="">All statuses</option>
              {statuses.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
            <select
              aria-label="Sort prospects"
              value={sort}
              onChange={(e) => {
                setSort(e.target.value)
                setPage(1)
              }}
            >
              <option value="created_at">Date added</option>
              <option value="full_name">Contact name</option>
              <option value="company">Company</option>
              <option value="status">Status</option>
            </select>
            <Button
              variant="outline"
              size="icon"
              aria-label="Reverse sort direction"
              onClick={() => setDirection(direction === 'asc' ? 'desc' : 'asc')}
            >
              <ArrowDownUp size={16} />
            </Button>
          </div>
        </div>
        {selected.length > 0 && (
          <div className="bulk-bar">
            <span>{selected.length} selected</span>
            <Button
              size="sm"
              variant="outline"
              disabled={bulk.isPending}
              onClick={() => bulk.mutate('status')}
            >
              Mark qualified
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={bulk.isPending}
              onClick={() => bulk.mutate('do_not_contact')}
            >
              Do not contact
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setSelected([])}>
              Clear
            </Button>
          </div>
        )}
        {bulk.error && <p className="field-error">{bulk.error.message}</p>}
        {query.isPending ? (
          <Loading />
        ) : query.error ? (
          <ErrorState error={query.error} retry={() => void query.refetch()} />
        ) : query.data.items.length === 0 ? (
          <EmptyState
            title={search || status ? 'No matching prospects' : 'No prospects yet'}
            description={
              search || status
                ? 'Adjust the search or status filter to find your prospects.'
                : 'Add a known company or import your list. Research and outreach begin with your own data.'
            }
          />
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>
                    <input
                      aria-label="Select all visible prospects"
                      type="checkbox"
                      checked={query.data.items.every((p) => selected.includes(p.id))}
                      onChange={(e) =>
                        setSelected(e.target.checked ? query.data.items.map((p) => p.id) : [])
                      }
                    />
                  </th>
                  <th>Contact</th>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Source</th>
                  <th>Added</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {query.data.items.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <input
                        aria-label={`Select ${p.full_name || p.company.name}`}
                        type="checkbox"
                        checked={selected.includes(p.id)}
                        onChange={(e) =>
                          setSelected(
                            e.target.checked
                              ? [...selected, p.id]
                              : selected.filter((id) => id !== p.id),
                          )
                        }
                      />
                    </td>
                    <td>
                      <div className="contact-cell">
                        <span className="company-avatar">
                          {(p.full_name || p.company.name).slice(0, 2).toUpperCase()}
                        </span>
                        <div>
                          <strong>{p.full_name || 'Contact not identified'}</strong>
                          <small>{p.email || p.job_title || 'Company-level prospect'}</small>
                          {p.do_not_contact && <span className="opt-out">Do not contact</span>}
                        </div>
                      </div>
                    </td>
                    <td>
                      <button className="company-link" onClick={() => setCompanyId(p.company.id)}>
                        {p.company.name}
                      </button>
                      <small>{p.company.domain}</small>
                    </td>
                    <td>
                      <Badge value={p.status} />
                    </td>
                    <td>
                      <span className="help">{p.source.replaceAll('_', ' ')}</span>
                      {p.source_url && (
                        <a
                          href={p.source_url}
                          className="inline-link"
                          target="_blank"
                          rel="noreferrer"
                          aria-label="View source"
                        >
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </td>
                    <td className="help">{new Date(p.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className="row-actions">
                        <Button asChild size="sm" variant="ghost">
                          <Link title="Research prospect" to={`/research?prospect=${p.id}`}>
                            <Search size={14} />
                            <span className="sr-only">Research</span>
                          </Link>
                        </Button>
                        <Button asChild size="sm" variant="ghost">
                          <Link title="Compose outreach" to={`/outreach?prospect=${p.id}`}>
                            <Building2 size={14} />
                            <span className="sr-only">Compose</span>
                          </Link>
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          aria-label={`Edit ${p.full_name || p.company.name}`}
                          onClick={() => {
                            setEditing(p)
                            setModal('edit')
                          }}
                        >
                          <Pencil size={14} />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          aria-label={`Delete ${p.full_name || p.company.name}`}
                          onClick={() => {
                            remove.reset()
                            setDeleting(p)
                          }}
                        >
                          <Trash2 size={14} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {query.data && (
          <div className="pagination">
            <span>
              {query.data.total} prospect{query.data.total === 1 ? '' : 's'} · Page {page} of{' '}
              {Math.max(1, Math.ceil(query.data.total / 20))}
            </span>
            <div className="actions">
              <Button
                variant="outline"
                size="sm"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                <ChevronLeft size={14} />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page * 20 >= query.data.total}
                onClick={() => setPage(page + 1)}
              >
                Next
                <ChevronRight size={14} />
              </Button>
            </div>
          </div>
        )}
      </section>
      {modal === 'add' && <ProspectForm close={() => setModal(null)} saved={saved} />}
      {modal === 'edit' && editing && (
        <ProspectForm prospect={editing} close={() => setModal(null)} saved={saved} />
      )}
      {modal === 'csv' && <CsvDialog close={() => setModal(null)} saved={refresh} />}
      {modal === 'discovery' && <DiscoveryDialog close={() => setModal(null)} saved={refresh} />}
      {companyId && <CompanyDialog id={companyId} close={() => setCompanyId(undefined)} />}
      {deleting && (
        <Modal title="Delete prospect?" close={() => setDeleting(undefined)}>
          <p className="help">
            Delete {deleting.full_name || deleting.company.name}? Associated drafts and approval
            events will also be removed. The company, research and activity history remain.
          </p>
          {remove.error && (
            <p role="alert" className="field-error">
              {remove.error.message}
            </p>
          )}
          <div className="dialog-actions">
            <Button variant="outline" onClick={() => setDeleting(undefined)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              disabled={remove.isPending}
              onClick={() => remove.mutate()}
            >
              {remove.isPending ? 'Deleting…' : 'Confirm deletion'}
            </Button>
          </div>
        </Modal>
      )}
    </>
  )
}
