"""
Test Backend Startup

Quick script to verify the backend can start without errors.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("Testing backend imports...")

try:
    from app.config import settings
    print("✅ Config loaded")
    print(f"   - App: {settings.APP_NAME}")
    print(f"   - Environment: {settings.ENVIRONMENT}")
except Exception as e:
    print(f"❌ Config failed: {e}")
    sys.exit(1)

try:
    from app.db import engine
    print("✅ Database engine created")
except Exception as e:
    print(f"❌ Database failed: {e}")
    sys.exit(1)

try:
    from app.users.models import User, OAuthAccount
    print("✅ User models imported")
except Exception as e:
    print(f"❌ User models failed: {e}")
    sys.exit(1)

try:
    from app.users.auth import fastapi_users, google_oauth_client, discord_oauth_client
    print("✅ Auth configuration imported")
except Exception as e:
    print(f"❌ Auth config failed: {e}")
    sys.exit(1)

try:
    from app.users.routes import router
    print("✅ User routes imported")
except Exception as e:
    print(f"❌ User routes failed: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("✅ FastAPI app created")
    print(f"   - Routes: {len(app.routes)}")
except Exception as e:
    print(f"❌ FastAPI app failed: {e}")
    sys.exit(1)

print("\n🎉 All imports successful! Backend is ready.")
print("\nTo run the server:")
print("  cd backend")
print("  uvicorn app.main:app --reload")
