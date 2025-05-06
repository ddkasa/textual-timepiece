from __future__ import annotations

import nox

nox.options.default_venv_backend = "uv|virtualenv"


@nox.session(python=["3.10"])
def lint(session: nox.Session) -> None:
    session.run("uv", "sync", "--active", "--no-dev", "--group", "lint")
    session.run("uv", "run", "--active", "ruff", "check", "src")


@nox.session(python=["3.10"])
def type_check(session: nox.Session) -> None:
    session.run("uv", "sync", "--active", "--no-dev", "--group", "type")
    session.run("uv", "run", "--active", "mypy", "src")


@nox.session(python=["3.10", "3.11", "3.12", "3.13"])
def test(session: nox.Session) -> None:
    python_version = f"--python={session.python}"
    session.run(
        "uv",
        "sync",
        "--active",
        python_version,
        "--no-dev",
        "--group",
        "test",
    )
    session.run(
        "uv",
        "run",
        "--active",
        python_version,
        "pytest",
        "--cov-branch",
        "--cov-report=xml",
        "-n",
        "auto",
    )
