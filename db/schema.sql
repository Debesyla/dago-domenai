-- PostgreSQL schema for domenai project

CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    domain_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    domain_id INT NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    checked_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- trigger to update updated_at on domains
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_domains_updated_at ON domains;
CREATE TRIGGER trg_domains_updated_at
BEFORE UPDATE ON domains
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
