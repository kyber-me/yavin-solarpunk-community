BEGIN;

ALTER TABLE yavin.conversations ADD COLUMN title TEXT;

UPDATE yavin.conversations AS c
SET title = left('Conversa com ' || COALESCE(a.name, c.participant_id), 120)
FROM (SELECT id, name FROM yavin.agents) AS a
WHERE a.id = c.participant_id;

UPDATE yavin.conversations
SET title = left('Conversa com ' || participant_id, 120)
WHERE title IS NULL;

ALTER TABLE yavin.conversations ALTER COLUMN title SET NOT NULL;
ALTER TABLE yavin.conversations ADD CONSTRAINT conversations_title_valid
    CHECK (btrim(title) <> '' AND char_length(title) <= 120);

COMMIT;
