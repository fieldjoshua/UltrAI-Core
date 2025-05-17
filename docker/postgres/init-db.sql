-- Initialize PostgreSQL database for Ultra development environment

-- Create necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search capabilities

-- Create schema
CREATE SCHEMA IF NOT EXISTS ultra;

-- Set search path
SET search_path TO ultra,public;

-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active',
    subscription_tier VARCHAR(50) DEFAULT 'free',
    api_quota_limit INTEGER DEFAULT 100,
    api_quota_used INTEGER DEFAULT 0,
    api_quota_reset_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '1 month'
);

-- Create API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_value VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create documents table if it doesn't exist
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES users(id),
    file_path VARCHAR(1024),
    content_type VARCHAR(255),
    size_bytes INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB,
    embedding_status VARCHAR(50) DEFAULT 'pending',
    embedding_error TEXT
);

-- Create document_chunks table if it doesn't exist
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB,
    embedding VECTOR(1536) -- For OpenAI embeddings, adjust dimension as needed
);

-- Create analyses table if it doesn't exist
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    type VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_used VARCHAR(255),
    prompt TEXT,
    processing_time FLOAT,
    error TEXT,
    parameters JSONB DEFAULT '{}'::jsonb
);

-- Create LLM requests tracking table
CREATE TABLE IF NOT EXISTS llm_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    analysis_id UUID REFERENCES analyses(id),
    model VARCHAR(255),
    provider VARCHAR(255),
    prompt TEXT,
    response TEXT,
    tokens_input INTEGER,
    tokens_output INTEGER,
    duration_ms INTEGER,
    cost NUMERIC(10, 6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending',
    error TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create table for token blacklisting
CREATE TABLE IF NOT EXISTS token_blacklist (
    jti VARCHAR(255) PRIMARY KEY,
    token_type VARCHAR(50),
    user_id UUID,
    expiry TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create analysis patterns table
CREATE TABLE IF NOT EXISTS analysis_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id UUID REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,
    prompt_template TEXT NOT NULL,
    parameters JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create settings table
CREATE TABLE IF NOT EXISTS settings (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_document_id ON analyses(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_llm_requests_user_id ON llm_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_llm_requests_analysis_id ON llm_requests(analysis_id);
CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(type);

-- Add some test data if tables are empty
DO $$
BEGIN
    -- Insert test user if no users exist
    IF NOT EXISTS (SELECT 1 FROM users LIMIT 1) THEN
        INSERT INTO users (username, email, name, password_hash, subscription_tier)
        VALUES
        ('testuser', 'test@example.com', 'Test User', '$2b$12$SRQd8YM.SjENvv.Hd1vUXeQ8dVLigdBHPq5iZlO36zT0/bcbKWJQi', 'premium'), -- password is 'testpassword'
        ('admin', 'admin@example.com', 'Admin User', '$2b$12$SRQd8YM.SjENvv.Hd1vUXeQ8dVLigdBHPq5iZlO36zT0/bcbKWJQi', 'enterprise');
    END IF;

    -- Insert default settings if settings table is empty
    IF NOT EXISTS (SELECT 1 FROM settings LIMIT 1) THEN
        INSERT INTO settings (key, value, description)
        VALUES
        ('default_models', '{"text": "gpt-3.5-turbo", "embedding": "text-embedding-ada-002"}'::jsonb, 'Default models to use for each task type'),
        ('rate_limits', '{"anonymous": 10, "user": 100, "admin": 1000}'::jsonb, 'Rate limits per minute for different user types'),
        ('feature_flags', '{"document_processing": true, "advanced_analytics": true, "mock_llm": true}'::jsonb, 'Feature flags configuration');
    END IF;

    -- Insert default analysis patterns if empty
    IF NOT EXISTS (SELECT 1 FROM analysis_patterns LIMIT 1) THEN
        INSERT INTO analysis_patterns (name, description, prompt_template, is_public)
        VALUES
        ('Basic Summary', 'Generate a concise summary of the document', 'Please provide a concise summary of the following document in 3-5 paragraphs: {{document}}', TRUE),
        ('Key Insights', 'Extract key insights from the document', 'What are the 5-7 most important insights from this document? {{document}}', TRUE),
        ('Action Items', 'Extract action items from the document', 'Please identify all action items, next steps, or tasks mentioned in the following document: {{document}}', TRUE);
    END IF;
END $$;
