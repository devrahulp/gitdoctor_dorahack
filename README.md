# GitDoctor 🩺

GitDoctor is an AI-powered codebase health analyzer that analyzes a GitHub repository, identifies potential issues, scores repository health, and is designed to eventually generate and verify fixes.

## Current Status

**V1 Repository Health Analysis is complete.**

The current system can:

- Validate a GitHub repository URL
- Retrieve repository metadata through the GitHub REST API
- Retrieve the repository file tree
- Filter irrelevant files
- Rank relevant files
- Select the most important files for analysis
- Fetch selected file contents
- Run rule-based static analysis
- Detect security, code-quality, maintainability, and reliability issues
- Assign severity and confidence
- Calculate a repository health score
- Persist projects, analyses, and issues in MySQL
- Run backend tests
- Run the application through Docker Compose

---

## Current Pipeline

```text
GitHub Repository URL
        ↓
Validate GitHub URL
        ↓
GitHub API
        ↓
Repository Metadata
        ↓
Repository File Tree
        ↓
Filter Relevant Files
        ↓
Rank Files
        ↓
Select Top 50 Files
        ↓
Fetch File Contents
        ↓
Rule-Based Analyzer
        ↓
Detect Issues
        ↓
Severity + Confidence
        ↓
Health Score
        ↓
Store in MySQL

Current Features
GitHub Integration
GitHub repository URL validation
GitHub REST API integration
GitHub Personal Access Token support
Repository metadata retrieval
Default branch detection
Repository file tree retrieval
Source file retrieval through the GitHub API
Repository Processing

GitDoctor avoids downloading the entire repository for analysis.

For example, a large repository can go through:

7202 total files
       ↓
1000 relevant files
       ↓
50 selected files
       ↓
50 files analyzed
File Filtering

The analyzer currently considers source and configuration files such as:

.py
.js
.jsx
.ts
.tsx
.java
.cpp
.c
.go
.rs
.php


package.json
requirements.txt
pyproject.toml
Dockerfile
docker-compose.yml
docker-compose.yaml
.env.example

Directories such as the following are filtered out:

.git
node_modules
dist
build
coverage
vendor
__pycache__
.next
target
File Prioritization

Files are ranked so that important application and configuration files are analyzed first.

Higher priority is given to files such as:

package.json
requirements.txt
pyproject.toml
src/*
app/*
lib/*

The current analysis pipeline selects up to 50 files.

Rule-Based Analyzer

GitDoctor currently uses deterministic rules for the first analysis pass.

Security
Hardcoded Secrets

Detects possible hardcoded:

Passwords
Secrets
API keys
Tokens

Example:

password = "admin123"
Unsafe eval()

Detects:

result = eval(user_input)
Potentially Unsafe Shell Execution

Detects:

subprocess.run(command, shell=True)
Code Quality
Debug print()

Detects possible leftover Python debug statements:

print("debug")
Debug console.log()

Detects possible leftover JavaScript debug statements:

console.log("debug");
Maintainability
TODO / FIXME

Detects:

TODO
FIXME

These are reported as possible unfinished work or technical debt.

Reliability
Bare except

Detects:

except:

which can hide unexpected exceptions.

Severity and Confidence

GitDoctor assigns severity levels:

critical
high
medium
low

The analyzer also assigns a confidence value to findings.

Test files are treated differently from production files. For example, an eval() finding inside a test file can receive lower severity and confidence than the same pattern in application code.

Health Score

GitDoctor calculates a repository health score starting from:

100

and reduces the score according to issue severity.

Current weights:

Critical → -15
High     → -8
Medium   → -4
Low      → -1

The score is never allowed to fall below:

0
Database

GitDoctor uses MySQL 8.4.

Current database relationships:

projects
    │
    ▼
analyses
    │
    ▼
issues
    │
    ▼
fixes
Current tables
projects

Stores repository information.

analyses

Stores each analysis run and its health score.

issues

Stores detected issues including:

title
category
severity
confidence
file path
line number
description
impact
recommendation
status
fixes

The table is already prepared for future fix-generation functionality.

It is currently empty because automated fix generation is part of the next version.

Example Analysis

For the React repository:

Repository:
https://github.com/facebook/react.git

One successful analysis produced:

Total files:        7202
Relevant files:     1000
Selected files:     50
Fetched files:      50
Issues detected:    18
Health score:       82

Example finding:

{
    "file": "packages/react-client/src/__tests__/ReactFlight-test.js",
    "line": 1620,
    "category": "security",
    "severity": "low",
    "confidence": 0.7,
    "title": "Unsafe use of eval()"
}
API
Health Check
GET /api/health

Example:

{
    "status": "healthy",
    "service": "gitdoctor-backend"
}
Database Health Check
GET /api/health/db

Example:

{
    "status": "healthy",
    "database": "connected"
}
Analyze Repository
POST /api/projects

Request:

{
    "github_url": "https://github.com/facebook/react.git"
}

The endpoint performs repository ingestion, file selection, code analysis, health-score calculation, and MySQL persistence.

Technology Stack
Frontend
React
JavaScript
HTML
CSS
Backend
Python
Flask
Flask-CORS
Database
MySQL 8.4
Repository Analysis
GitHub REST API
Python
Regular Expressions
Rule-based static analysis
DevOps
Docker
Docker Compose
Git
GitHub Actions
Testing
pytest
Docker Architecture
                    Docker Compose
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
      Frontend        Backend         MySQL
       :3000           :5000           :3306
                         │
                         ▼
                    GitHub API
Running the Project

Start all services:

docker compose up -d

Check running services:

docker compose ps

Rebuild the backend:

docker compose up -d --build backend

View backend logs:

docker compose logs --tail=50 backend

View MySQL logs:

docker compose logs --tail=50 mysql

Stop services:

docker compose down

Avoid docker compose down -v unless you intentionally want to delete the MySQL Docker volume and reset the database.

Testing

From the backend directory:

pytest

The project includes tests for:

Flask health endpoint
Hardcoded secret detection
Unsafe eval() detection
Debug print detection
Debug console.log() detection
Shell execution detection
Repository-level analysis
Health score calculation
Environment Variables

Create a local .env file:

MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=gitdoctor
MYSQL_PORT=3306


MYSQL_HOST=mysql
MYSQL_USER=root


GITHUB_TOKEN=your_github_token

Never commit .env to Git.

The repository should only contain .env.example.

Project Structure
dorahack/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── projects.py
│   │   │
│   │   ├── services/
│   │   │   ├── github_service.py
│   │   │   └── analyzer.py
│   │   │
│   │   ├── database.py
│   │   └── __init__.py
│   │
│   ├── tests/
│   │   ├── test_analyzer.py
│   │   └── test_health.py
│   │
│   ├── pytest.ini
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│
├── database/
│   └── schema.sql
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md