-- Create job_alerts table
CREATE TABLE IF NOT EXISTS job_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    keywords TEXT[],
    locations TEXT[],
    job_types VARCHAR(50)[],
    min_salary INTEGER,
    frequency VARCHAR(50) DEFAULT 'daily',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sent TIMESTAMP
);

-- Create saved_jobs table
CREATE TABLE IF NOT EXISTS saved_jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES job_listings(id) ON DELETE CASCADE,
    notes TEXT,
    tags TEXT[],
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id)
);

-- Create application_history table
CREATE TABLE IF NOT EXISTS application_history (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    notes TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create interview_schedule table
CREATE TABLE IF NOT EXISTS interview_schedule (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    interview_type VARCHAR(50),
    scheduled_at TIMESTAMP NOT NULL,
    location VARCHAR(255),
    meeting_link VARCHAR(500),
    interviewer_name VARCHAR(255),
    interviewer_email VARCHAR(255),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create cover_letter_templates table
CREATE TABLE IF NOT EXISTS cover_letter_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    variables JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create activity_logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create skills_taxonomy table
CREATE TABLE IF NOT EXISTS skills_taxonomy (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100),
    related_skills TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_skills table
CREATE TABLE IF NOT EXISTS user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills_taxonomy(id) ON DELETE CASCADE,
    proficiency_level VARCHAR(50),
    years_experience FLOAT,
    verified BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, skill_id)
);

-- Additional indices for new tables
CREATE INDEX idx_job_alerts_user_id ON job_alerts(user_id);
CREATE INDEX idx_saved_jobs_user_id ON saved_jobs(user_id);
CREATE INDEX idx_application_history_app_id ON application_history(application_id);
CREATE INDEX idx_interview_schedule_app_id ON interview_schedule(application_id);
CREATE INDEX idx_interview_schedule_date ON interview_schedule(scheduled_at);
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at DESC);
CREATE INDEX idx_user_skills_user_id ON user_skills(user_id);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credentials_updated_at BEFORE UPDATE ON credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON cover_letter_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
