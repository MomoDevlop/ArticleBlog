-- Initialization script for PostgreSQL Database 1 (Primary)

-- Create articles table
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

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_author ON articles(author);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC) WHERE published_at IS NOT NULL;

-- Create GIN index for JSONB tags for faster searches
CREATE INDEX IF NOT EXISTS idx_articles_tags ON articles USING GIN (tags);

-- Create full-text search index
CREATE INDEX IF NOT EXISTS idx_articles_title_content_fts ON articles USING GIN (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
);

-- Insert sample data
INSERT INTO articles (title, content, author, category, tags, status, views_count, published_at)
VALUES
    (
        'Introduction to RESTful APIs',
        'RESTful APIs are a fundamental concept in modern web development. They provide a standardized way to build web services that can be consumed by various clients.',
        'John Doe',
        'technology',
        '["api", "rest", "web-development"]'::jsonb,
        'published',
        150,
        NOW() - INTERVAL '5 days'
    ),
    (
        'Getting Started with GraphQL',
        'GraphQL is a query language for APIs that provides a more efficient, powerful and flexible alternative to REST.',
        'Jane Smith',
        'technology',
        '["graphql", "api", "query-language"]'::jsonb,
        'published',
        200,
        NOW() - INTERVAL '3 days'
    ),
    (
        'Microservices Architecture Patterns',
        'Learn about common patterns and best practices for building microservices-based applications.',
        'John Doe',
        'architecture',
        '["microservices", "architecture", "patterns"]'::jsonb,
        'draft',
        0,
        NULL
    );

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database 1 (Primary) initialized successfully';
END $$;
