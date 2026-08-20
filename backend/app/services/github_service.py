import os
import json
import tempfile
import requests
import base64

from git import Repo


# ==========================================
# OLD CLONE FUNCTION
# ==========================================

def clone_repository(github_url):
    temp_dir = tempfile.mkdtemp()

    Repo.clone_from(
        github_url,
        temp_dir,
        depth=1
    )

    return temp_dir


# ==========================================
# OLD PROJECT DETECTION
# ==========================================

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

            files.append(
                relative_path.replace("\\", "/")
            )

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

            counts[language] = (
                counts.get(language, 0) + 1
            )

    if not counts:
        return "Unknown"

    return max(
        counts,
        key=counts.get
    )


def detect_framework(repo_path, files):

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


    if "package.json" in files:

        try:

            with open(
                os.path.join(repo_path, "package.json"),
                "r",
                encoding="utf-8"
            ) as f:

                package = json.load(f)

            dependencies = {}

            dependencies.update(
                package.get("dependencies", {})
            )

            dependencies.update(
                package.get("devDependencies", {})
            )

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


# ==========================================
# GITHUB API
# ==========================================

def get_repository_info(github_url):

    clean_url = github_url.rstrip("/")

    if clean_url.endswith(".git"):
        clean_url = clean_url[:-4]

    parts = clean_url.split("/")

    owner = parts[-2]
    repo = parts[-1]

    headers = {}

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}",
        headers=headers,
        timeout=10
    )

    if response.status_code != 200:

        raise ValueError(
            f"GitHub repository not found or inaccessible: "
            f"{response.status_code}"
        )

    data = response.json()

    return {
        "owner": data["owner"]["login"],
        "repository_name": data["name"],
        "default_branch": data["default_branch"],
        "language": data["language"],
        "size_kb": data["size"],
        "private": data["private"]
    }


def get_repository_tree(
    github_url,
    default_branch
):

    clean_url = github_url.rstrip("/")

    if clean_url.endswith(".git"):
        clean_url = clean_url[:-4]

    parts = clean_url.split("/")

    owner = parts[-2]
    repo = parts[-1]

    headers = {}

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/git/trees/{default_branch}",
        headers=headers,
        params={
            "recursive": "1"
        },
        timeout=20
    )

    if response.status_code != 200:

        raise ValueError(
            "Could not fetch repository file tree"
        )

    data = response.json()

    files = [
        item["path"]
        for item in data.get("tree", [])
        if item["type"] == "blob"
    ]

    return files


def filter_relevant_files(files):

    allowed_extensions = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".go",
        ".rs",
        ".php"
    }

    important_files = {
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env.example"
    }

    ignored_directories = {
        ".git",
        "node_modules",
        "dist",
        "build",
        "coverage",
        "vendor",
        "__pycache__",
        ".next",
        "target",
        "compiler",
        "scripts",
        "fixtures",
        "snapshots",
        "tests"
    }

    relevant = []

    for file in files:

        parts = file.split("/")

        if any(
            directory in ignored_directories
            for directory in parts
        ):
            continue

        filename = parts[-1]

        if filename in important_files:

            relevant.append(file)

            continue

        extension = (
            "." + filename.split(".")[-1]
            if "." in filename
            else ""
        )

        if extension in allowed_extensions:

            relevant.append(file)

    return relevant[:1000]


def rank_files(files):

    scores = {}

    for file in files:

        score = 0

        filename = file.split("/")[-1].lower()

        if filename in {
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml"
        }:

            score += 10

        if (
            "/src/" in file.lower()
            or file.startswith("src/")
        ):

            score += 6

        if (
            "/app/" in file.lower()
            or file.startswith("app/")
        ):

            score += 6

        if (
            "/lib/" in file.lower()
            or file.startswith("lib/")
        ):

            score += 5

        if (
            "/test" in file.lower()
            or "test" in filename
        ):

            score += 2

        if filename.endswith(
            (".json", ".yaml", ".yml", ".toml")
        ):

            score += 3

        scores[file] = score

    return sorted(
        files,
        key=lambda file: scores[file],
        reverse=True
    )


def get_file_content(
    github_url,
    file_path,
    branch
):

    clean_url = github_url.rstrip("/")

    if clean_url.endswith(".git"):
        clean_url = clean_url[:-4]

    parts = clean_url.split("/")

    owner = parts[-2]
    repo = parts[-1]

    headers = {}

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contents/{file_path}",
        headers=headers,
        params={
            "ref": branch
        },
        timeout=20
    )

    if response.status_code != 200:

        raise ValueError(
            f"Could not fetch file: {file_path}"
        )

    data = response.json()

    content = base64.b64decode(
        data["content"]
    ).decode(
        "utf-8",
        errors="replace"
    )

    return content