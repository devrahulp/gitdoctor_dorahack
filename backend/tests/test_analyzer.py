from app.services.analyzer import (
    analyze_file,
    analyze_repository,
    calculate_health_score
)


def test_detect_hardcoded_password():

    code = '''
password = "admin123"
'''

    issues = analyze_file(
        "app.py",
        code
    )

    assert len(issues) == 1
    assert issues[0]["category"] == "security"
    assert issues[0]["severity"] == "high"


def test_detect_eval():

    code = '''
result = eval(user_input)
'''

    issues = analyze_file(
        "app.py",
        code
    )

    assert len(issues) == 1
    assert issues[0]["title"] == "Unsafe use of eval()"
    assert issues[0]["severity"] == "high"


def test_detect_debug_print():

    code = '''
print("debug")
'''

    issues = analyze_file(
        "app.py",
        code
    )

    assert len(issues) == 1
    assert issues[0]["category"] == "code_quality"
    assert issues[0]["severity"] == "low"


def test_detect_console_log():

    code = '''
console.log("debug");
'''

    issues = analyze_file(
        "app.js",
        code
    )

    assert len(issues) == 1
    assert issues[0]["title"] == (
        "Debug console.log statement"
    )


def test_detect_shell_true():

    code = '''
subprocess.run(command, shell=True)
'''

    issues = analyze_file(
        "app.py",
        code
    )

    assert len(issues) == 1
    assert issues[0]["severity"] == "high"


def test_analyze_repository():

    files = [
        {
            "file": "app.py",
            "content": 'password = "admin123"'
        },
        {
            "file": "test.py",
            "content": 'result = eval(user_input)'
        }
    ]

    issues = analyze_repository(
        files
    )

    assert len(issues) == 2


def test_health_score():

    issues = [
        {
            "severity": "high"
        },
        {
            "severity": "medium"
        },
        {
            "severity": "low"
        }
    ]

    score = calculate_health_score(
        issues
    )

    assert score == 87