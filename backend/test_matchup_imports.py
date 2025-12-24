"""
Quick test to verify matchup module imports
"""

if __name__ == "__main__":
    print("Testing imports...")
    
    try:
        from app.matchup.models import Matchup
        print("✅ Matchup model imported")
    except Exception as e:
        print(f"❌ Failed to import Matchup model: {e}")
    
    try:
        from app.matchup.schemas import (
            MatchupCreate,
            MatchupCreateResponse,
            ListSubmit,
            ListSubmitResponse,
            MatchupStatus,
            MatchupReveal,
        )
        print("✅ Matchup schemas imported")
    except Exception as e:
        print(f"❌ Failed to import Matchup schemas: {e}")
    
    try:
        from app.matchup import service
        print("✅ Matchup service imported")
    except Exception as e:
        print(f"❌ Failed to import Matchup service: {e}")
    
    try:
        from app.matchup.routes import router
        print("✅ Matchup router imported")
    except Exception as e:
        print(f"❌ Failed to import Matchup router: {e}")
    
    try:
        from app.main import app
        print("✅ Main app imported")
    except Exception as e:
        print(f"❌ Failed to import main app: {e}")
    
    print("\n✅ All imports successful!")
