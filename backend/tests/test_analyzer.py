from app.services.analyzer import analyze_file


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
