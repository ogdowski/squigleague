"""
Leagues module - League management and tournament organization
"""

# Avoid eager imports that pull in FastAPI users/auth on package import.
# Router can be accessed lazily via __getattr__ to prevent side effects
# when importing submodules like `app.leagues.scoring` in tests.

def __getattr__(name):
	if name == "router":
		from app.leagues.routes import router as _router
		return _router
	raise AttributeError(f"module 'app.leagues' has no attribute {name!r}")

__all__ = ["router"]
