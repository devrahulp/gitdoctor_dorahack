from flask import Blueprint, request
from urllib.parse import urlparse

from app.services.github_service import (
    get_repository_info,
    get_repository_tree,
    filter_relevant_files,
    rank_files,
    get_file_content
)


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
        return {
            "error": "github_url is required"
        }, 400

    github_url = data["github_url"].strip()

    if not validate_github_url(github_url):
        return {
            "error": "Invalid GitHub repository URL"
        }, 400

    try:

        # --------------------------------
        # 1. Get repository information
        # --------------------------------

        repo_info = get_repository_info(github_url)


        # --------------------------------
        # 2. Get all repository file paths
        # --------------------------------

        files = get_repository_tree(
            github_url,
            repo_info["default_branch"]
        )


        # --------------------------------
        # 3. Filter relevant files
        # --------------------------------

        relevant_files = filter_relevant_files(files)


        # --------------------------------
        # 4. Rank relevant files
        # --------------------------------

        ranked_files = rank_files(relevant_files)


        # --------------------------------
        # 5. Select files for analysis
        # --------------------------------

        config_files = []
        source_files = []
        test_files = []

        for file in ranked_files:

            lower = file.lower()
            filename = file.split("/")[-1].lower()

            if filename in {
                "package.json",
                "requirements.txt",
                "pyproject.toml",
                "dockerfile",
                "docker-compose.yml",
                "docker-compose.yaml"
            }:

                config_files.append(file)

            elif "/test" in lower or "test" in filename:

                test_files.append(file)

            else:

                source_files.append(file)


        selected_files = (
            config_files[:5]
            + source_files[:40]
            + test_files[:5]
        )

        selected_files = selected_files[:50]


        # --------------------------------
        # 6. Fetch selected file contents
        # --------------------------------

        files_content = []

        for file in selected_files:

            try:

                content = get_file_content(
                    github_url,
                    file,
                    repo_info["default_branch"]
                )

                files_content.append({
                    "file": file,
                    "content": content
                })

            except Exception:

                continue


        # --------------------------------
        # 7. Temporary response
        # --------------------------------

        return {
            "message": "Repository files fetched",

            "github": repo_info,

            "file_count": len(files),

            "relevant_file_count": len(relevant_files),

            "selected_file_count": len(selected_files),

            "fetched_file_count": len(files_content),

            "files": [
                item["file"]
                for item in files_content
            ]
        }, 200


    except Exception as e:

        return {
            "error": str(e)
        }, 400