import os
import json
import tempfile
from git import Repo
import requests

def clone_repository(github_url):
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(github_url, temp_dir ,  depth=1)
    return temp_dir

def detect_project(repo_path):
    files = []
    MAX_FILES = 2000

    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [
            d for d in dirs
            if d not in {
                ".git",
                "node_modules",
                "__pycache__",
                "venv",
                ".venv",
                "dist",
                "build",
                ".next",
                "target",
                "coverage"
            }
        ]

        for filename in filenames:
            if len(files) >= MAX_FILES:
                break

            relative_path = os.path.relpath(
                os.path.join(root, filename),
                repo_path
            )

            files.append(relative_path.replace("\\", "/"))

        if len(files) >= MAX_FILES:
            break

    language = detect_language(files)
    framework = detect_framework(repo_path, files)
    project_type = detect_project_type(repo_path, files)

    return {
        "language": language,
        "framework": framework,
        "project_type": project_type,
        "file_count": len(files),
        "files": sorted(files)
    }

def detect_language(files):
    extensions = {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".go": "Go",
        ".rs": "Rust",
        ".php": "PHP"
    }

    counts = {}

    for file in files:
        _, ext = os.path.splitext(file)

        if ext in extensions:
            language = extensions[ext]
            counts[language] = counts.get(language, 0) + 1

    if not counts:
        return "Unknown"

    return max(counts, key=counts.get)

def detect_framework(repo_path, files):

    # Python dependency files
    dependency_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "setup.py",
        "setup.cfg"
    ]

    content = ""

    for filename in dependency_files:
        if filename in files:
            try:
                with open(
                    os.path.join(repo_path, filename),
                    "r",
                    encoding="utf-8"
                ) as f:
                    content += f.read().lower()
            except Exception:
                pass

    if "flask" in content:
        return "Flask"

    if "django" in content:
        return "Django"

    if "fastapi" in content:
        return "FastAPI"

    if "pytest" in content:
        return "Pytest"

    # JavaScript
    if "package.json" in files:
        try:
            with open(
                os.path.join(repo_path, "package.json"),
                "r",
                encoding="utf-8"
            ) as f:
                package = json.load(f)

            dependencies = {}
            dependencies.update(package.get("dependencies", {}))
            dependencies.update(package.get("devDependencies", {}))

            if "react" in dependencies:
                return "React"

            if "next" in dependencies:
                return "Next.js"

            if "express" in dependencies:
                return "Express"

            if "vue" in dependencies:
                return "Vue"

        except Exception:
            pass

    return "Unknown"


def detect_project_type(repo_path, files):

    if "package.json" in files:
        return "Node.js Project"

    if any(file.endswith(".py") for file in files):
        return "Python Project"

    if any(file.endswith(".cpp") for file in files):
        return "C++ Project"

    if any(file.endswith(".java") for file in files):
        return "Java Project"

    if any(file.endswith(".go") for file in files):
        return "Go Project"

    return "Unknown"


def get_repository_info(github_url):
    parts = github_url.rstrip("/").replace(".git", "").split("/")

    owner = parts[-2]
    repo = parts[-1]

    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}",
        timeout=10
    )

    if response.status_code != 200:
        raise ValueError("GitHub repository not found or inaccessible")

    data = response.json()

    return {
        "owner": data["owner"]["login"],
        "repository_name": data["name"],
        "default_branch": data["default_branch"],
        "language": data["language"],
        "size_kb": data["size"],
        "private": data["private"]
    }