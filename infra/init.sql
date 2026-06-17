-- infra/init.sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE api_requests (
    id          SERIAL PRIMARY KEY,
    request_id  UUID DEFAULT gen_random_uuid() NOT NULL UNIQUE,
    timestamp   TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    endpoint    VARCHAR(20) NOT NULL CHECK (endpoint IN ('stt', 'tts', 'idp')),
    http_status SMALLINT NOT NULL,
    latency_ms  INTEGER NOT NULL,
    error_msg   TEXT,
    created_at  TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE stt_details (
    id                  SERIAL PRIMARY KEY,
    request_id          UUID NOT NULL REFERENCES api_requests(request_id),
    input_filename      TEXT NOT NULL,
    audio_duration_secs FLOAT NOT NULL,   
    audio_channels      SMALLINT NOT NULL, 
    detected_language   VARCHAR(10),       
    deepgram_model      VARCHAR(50),      
    num_speakers        SMALLINT,          
    transcript_summary  TEXT,
    diarization_json    JSONB,
    input_tokens        INTEGER,     
    output_tokens       INTEGER,
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()  
);

CREATE TABLE tts_details (
    id             SERIAL PRIMARY KEY,
    request_id     UUID NOT NULL REFERENCES api_requests(request_id),
    input_text     TEXT NOT NULL,
    input_chars    INTEGER NOT NULL,  
    voice_model    VARCHAR(50),       
    output_format  VARCHAR(20),
    file_reference TEXT,
    created_at     TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()  
);

CREATE TABLE idp_details (
    id                SERIAL PRIMARY KEY,
    request_id        UUID NOT NULL REFERENCES api_requests(request_id),
    input_filename    TEXT NOT NULL,
    document_type     VARCHAR(50),     
    prompt_tokens     INTEGER NOT NULL, 
    completion_tokens INTEGER NOT NULL, 
    total_tokens      INTEGER NOT NULL, 
    azure_model       VARCHAR(50),      
    extracted_json    TEXT,
    created_at        TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() 
);

CREATE TABLE IF NOT EXISTS tasks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type        VARCHAR(20) NOT NULL CHECK (type IN ('stt', 'tts', 'idp')),
    status      VARCHAR(20) NOT NULL DEFAULT 'pending' 
                CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    filename    TEXT,
    result      JSONB,
    error_msg   TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Índices
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type ON tasks(type);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

CREATE INDEX idx_requests_endpoint  ON api_requests(endpoint);
CREATE INDEX idx_requests_timestamp ON api_requests(timestamp);
CREATE INDEX idx_requests_status    ON api_requests(http_status);