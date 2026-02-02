-- Database Initialization Script for Agentic AI
-- ===============================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- For encryption

-- Create schemas
CREATE SCHEMA IF NOT EXISTS agenticai;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set search path
SET search_path TO agenticai, public;

-- ===============================================
-- Core Tables
-- ===============================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'user',
    api_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    config JSONB DEFAULT '{}',
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent executions log
CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50),
    duration_ms INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 4),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector embeddings
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI embedding size
    metadata JSONB DEFAULT '{}',
    source VARCHAR(255),
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API keys
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scopes JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===============================================
-- Audit Tables
-- ===============================================

CREATE TABLE IF NOT EXISTS audit.user_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===============================================
-- Indexes
-- ===============================================

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);

-- Agents indexes
CREATE INDEX IF NOT EXISTS idx_agents_owner_id ON agents(owner_id);
CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(type);
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at DESC);

-- Tasks indexes
CREATE INDEX IF NOT EXISTS idx_tasks_owner_id ON tasks(owner_id);
CREATE INDEX IF NOT EXISTS idx_tasks_agent_id ON tasks(agent_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- Agent executions indexes
CREATE INDEX IF NOT EXISTS idx_executions_agent_id ON agent_executions(agent_id);
CREATE INDEX IF NOT EXISTS idx_executions_task_id ON agent_executions(task_id);
CREATE INDEX IF NOT EXISTS idx_executions_created_at ON agent_executions(created_at DESC);

-- Embeddings indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_owner_id ON embeddings(owner_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_source ON embeddings(source);

-- API keys indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);

-- Audit indexes
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit.user_actions(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit.user_actions(action);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit.user_actions(created_at DESC);

-- ===============================================
-- Functions and Triggers
-- ===============================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update timestamp trigger to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===============================================
-- Initial Data
-- ===============================================

-- Create default admin user (password: admin123 - CHANGE IN PRODUCTION!)
INSERT INTO users (email, username, hashed_password, full_name, is_superuser, role)
VALUES (
    'admin@agenticai.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lJ3xUJjFvWAe',  -- admin123
    'System Administrator',
    TRUE,
    'admin'
)
ON CONFLICT (email) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA agenticai TO agenticai;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA agenticai TO agenticai;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO agenticai;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA audit TO agenticai;
