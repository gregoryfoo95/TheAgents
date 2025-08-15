-- Stock AI Service Database Schema (Separate Database)
-- Run this on the stock_ai database

-- Create database (run as superuser first)
-- CREATE DATABASE stock_ai;
-- CREATE USER stock_user WITH ENCRYPTED PASSWORD 'stock_password';
-- GRANT ALL PRIVILEGES ON DATABASE stock_ai TO stock_user;

-- Connect to stock_ai database and run the following:

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Stock Analysis Sessions (Main session tracking)
CREATE TABLE stock_analysis_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,  -- Reference to main backend user (no FK constraint)
    stock_symbol VARCHAR(10) NOT NULL,
    time_frequency VARCHAR(10) NOT NULL,
    workflow_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT chk_status 
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    CONSTRAINT chk_confidence 
        CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Agent Analysis Results
CREATE TABLE agent_analyses (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    analysis_text TEXT NOT NULL,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_agent_analysis_session 
        FOREIGN KEY (session_id) REFERENCES stock_analysis_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT chk_agent_type 
        CHECK (agent_type IN ('finance_guru', 'geopolitics_guru', 'legal_guru', 'quant_dev', 'financial_analyst'))
);

-- Stock Price Predictions
CREATE TABLE stock_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    prediction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    predicted_price DECIMAL(10,2) NOT NULL,
    prediction_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_prediction_session 
        FOREIGN KEY (session_id) REFERENCES stock_analysis_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT chk_price_positive 
        CHECK (predicted_price > 0),
    UNIQUE (session_id, prediction_date)
);

-- Chat Messages
CREATE TABLE stock_chat_messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sender_type VARCHAR(20) NOT NULL,
    message_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_chat_message_session 
        FOREIGN KEY (session_id) REFERENCES stock_analysis_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT chk_message_type 
        CHECK (message_type IN ('user_query', 'agent_response', 'system_message', 'prediction_result')),
    CONSTRAINT chk_sender_type 
        CHECK (sender_type IN ('user', 'ai_agent', 'system'))
);

-- Error Logs
CREATE TABLE stock_analysis_errors (
    error_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID,
    agent_type VARCHAR(50),
    error_type VARCHAR(50) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_error_session 
        FOREIGN KEY (session_id) REFERENCES stock_analysis_sessions(session_id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_stock_sessions_user_id ON stock_analysis_sessions(user_id);
CREATE INDEX idx_stock_sessions_symbol ON stock_analysis_sessions(stock_symbol);
CREATE INDEX idx_stock_sessions_created_at ON stock_analysis_sessions(created_at);
CREATE INDEX idx_stock_sessions_status ON stock_analysis_sessions(status);
CREATE INDEX idx_stock_sessions_workflow_id ON stock_analysis_sessions(workflow_id);

CREATE INDEX idx_agent_analyses_session_id ON agent_analyses(session_id);
CREATE INDEX idx_agent_analyses_agent_type ON agent_analyses(agent_type);

CREATE INDEX idx_predictions_session_id ON stock_predictions(session_id);
CREATE INDEX idx_predictions_date ON stock_predictions(prediction_date);

CREATE INDEX idx_chat_messages_session_id ON stock_chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON stock_chat_messages(created_at);

CREATE INDEX idx_errors_session_id ON stock_analysis_errors(session_id);
CREATE INDEX idx_errors_created_at ON stock_analysis_errors(created_at);

-- Add trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_stock_sessions_updated_at 
    BEFORE UPDATE ON stock_analysis_sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions to stock_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO stock_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO stock_user;