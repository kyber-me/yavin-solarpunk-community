BEGIN;

CREATE TABLE yavin.agents (
    id TEXT PRIMARY KEY CHECK (id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
    name TEXT NOT NULL UNIQUE CHECK (btrim(name) <> '')
);

CREATE TABLE yavin.documents (
    id TEXT PRIMARY KEY CHECK (id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
    kind TEXT NOT NULL CHECK (kind IN ('identity', 'manifesto', 'research_project')),
    agent_id TEXT REFERENCES yavin.agents(id) ON DELETE CASCADE,
    notion_page_id TEXT,
    content TEXT,
    CONSTRAINT document_source CHECK (
        (kind = 'identity' AND agent_id IS NOT NULL AND content IS NOT NULL AND btrim(content) <> '' AND notion_page_id IS NULL)
        OR (kind <> 'identity' AND agent_id IS NULL AND notion_page_id IS NOT NULL AND btrim(notion_page_id) <> '' AND content IS NULL)
    )
);

CREATE UNIQUE INDEX documents_identity_agent_uq ON yavin.documents(agent_id) WHERE kind = 'identity';
CREATE UNIQUE INDEX documents_general_kind_uq ON yavin.documents(kind) WHERE agent_id IS NULL;

COMMIT;
