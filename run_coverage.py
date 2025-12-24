"""
Run leagues tests with coverage
"""
import os
import sys
import subprocess

# Set environment
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["PYTHONPATH"] = "squigleague/backend"

# Run pytest
cmd = [
    sys.executable,
    "-m", "pytest",
    "squigleague/backend/tests/test_leagues_scoring.py",
    "squigleague/backend/tests/test_leagues_service.py",
    "squigleague/backend/tests/test_leagues_routes.py",
    "squigleague/backend/tests/test_leagues_models.py",
    "-o", "addopts=",
    "--cov=app.leagues.scoring",
    "--cov=app.leagues.service",
    "--cov=app.leagues.routes",
    "--cov=app.leagues.models",
    "--cov=app.leagues.schemas",
    "--cov-branch",
    "--cov-report=term-missing",
    "--cov-report=html:squigleague/htmlcov",
    "--cov-fail-under=100",
    "-v",
    "-W", "ignore::pytest.PytestUnraisableExceptionWarning"
]

print(f"Running: {' '.join(cmd)}\n")
result = subprocess.run(cmd, cwd="C:/repos/SquigLeague")
sys.exit(result.returncode)
