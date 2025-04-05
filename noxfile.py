import nox

nox.options.default_venv_backend = "uv|virtualenv"


@nox.session(python=["3.10"])
def lint(session: nox.Session) -> None:
    session.run("uv", "sync", "--no-dev", "--group", "lint")
    session.run("uv", "run", "ruff", "check", "src")


@nox.session(python=["3.10"])
def type_check(session: nox.Session) -> None:
    session.run("uv", "sync", "--no-dev", "--group", "type")
    session.run("uv", "run", "mypy", "src")


@nox.session(python=["3.10", "3.11", "3.12", "3.13"])
def test(session: nox.Session) -> None:
    py_version = f"--python={session.python}"
    session.run("uv", "sync", py_version, "--no-dev", "--group", "test")
    session.run(
        "uv",
        "run",
        py_version,
        "pytest",
        "--cov-branch",
        "--cov-report=xml",
        "-n",
        "auto",
    )
