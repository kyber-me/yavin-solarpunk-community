-- Nature: development migration approved on 2026-11-07.
-- Apply explicitly once to the intended database. Do not run on API startup.
BEGIN;

CREATE SCHEMA IF NOT EXISTS yavin;

CREATE TABLE yavin.conversations (
    id TEXT PRIMARY KEY CHECK (id ~ '^Conv_[0-9A-HJKMNP-TV-Z]{26}$'),
    sender_id TEXT NOT NULL CHECK (btrim(sender_id) <> ''),
    participant_id TEXT NOT NULL CHECK (btrim(participant_id) <> ''),
    look_up_key TEXT NOT NULL,
    thread_id TEXT NOT NULL UNIQUE CHECK (btrim(thread_id) <> ''),
    created_at TIMESTAMPTZ NOT NULL,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT conversations_distinct_participants CHECK (sender_id <> participant_id)
);

CREATE UNIQUE INDEX conversations_active_lookup_uq
    ON yavin.conversations (look_up_key) WHERE active;

COMMIT;
