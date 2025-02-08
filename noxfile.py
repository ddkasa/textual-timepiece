import nox

nox.options.default_venv_backend = "uv|virtualenv"


@nox.session(python=["3.12"])
def lint(session: nox.Session):
    session.run("uv", "sync", "--no-dev", "--group", "lint")
    session.run("uv", "run", "ruff", "check", "src")


@nox.session(python=["3.12"])
def type_check(session: nox.Session):
    session.run("uv", "sync", "--no-dev", "--group", "type")
    session.run("uv", "run", "mypy", "src")


@nox.session(python=["3.10", "3.11", "3.12", "3.13"])
def test(session: nox.Session):
    session.run("uv", "sync", "--no-dev", "--group", "test")
    session.run(
        "uv", "run", "pytest", "--cov-branch", "--cov-report=xml", "-n", "auto"
    )
