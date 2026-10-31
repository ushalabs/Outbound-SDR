CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE sdr.activity_logs (
	event_type VARCHAR(80) NOT NULL,
	entity_type VARCHAR(40) NOT NULL,
	entity_id UUID,
	details JSONB NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_activity_logs PRIMARY KEY (id)
);
CREATE INDEX ix_activity_logs_created_at ON sdr.activity_logs (created_at);
CREATE INDEX ix_activity_logs_entity_id ON sdr.activity_logs (entity_id);
CREATE INDEX ix_activity_logs_event_type ON sdr.activity_logs (event_type);
CREATE TABLE sdr.companies (
	name VARCHAR(200) NOT NULL,
	domain VARCHAR(253) NOT NULL,
	website_url TEXT NOT NULL,
	industry VARCHAR(160),
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_companies PRIMARY KEY (id),
	CONSTRAINT uq_companies_domain UNIQUE (domain)
);
CREATE INDEX ix_companies_created_at ON sdr.companies (created_at);
CREATE INDEX ix_companies_industry ON sdr.companies (industry);
CREATE TABLE sdr.import_jobs (
	filename VARCHAR(200) NOT NULL,
	file_hash VARCHAR(64) NOT NULL,
	total_rows INTEGER NOT NULL,
	imported_rows INTEGER NOT NULL,
	duplicates INTEGER NOT NULL,
	errors JSONB NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_import_jobs PRIMARY KEY (id),
	CONSTRAINT ck_import_jobs_row_counts CHECK (total_rows >= 0 AND imported_rows >= 0 AND duplicates >= 0)
);
CREATE INDEX ix_import_jobs_created_at ON sdr.import_jobs (created_at);
CREATE TABLE sdr.prospects (
	company_id UUID NOT NULL,
	full_name VARCHAR(200),
	email VARCHAR(320),
	identity_key VARCHAR(64) NOT NULL,
	job_title VARCHAR(200),
	location VARCHAR(200),
	linkedin_url TEXT,
	source VARCHAR(80) NOT NULL,
	source_url TEXT,
	notes TEXT,
	status VARCHAR(32) NOT NULL,
	do_not_contact BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_prospects PRIMARY KEY (id),
	CONSTRAINT ck_prospects_status CHECK (status IN ('new','researching','researched','qualified','unqualified')),
	CONSTRAINT fk_prospects_company_id FOREIGN KEY(company_id) REFERENCES sdr.companies (id),
	CONSTRAINT uq_prospects_email UNIQUE (email),
	CONSTRAINT uq_prospects_identity_key UNIQUE (identity_key)
);
CREATE INDEX ix_prospects_company_id ON sdr.prospects (company_id);
CREATE INDEX ix_prospects_created_at ON sdr.prospects (created_at);
CREATE INDEX ix_prospects_name ON sdr.prospects (full_name);
CREATE INDEX ix_prospects_status ON sdr.prospects (status);
CREATE TABLE sdr.research (
	company_id UUID NOT NULL,
	prospect_id UUID,
	status VARCHAR(32) NOT NULL,
	stage VARCHAR(100) NOT NULL,
	input_snapshot JSONB NOT NULL,
	findings JSONB,
	error TEXT,
	model VARCHAR(120),
	attempts INTEGER NOT NULL,
	started_at TIMESTAMP WITH TIME ZONE,
	finished_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_research PRIMARY KEY (id),
	CONSTRAINT ck_research_status CHECK (status IN ('queued','running','completed','failed')),
	CONSTRAINT fk_research_company_id FOREIGN KEY(company_id) REFERENCES sdr.companies (id),
	CONSTRAINT fk_research_prospect_id FOREIGN KEY(prospect_id) REFERENCES sdr.prospects (id) ON DELETE SET NULL
);
CREATE INDEX ix_research_company_id ON sdr.research (company_id);
CREATE INDEX ix_research_created_at ON sdr.research (created_at);
CREATE INDEX ix_research_prospect_id ON sdr.research (prospect_id);
CREATE INDEX ix_research_status ON sdr.research (status);
CREATE TABLE sdr.outreach_drafts (
	prospect_id UUID NOT NULL,
	research_id UUID NOT NULL,
	status VARCHAR(32) NOT NULL,
	tone VARCHAR(32) NOT NULL,
	current_version INTEGER NOT NULL,
	sender_context JSONB NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_outreach_drafts PRIMARY KEY (id),
	CONSTRAINT ck_outreach_drafts_status CHECK (status IN ('pending','approved','rejected','archived')),
	CONSTRAINT ck_outreach_drafts_tone CHECK (tone IN ('professional','concise','friendly')),
	CONSTRAINT ck_outreach_drafts_version CHECK (current_version > 0),
	CONSTRAINT fk_outreach_drafts_prospect_id FOREIGN KEY(prospect_id) REFERENCES sdr.prospects (id) ON DELETE CASCADE,
	CONSTRAINT fk_outreach_drafts_research_id FOREIGN KEY(research_id) REFERENCES sdr.research (id)
);
CREATE INDEX ix_outreach_drafts_created_at ON sdr.outreach_drafts (created_at);
CREATE INDEX ix_outreach_drafts_prospect_id ON sdr.outreach_drafts (prospect_id);
CREATE INDEX ix_outreach_drafts_research_id ON sdr.outreach_drafts (research_id);
CREATE INDEX ix_outreach_drafts_status ON sdr.outreach_drafts (status);
CREATE TABLE sdr.research_sources (
	research_id UUID NOT NULL,
	url TEXT,
	title VARCHAR(300) NOT NULL,
	kind VARCHAR(32) NOT NULL,
	evidence TEXT NOT NULL,
	fetched_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_research_sources PRIMARY KEY (id),
	CONSTRAINT fk_research_sources_research_id FOREIGN KEY(research_id) REFERENCES sdr.research (id) ON DELETE CASCADE
);
CREATE INDEX ix_research_sources_created_at ON sdr.research_sources (created_at);
CREATE INDEX ix_research_sources_research_id ON sdr.research_sources (research_id);
CREATE TABLE sdr.draft_versions (
	draft_id UUID NOT NULL,
	version INTEGER NOT NULL,
	subject VARCHAR(300) NOT NULL,
	body TEXT NOT NULL,
	personalization JSONB NOT NULL,
	cta TEXT NOT NULL,
	context JSONB NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_draft_versions PRIMARY KEY (id),
	CONSTRAINT uq_draft_versions_draft_id UNIQUE (draft_id, version),
	CONSTRAINT ck_draft_versions_version CHECK (version > 0),
	CONSTRAINT fk_draft_versions_draft_id FOREIGN KEY(draft_id) REFERENCES sdr.outreach_drafts (id) ON DELETE CASCADE
);
CREATE INDEX ix_draft_versions_created_at ON sdr.draft_versions (created_at);
CREATE INDEX ix_draft_versions_draft_id ON sdr.draft_versions (draft_id);
CREATE TABLE sdr.research_chunks (
	source_id UUID NOT NULL,
	text TEXT NOT NULL,
	embedding VECTOR(768),
	embedding_model VARCHAR(120),
	embedding_status VARCHAR(32) NOT NULL,
	embedding_error TEXT,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_research_chunks PRIMARY KEY (id),
	CONSTRAINT ck_research_chunks_embedding_status CHECK (embedding_status IN ('missing','completed','failed','stale')),
	CONSTRAINT fk_research_chunks_source_id FOREIGN KEY(source_id) REFERENCES sdr.research_sources (id) ON DELETE CASCADE
);
CREATE INDEX ix_research_chunks_created_at ON sdr.research_chunks (created_at);
CREATE INDEX ix_research_chunks_source_id ON sdr.research_chunks (source_id);
CREATE TABLE sdr.approval_events (
	draft_id UUID NOT NULL,
	version_id UUID NOT NULL,
	action VARCHAR(32) NOT NULL,
	note TEXT,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT pk_approval_events PRIMARY KEY (id),
	CONSTRAINT ck_approval_events_action CHECK (action IN ('created','edited','regenerated','approved','rejected','archived','reopened')),
	CONSTRAINT fk_approval_events_draft_id FOREIGN KEY(draft_id) REFERENCES sdr.outreach_drafts (id) ON DELETE CASCADE,
	CONSTRAINT fk_approval_events_version_id FOREIGN KEY(version_id) REFERENCES sdr.draft_versions (id) ON DELETE CASCADE
);
CREATE INDEX ix_approval_events_created_at ON sdr.approval_events (created_at);
CREATE INDEX ix_approval_events_draft_id ON sdr.approval_events (draft_id);
