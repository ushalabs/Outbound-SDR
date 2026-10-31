export type ProspectStatus = 'new' | 'researching' | 'researched' | 'qualified' | 'unqualified'
export type DraftStatus = 'pending' | 'approved' | 'rejected' | 'archived'
export interface Company { id: string; name: string; domain: string; website_url: string; industry: string | null; created_at: string }
export interface Prospect { id: string; company: Company; full_name: string | null; email: string | null; job_title: string | null; location: string | null; linkedin_url: string | null; source: string; source_url: string | null; notes: string | null; status: ProspectStatus; do_not_contact: boolean; created_at: string; updated_at: string }
export interface Page<T> { items: T[]; total: number; page: number; page_size: number }
export interface DatabaseStatus { status: string; vector_version: string | null; schema_revision: string; companies: number; prospects: number }
export interface Source { id: string; url: string | null; title: string; evidence: string; kind: string; fetched_at: string }
export interface Research { id: string; company_id: string; prospect_id: string | null; status: 'queued' | 'running' | 'completed' | 'failed'; stage: string; findings: Record<string, unknown> | null; error: string | null; model: string | null; created_at: string; sources?: Source[] }
export interface DraftVersion { id: string; version: number; subject: string; body: string; cta: string; personalization: Record<string, unknown>; context: Record<string, unknown>; created_at: string }
export interface ApprovalEvent { id: string; action: string; version_id: string; note: string | null; created_at: string }
export interface Draft { id: string; prospect_id: string; research_id: string; status: DraftStatus; tone: string; current_version: number; created_at: string; updated_at: string; versions: DraftVersion[]; events: ApprovalEvent[] }
export interface ActivityEvent { id: string; event_type: string; entity_type: string; entity_id: string | null; details: Record<string, unknown>; created_at: string }
