from flask import Blueprint, request
from urllib.parse import urlparse

from app.services.github_service import (clone_repository ,
                                         get_repository_info ,
                                           detect_project)
from app.database import get_db


projects_bp = Blueprint("projects", __name__)


def validate_github_url(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme != "https":
            return False

        if parsed.netloc != "github.com":
            return False

        parts = parsed.path.strip("/").split("/")

        if len(parts) != 2:
            return False

        if not parts[0] or not parts[1]:
            return False

        return True

    except Exception:
        return False


@projects_bp.route("/api/projects", methods=["POST"])
def create_project():

    data = request.get_json()

    if not data or "github_url" not in data:
        return {"error": "github_url is required"}, 400

    github_url = data["github_url"].strip()

    if not validate_github_url(github_url):
        return {
            "error": "Invalid GitHub repository URL"
        }, 400

    try:

        repo_info = get_repository_info(github_url)

        return {
            "message": "GitHub repository found",
            "github": repo_info
        }, 200
        parts = github_url.rstrip("/").replace(".git", "").split("/")

        owner = parts[-2]
        repository_name = parts[-1]

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO projects
            (github_url, owner, repository_name, language, framework, project_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                github_url,
                owner,
                repository_name,
                project_info["language"],
                project_info["framework"],
                project_info["project_type"]
            )
        )
                

        db.commit()

        project_id = cursor.lastrowid

        cursor.close()
        db.close()

        return {
            "message": "Project created successfully",
            "project_id": project_id,
            "github_url": github_url,
            "owner": owner,
            "repository_name": repository_name,
            "repo_path": repo_path,
            "language": project_info["language"],
            "framework": project_info["framework"],
            "project_type": project_info["project_type"],
            "file_count":project_info["file_count"]
        }, 201

    except Exception as e:
        return {"error": str(e)}, 400