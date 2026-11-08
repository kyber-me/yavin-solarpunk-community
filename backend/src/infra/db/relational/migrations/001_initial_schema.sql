-- Nature: initial development schema consolidated on 2026-11-07.
-- Apply explicitly once. Does not modify LangGraph checkpoint tables.
BEGIN;

CREATE SCHEMA IF NOT EXISTS yavin;

CREATE TABLE yavin.conversations (
    id TEXT PRIMARY KEY CHECK (id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
    sender_id TEXT NOT NULL CHECK (btrim(sender_id) <> ''),
    participant_id TEXT NOT NULL CHECK (btrim(participant_id) <> ''),
    thread_id TEXT NOT NULL UNIQUE CHECK (btrim(thread_id) <> ''),
    created_at TIMESTAMPTZ NOT NULL,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT conversations_distinct_participants CHECK (sender_id <> participant_id)
);

CREATE UNIQUE INDEX conversations_active_pair_uq
    ON yavin.conversations (
        LEAST(sender_id, participant_id),
        GREATEST(sender_id, participant_id)
    ) WHERE active;

CREATE TABLE yavin.messages (
    id TEXT PRIMARY KEY CHECK (id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
    conversation_id TEXT NOT NULL REFERENCES yavin.conversations(id),
    sender_id TEXT NOT NULL CHECK (btrim(sender_id) <> ''),
    content TEXT NOT NULL CHECK (content ~ '[^[:space:]]'),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

CREATE INDEX messages_conversation_created_idx
    ON yavin.messages (conversation_id, created_at, id);

COMMIT;
