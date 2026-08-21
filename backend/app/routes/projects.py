from flask import Blueprint, request
from urllib.parse import urlparse

from app.services.github_service import (
    get_repository_info,
    get_repository_tree,
    filter_relevant_files,
    rank_files,
    get_file_content
)

from app.services.analyzer import (
    analyze_repository,
    calculate_health_score
)

from app.database import get_db


projects_bp = Blueprint("projects", __name__)


# ==========================================
# GITHUB URL VALIDATION
# ==========================================

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


# ==========================================
# CREATE PROJECT + ANALYZE REPOSITORY
# ==========================================

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

    db = None
    cursor = None

    try:

        # ==================================
        # 1. GET REPOSITORY INFORMATION
        # ==================================

        repo_info = get_repository_info(
            github_url
        )


        # ==================================
        # 2. GET REPOSITORY FILE TREE
        # ==================================

        files = get_repository_tree(
            github_url,
            repo_info["default_branch"]
        )


        # ==================================
        # 3. FILTER RELEVANT FILES
        # ==================================

        relevant_files = filter_relevant_files(
            files
        )


        # ==================================
        # 4. RANK FILES
        # ==================================

        ranked_files = rank_files(
            relevant_files
        )


        # ==================================
        # 5. SELECT FILES
        # ==================================

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

            elif (
                "/test" in lower
                or "test" in filename
            ):

                test_files.append(file)

            else:

                source_files.append(file)


        selected_files = (
            config_files[:5]
            + source_files[:40]
            + test_files[:5]
        )

        selected_files = selected_files[:50]


        # ==================================
        # 6. FETCH FILE CONTENT
        # ==================================

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


        # ==================================
        # 7. RUN ANALYZER
        # ==================================

        issues = analyze_repository(
            files_content
        )


        # ==================================
        # 8. CALCULATE COUNTS
        # ==================================

        critical_count = sum(
            1
            for issue in issues
            if issue.get("severity") == "critical"
        )

        high_count = sum(
            1
            for issue in issues
            if issue.get("severity") == "high"
        )

        medium_count = sum(
            1
            for issue in issues
            if issue.get("severity") == "medium"
        )

        low_count = sum(
            1
            for issue in issues
            if issue.get("severity") == "low"
        )


        # ==================================
        # 9. CALCULATE HEALTH SCORE
        # ==================================

        health_score = calculate_health_score(
            issues
        )


        # ==================================
        # 10. CONNECT DATABASE
        # ==================================

        db = get_db()
        cursor = db.cursor()


        # ==================================
        # 11. FIND OR CREATE PROJECT
        # ==================================

        cursor.execute(
            """
            SELECT id
            FROM projects
            WHERE github_url = %s
            """,
            (github_url,)
        )

        existing_project = cursor.fetchone()


        if existing_project:

            project_id = existing_project[0]

            cursor.execute(
                """
                UPDATE projects
                SET owner = %s,
                    repository_name = %s,
                    language = %s
                WHERE id = %s
                """,
                (
                    repo_info["owner"],
                    repo_info["repository_name"],
                    repo_info["language"],
                    project_id
                )
            )

        else:

            cursor.execute(
                """
                INSERT INTO projects
                (
                    github_url,
                    owner,
                    repository_name,
                    language,
                    framework,
                    project_type
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    github_url,
                    repo_info["owner"],
                    repo_info["repository_name"],
                    repo_info["language"],
                    "Unknown",
                    "Unknown"
                )
            )

            project_id = cursor.lastrowid


        # ==================================
        # 12. CREATE ANALYSIS
        # ==================================

        cursor.execute(
            """
            INSERT INTO analyses
            (
                project_id,
                status,
                health_score,
                total_issues,
                critical_count,
                high_count,
                medium_count,
                low_count,
                completed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                project_id,
                "completed",
                health_score,
                len(issues),
                critical_count,
                high_count,
                medium_count,
                low_count
            )
        )

        analysis_id = cursor.lastrowid


        # ==================================
        # 13. STORE ISSUES
        # ==================================

        for issue in issues:

            cursor.execute(
                """
                INSERT INTO issues
                (
                    analysis_id,
                    title,
                    category,
                    severity,
                    file_path,
                    line_number,
                    description,
                    impact,
                    recommendation,
                    confidence,
                    status
                )
                VALUES
                (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    analysis_id,

                    issue.get(
                        "title",
                        "Unknown issue"
                    ),

                    issue.get(
                        "category",
                        "unknown"
                    ),

                    issue.get(
                        "severity",
                        "low"
                    ),

                    issue.get(
                        "file"
                    ),

                    issue.get(
                        "line"
                    ),

                    issue.get(
                        "description"
                    ),

                    issue.get(
                        "impact",
                        "Potential impact should be reviewed."
                    ),

                    issue.get(
                        "recommendation",
                        "Review and fix the reported issue."
                    ),

                    issue.get(
                        "confidence",
                        0.8
                    ),

                    "open"
                )
            )


        # ==================================
        # 14. COMMIT EVERYTHING
        # ==================================

        db.commit()


        # ==================================
        # 15. RESPONSE
        # ==================================

        return {

            "message": "Repository analyzed successfully",

            "project_id": project_id,

            "analysis_id": analysis_id,

            "github": repo_info,

            "file_count": len(files),

            "relevant_file_count": len(
                relevant_files
            ),

            "selected_file_count": len(
                selected_files
            ),

            "fetched_file_count": len(
                files_content
            ),

            "issue_count": len(issues),

            "health_score": health_score,

            "severity_counts": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count
            },

            "issues": issues

        }, 201


    except Exception as e:

        if db:

            db.rollback()

        return {
            "error": str(e)
        }, 400


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()