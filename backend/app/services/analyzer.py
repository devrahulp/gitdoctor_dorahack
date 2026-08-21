import re


# ==========================================
# CHECK WHETHER FILE IS A TEST FILE
# ==========================================

def is_test_file(file_path):

    path = file_path.lower()

    return (
        "/test/" in path
        or "/tests/" in path
        or "/__tests__/" in path
        or path.startswith("test/")
        or path.startswith("tests/")
    )


# ==========================================
# ANALYZE ONE FILE
# ==========================================

def analyze_file(file_path, content):

    issues = []

    test_file = is_test_file(file_path)

    lines = content.splitlines()


    # ==========================================
    # CHECK EACH LINE
    # ==========================================

    for line_number, line in enumerate(
        lines,
        start=1
    ):

        # ======================================
        # HARD CODED SECRET
        # ======================================

        secret_pattern = re.compile(
            r'(?i)(password|secret|api[_-]?key|token)'
            r'\s*=\s*["\'][^"\']+["\']'
        )

        if secret_pattern.search(line):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "security",
                "severity": "low" if test_file else "high",
                "title": "Possible hardcoded secret",
                "description": (
                    "A possible password, token, API key, "
                    "or secret is hardcoded in source code."
                ),
                "impact": (
                    "Hardcoded secrets may be exposed through "
                    "source control and could allow unauthorized access."
                ),
                "recommendation": (
                    "Move secrets to environment variables or "
                    "a secure secrets-management system."
                ),
                "confidence": 0.70 if test_file else 0.95
            })


        # ======================================
        # UNSAFE EVAL
        # ======================================

        if re.search(
            r"\beval\s*\(",
            line
        ):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "security",
                "severity": "low" if test_file else "high",
                "title": "Unsafe use of eval()",
                "description": (
                    "eval() can execute arbitrary code and "
                    "should generally be avoided with untrusted input."
                ),
                "impact": (
                    "If untrusted input reaches eval(), an attacker "
                    "may be able to execute arbitrary code."
                ),
                "recommendation": (
                    "Avoid eval() and use a safer alternative "
                    "appropriate for the required operation."
                ),
                "confidence": 0.70 if test_file else 0.95
            })


        # ======================================
        # DEBUG PRINT
        # ======================================

        if re.search(
            r"\bprint\s*\(",
            line
        ):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "code_quality",
                "severity": "low",
                "title": "Debug print statement",
                "description": (
                    "A print() statement may be leftover "
                    "debugging code."
                ),
                "impact": (
                    "Debug output can create unnecessary logs "
                    "or expose internal information."
                ),
                "recommendation": (
                    "Remove the debug statement or replace it "
                    "with the application's logging mechanism."
                ),
                "confidence": 0.85
            })


        # ======================================
        # JAVASCRIPT CONSOLE.LOG
        # ======================================

        if re.search(
            r"\bconsole\.log\s*\(",
            line
        ):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "code_quality",
                "severity": "low",
                "title": "Debug console.log statement",
                "description": (
                    "A console.log() statement may be "
                    "leftover debugging code."
                ),
                "impact": (
                    "Debug output may expose internal information "
                    "or create unnecessary production logs."
                ),
                "recommendation": (
                    "Remove the debug statement or replace it "
                    "with the application's logging mechanism."
                ),
                "confidence": 0.85
            })


        # ======================================
        # TODO / FIXME
        # ======================================

        if re.search(
            r"\b(TODO|FIXME)\b",
            line,
            re.IGNORECASE
        ):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "maintainability",
                "severity": "low",
                "title": "TODO or FIXME found",
                "description": (
                    "The source code contains a TODO or FIXME "
                    "that may represent unfinished work."
                ),
                "impact": (
                    "Unresolved TODOs can indicate unfinished "
                    "functionality or technical debt."
                ),
                "recommendation": (
                    "Review the TODO and either implement the "
                    "required work or remove the obsolete comment."
                ),
                "confidence": 0.90
            })


        # ======================================
        # PYTHON SHELL=TRUE
        # ======================================

        if re.search(
            r"\bshell\s*=\s*True",
            line
        ):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "security",
                "severity": "low" if test_file else "high",
                "title": "Potentially unsafe shell execution",
                "description": (
                    "shell=True can allow command injection "
                    "when command input is influenced by users."
                ),
                "impact": (
                    "Untrusted command input may allow an attacker "
                    "to execute operating-system commands."
                ),
                "recommendation": (
                    "Avoid shell=True when possible and pass "
                    "commands as structured arguments."
                ),
                "confidence": 0.70 if test_file else 0.95
            })


        # ======================================
        # BARE EXCEPT
        # ======================================

        if re.match(
            r"^\s*except\s*:",
            line
        ):

            issues.append({
                "file": file_path,
                "line": line_number,
                "category": "reliability",
                "severity": "medium",
                "title": "Bare except statement",
                "description": (
                    "A bare except catches every exception and "
                    "can hide unexpected application errors."
                ),
                "impact": (
                    "Unexpected errors may be hidden, making "
                    "debugging and reliability more difficult."
                ),
                "recommendation": (
                    "Catch specific exceptions instead of using "
                    "a bare except statement."
                ),
                "confidence": 0.90
            })

    return issues


# ==========================================
# ANALYZE MULTIPLE FILES
# ==========================================

def analyze_repository(files_content):

    all_issues = []

    for item in files_content:

        issues = analyze_file(
            item["file"],
            item["content"]
        )

        all_issues.extend(issues)

    return all_issues


# ==========================================
# CALCULATE HEALTH SCORE
# ==========================================

def calculate_health_score(issues):

    score = 100

    weights = {
        "critical": 15,
        "high": 8,
        "medium": 4,
        "low": 1
    }

    for issue in issues:

        severity = issue.get(
            "severity",
            "low"
        )

        score -= weights.get(
            severity,
            1
        )

    return max(
        0,
        score
    )