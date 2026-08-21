CREATE DATABASE IF NOT EXISTS gitdoctor;

USE gitdoctor;

CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    github_url VARCHAR(500) NOT NULL UNIQUE,
    owner VARCHAR(255) NOT NULL,
    repository_name VARCHAR(255) NOT NULL,
    language VARCHAR(100),
    framework VARCHAR(100),
    project_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    health_score INT NOT NULL DEFAULT 100,
    total_files INT DEFAULT 0,
    relevant_files INT DEFAULT 0,
    analyzed_files INT DEFAULT 0,
    issue_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    line_number INT,
    category VARCHAR(100),
    severity VARCHAR(50),
    title VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (analysis_id)
        REFERENCES analyses(id)
        ON DELETE CASCADE
);