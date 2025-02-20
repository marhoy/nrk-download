"""Define nox sessions."""

import nox

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True


@nox.session(python=["3.10", "3.11", "3.12", "3.13"])
def tests(session: nox.Session) -> None:
    """Run tests."""
    session.run_install(
        "uv",
        "sync",
        env={
            "UV_FROZEN": "true",
            "UV_PYTHON": f"{session.python}",
            "UV_PROJECT_ENVIRONMENT": session.virtualenv.location,
        },
    )
    session.run("pytest", *session.posargs)


@nox.session
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "docs",
        env={
            "UV_FROZEN": "true",
            "UV_PROJECT_ENVIRONMENT": session.virtualenv.location,
        },
    )
    session.run("sphinx-build", "--write-all", "docs", "docs/_build")
