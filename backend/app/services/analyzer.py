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
                # Unsafe eval()
        if re.search(r"\beval\s*\(", line):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "security",
                "severity": "high",
                "title": "Unsafe use of eval()",
                "description": "eval() can execute arbitrary code and should generally be avoided with untrusted input."
            })

                # Debug statement
        if re.search(r"\bprint\s*\(", line):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "code_quality",
                "severity": "low",
                "title": "Debug print statement",
                "description": "A print() statement may be leftover debugging code."
            })

    return issues


def analyze_repository(files_content):

    all_issues = []

    for item in files_content:

        file_path = item["file"]
        content = item["content"]

        issues = analyze_file(
            file_path,
            content
        )

        all_issues.extend(issues)

    return all_issues