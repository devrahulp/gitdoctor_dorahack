import re


def analyze_file(file_path, content):

    issues = []

    # Hardcoded password / secret / API key
    secret_pattern = re.compile(
        r'(?i)(password|secret|api[_-]?key|token)\s*=\s*["\'][^"\']+["\']'
    )

    for line_number, line in enumerate(
        content.splitlines(),
        start=1
    ):

        if secret_pattern.search(line):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "security",
                "severity": "high",
                "title": "Possible hardcoded secret",
                "description": "A possible password, token, or secret is hardcoded in source code."
            })

    return issues
