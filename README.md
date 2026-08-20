
# GitDoctor 🩺

GitDoctor is an AI-powered codebase health analyzer that analyzes a GitHub repository, identifies potential issues, explains them, and eventually generates and verifies fixes.

## Current Status

The GitHub repository ingestion pipeline and initial rule-based analyzer are working.

### Current Pipeline

```text
GitHub Repository URL
        ↓
GitHub API
        ↓
Repository Metadata
        ↓
File Tree
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
Detected Issues
````

## Current Features

* GitHub repository URL validation
* GitHub REST API integration
* Repository metadata retrieval
* Repository file tree retrieval
* Relevant file filtering
* File ranking and selection
* Fetching source code from GitHub
* Rule-based code analysis
* Hardcoded secret detection
* Unsafe `eval()` detection
* Debug `print()` detection
* Repository-level analysis
* Backend unit tests
* Dockerized frontend, backend and MySQL

## Example

For the React repository:

```text
Total files:        7202
Relevant files:     1000
Selected files:     50
Fetched files:      50
Detected issues:    6
```

Example detected issue:

```json
{
    "file": "packages/react-client/src/__tests__/ReactFlight-test.js",
    "line": 1620,
    "category": "security",
    "severity": "high",
    "title": "Unsafe use of eval()"
}
```

## Tech Stack

### Frontend

* React
* JavaScript
* HTML
* CSS

### Backend

* Python
* Flask
* Flask-CORS

### Database

* MySQL 8.4

### Analysis

* GitHub REST API
* Python
* Regular Expressions
* Rule-based static analysis

### DevOps

* Docker
* Docker Compose
* Git
* GitHub

### Testing

* pytest

## Project Structure

```text
dorahack/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── projects.py
│   │   ├── services/
│   │   │   ├── github_service.py
│   │   │   └── analyzer.py
│   │   └── database.py
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
├── database/
│   └── schema.sql
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Running the Project

Start all services:

```bash
docker compose up -d
```

Check services:

```bash
docker compose ps
```

Rebuild backend:

```bash
docker compose up -d --build backend
```

View backend logs:

```bash
docker compose logs --tail=50 backend
```

## Testing

From the `backend` directory:

```bash
pytest
```

Current test status:

```text
5 passed
```

## API

### Health Check

```http
GET /api/health
```

### Database Health

```http
GET /api/health/db
```

### Analyze Repository

```http
POST /api/projects
```

Request:

```json
{
    "github_url": "https://github.com/facebook/react.git"
}
```

## Roadmap

### V1 - Repository Analysis

* [x] GitHub repository ingestion
* [x] File filtering
* [x] File ranking
* [x] Source code retrieval
* [x] Initial rule-based analyzer
* [x] Basic security detection
* [x] Basic code-quality detection
* [ ] Store issues in MySQL
* [ ] Improve issue prioritization
* [ ] Repository health score

### V2 - AI Analysis

* [ ] LLM integration
* [ ] Context-aware analysis
* [ ] Issue explanations
* [ ] Suggested fixes
* [ ] Better severity classification

### V3 - Automated Fixes

* [ ] Generate code patches
* [ ] Apply fixes
* [ ] Run tests
* [ ] Verify fixes
* [ ] Create GitHub branches
* [ ] Create GitHub pull requests

```

**This is enough for now.** Don't turn the README into a 20-page novel while the product itself is still growing. We can update it at each major milestone.
```
