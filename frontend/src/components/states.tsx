import { AlertCircle, ArrowUpRight, Inbox, LoaderCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from './ui/button'
export function Loading() { return <div className="state" role="status"><LoaderCircle className="animate-spin" />Loading workspace…</div> }
export function ErrorState({ error, retry }: { error: Error, retry?: () => void }) { return <div className="state error" role="alert"><AlertCircle /><p>{error.message}</p>{retry && <Button variant="outline" onClick={retry}>Try again</Button>}</div> }
export function EmptyState({ title, description, to, action }: { title: string, description: string, to?: string, action?: string }) { return <div className="state"><div className="empty-icon"><Inbox size={26} /></div><h3>{title}</h3><p>{description}</p>{to && <Button asChild><Link to={to}>{action}<ArrowUpRight size={16}/></Link></Button>}</div> }
