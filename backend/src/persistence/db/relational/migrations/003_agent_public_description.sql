-- Optional public copy for agent discovery; identity remains a separate document.
BEGIN;

ALTER TABLE yavin.agents
    ADD COLUMN public_description TEXT,
    ADD CONSTRAINT agents_public_description_not_blank
        CHECK (public_description IS NULL OR btrim(public_description) <> '');

COMMIT;
