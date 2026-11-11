-- Nature: consolidated development schema (2026-11-10).
-- Replaces migrations 001–004. Apply once on a clean database.
-- Does not modify LangGraph checkpoint tables (public schema).
-- Apply with: psql $DATABASE_URL -f src/persistence/db/seed.sql

BEGIN;

-- CREATE SCHEMA IF NOT EXISTS yavin;

-- Conversations

CREATE TABLE conversations (
    id              TEXT        PRIMARY KEY CHECK (id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
    sender_id       TEXT        NOT NULL CHECK (btrim(sender_id) <> ''),
    participant_id  TEXT        NOT NULL CHECK (btrim(participant_id) <> ''),
    thread_id       TEXT        NOT NULL UNIQUE CHECK (btrim(thread_id) <> ''),
    title           TEXT        NOT NULL CHECK (btrim(title) <> '' AND char_length(title) <= 120),
    created_at      TIMESTAMPTZ NOT NULL,
    start_date      TIMESTAMPTZ,
    end_date        TIMESTAMPTZ,
    active          BOOLEAN     NOT NULL DEFAULT TRUE,
    CONSTRAINT conversations_distinct_participants CHECK (sender_id <> participant_id)
);

-- One active conversation per ordered pair of participants.
CREATE UNIQUE INDEX conversations_active_pair_uq
    ON conversations (
        LEAST(sender_id, participant_id),
        GREATEST(sender_id, participant_id)
    ) WHERE active;

-- Messages

CREATE TABLE messages (
    id              TEXT        PRIMARY KEY CHECK (id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
    conversation_id TEXT        NOT NULL REFERENCES conversations(id),
    sender_id       TEXT        NOT NULL CHECK (btrim(sender_id) <> ''),
    content         TEXT        NOT NULL CHECK (content ~ '[^[:space:]]'),
    created_at      TIMESTAMPTZ NOT NULL,
    updated_at      TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX messages_conversation_created_idx
    ON messages (conversation_id, created_at, id);

-- Agents

CREATE TABLE agents (
    id                 TEXT PRIMARY KEY CHECK (id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
    name               TEXT NOT NULL UNIQUE CHECK (btrim(name) <> ''),
    public_description TEXT CHECK (public_description IS NULL OR btrim(public_description) <> '')
);

-- Documents

CREATE TABLE documents (
    id             TEXT PRIMARY KEY CHECK (id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
    kind           TEXT NOT NULL CHECK (kind IN ('identity', 'manifesto', 'research_project')),
    agent_id       TEXT REFERENCES agents(id) ON DELETE CASCADE,
    notion_page_id TEXT,
    content        TEXT,
    CONSTRAINT document_source CHECK (
        (kind = 'identity'
            AND agent_id IS NOT NULL
            AND content IS NOT NULL AND btrim(content) <> ''
            AND notion_page_id IS NULL)
        OR
        (kind <> 'identity'
            AND agent_id IS NULL
            AND notion_page_id IS NOT NULL AND btrim(notion_page_id) <> ''
            AND content IS NULL)
    )
);

-- One identity document per agent (partial unique index).
CREATE UNIQUE INDEX documents_identity_agent_uq
    ON documents(agent_id) WHERE kind = 'identity';

-- One general document per kind (manifesto, research_project).
CREATE UNIQUE INDEX documents_general_kind_uq
    ON documents(kind) WHERE agent_id IS NULL;

COMMIT;
