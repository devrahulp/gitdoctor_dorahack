CREATE DATABASE IF NOT EXISTS gitdoctor;

USE gitdoctor;

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    github_url VARCHAR(500) NOT NULL UNIQUE,
    owner VARCHAR(255) NOT NULL,
    repository_name VARCHAR(255) NOT NULL,
    language VARCHAR(100),
    framework VARCHAR(100),
    project_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    health_score INT,
    total_issues INT DEFAULT 0,
    critical_count INT DEFAULT 0,
    high_count INT DEFAULT 0,
    medium_count INT DEFAULT 0,
    low_count INT DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE
);

CREATE TABLE issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    title VARCHAR(500) NOT NULL,
    category VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    file_path VARCHAR(1000),
    line_number INT,
    description TEXT,
    impact TEXT,
    recommendation TEXT,
    confidence DECIMAL(5,4),
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id)
        REFERENCES analyses(id)
        ON DELETE CASCADE
);

CREATE TABLE fixes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT NOT NULL,
    description TEXT,
    original_code TEXT,
    fixed_code TEXT,
    diff TEXT,
    status VARCHAR(50) DEFAULT 'generated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_at TIMESTAMP NULL,
    FOREIGN KEY (issue_id)
        REFERENCES issues(id)
        ON DELETE CASCADE
);

CREATE TABLE verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fix_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    test_command VARCHAR(1000),
    output TEXT,
    exit_code INT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (fix_id)
        REFERENCES fixes(id)
        ON DELETE CASCADE
);