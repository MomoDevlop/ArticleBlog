-- Initialization script for PostgreSQL Database 2 (Replica)

-- Create articles table (same structure as DB1)
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    tags JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(20) DEFAULT 'draft',
    views_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    published_at TIMESTAMP,
    CONSTRAINT chk_status CHECK (status IN ('draft', 'published', 'archived'))
);

-- Create same indexes as DB1
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_author ON articles(author);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC) WHERE published_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_articles_tags ON articles USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_articles_title_content_fts ON articles USING GIN (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
);

-- Create table for tracking processed events (idempotency)
CREATE TABLE IF NOT EXISTS processed_events (
    event_id VARCHAR(255) PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    article_id INTEGER,
    processed_at TIMESTAMP DEFAULT NOW(),
    event_data JSONB
);

-- Create index on processed_events
CREATE INDEX IF NOT EXISTS idx_processed_events_article_id ON processed_events(article_id);
CREATE INDEX IF NOT EXISTS idx_processed_events_type ON processed_events(event_type);
CREATE INDEX IF NOT EXISTS idx_processed_events_processed_at ON processed_events(processed_at DESC);

-- Create function to clean old processed events (retention policy)
CREATE OR REPLACE FUNCTION clean_old_processed_events()
RETURNS void AS $$
BEGIN
    DELETE FROM processed_events
    WHERE processed_at < NOW() - INTERVAL '30 days';
    RAISE NOTICE 'Cleaned old processed events';
END;
$$ LANGUAGE plpgsql;

-- Create function to generate event ID for idempotency
CREATE OR REPLACE FUNCTION generate_event_id(p_event_type VARCHAR, p_article_id INTEGER, p_timestamp TIMESTAMP)
RETURNS VARCHAR AS $$
BEGIN
    RETURN MD5(p_event_type || ':' || p_article_id::TEXT || ':' || p_timestamp::TEXT);
END;
$$ LANGUAGE plpgsql;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database 2 (Replica) initialized successfully';
    RAISE NOTICE 'Processed events table created for idempotency';
END $$;
