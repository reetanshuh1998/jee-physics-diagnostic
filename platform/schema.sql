-- Database Schema for JEE Physics Diagnostic Platform

-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questions Table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(20) DEFAULT 'Physics',
    chapter VARCHAR(50) NOT NULL,
    topic VARCHAR(50),
    difficulty VARCHAR(10) CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    content TEXT NOT NULL, -- Question text or JSON for rich content
    correct_answer VARCHAR(10) NOT NULL, -- Option index or text
    explanation TEXT,
    year INTEGER, -- PYQ year if applicable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tests Table (for full syllabus or chapter-wise tests)
CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    test_type VARCHAR(20) CHECK (test_type IN ('Chapter-wise', 'Full Syllabus', 'Mock')),
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test Questions Mapping
CREATE TABLE test_questions (
    test_id INTEGER REFERENCES tests(id),
    question_id INTEGER REFERENCES questions(id),
    question_order INTEGER,
    PRIMARY KEY (test_id, question_id)
);

-- Test Attempts
CREATE TABLE test_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    test_id INTEGER REFERENCES tests(id),
    score INTEGER,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'In Progress' -- In Progress, Completed
);

-- Question Attempts (The "Gold Data" for ML)
CREATE TABLE question_attempts (
    id SERIAL PRIMARY KEY,
    test_attempt_id INTEGER REFERENCES test_attempts(id),
    question_id INTEGER REFERENCES questions(id),
    selected_answer VARCHAR(10),
    is_correct BOOLEAN,
    time_spent_seconds INTEGER, -- Time spent on this question
    revisit_count INTEGER DEFAULT 0, -- How many times the student came back to this question
    order_attempted INTEGER, -- Sequence in which they answered
    answer_changed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
