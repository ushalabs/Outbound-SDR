// @vitest-environment jsdom
import { afterEach, expect, it } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { Draft } from '@/lib/types'
import { DraftEditor } from './Outreach'

afterEach(cleanup)
const draft: Draft = {
  id: 'isolated-test',
  prospect_id: 'isolated-prospect',
  research_id: 'isolated-research',
  status: 'pending',
  tone: 'professional',
  current_version: 2,
  created_at: '',
  updated_at: '',
  company_name: 'Clearly synthetic UI fixture',
  contact_name: null,
  sender_context: {
    name: 'QA',
    company: 'QA fixture',
    value_proposition: 'Explicitly synthetic test data',
  },
  events: [],
  versions: [2, 1].map((version) => ({
    id: `v${version}`,
    version,
    subject: `Fixture version ${version}`,
    body: `Explicitly synthetic test body ${version}`,
    cta: '',
    personalization: {},
    context: {},
    created_at: '',
  })),
}
function setup() {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <DraftEditor draft={draft} saved={() => {}}>
        {(blocked) => <button disabled={blocked}>Review current version</button>}
      </DraftEditor>
    </QueryClientProvider>,
  )
}
it('blocks review when viewing an old immutable version', () => {
  setup()
  fireEvent.change(screen.getByLabelText('Draft version'), { target: { value: '1' } })
  expect((screen.getByLabelText('Email body') as HTMLTextAreaElement).disabled).toBe(true)
  expect((screen.getByText('Review current version') as HTMLButtonElement).disabled).toBe(true)
  fireEvent.change(screen.getByLabelText('Draft version'), { target: { value: '2' } })
  expect((screen.getByText('Review current version') as HTMLButtonElement).disabled).toBe(false)
})
it('blocks review until changed text is saved', () => {
  setup()
  fireEvent.change(screen.getByLabelText('Email body'), {
    target: { value: 'Changed isolated test body' },
  })
  expect((screen.getByText('Review current version') as HTMLButtonElement).disabled).toBe(true)
  expect((screen.getByText('Save new version') as HTMLButtonElement).disabled).toBe(false)
})
