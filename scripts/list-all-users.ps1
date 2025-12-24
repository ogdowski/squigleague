# List All Users Script
$ErrorActionPreference = "Continue"

Write-Host "Listing all users in database..." -ForegroundColor Cyan
Write-Host ""

# Try different ways to query the database
Write-Host "Method 1: Via postgres container..." -ForegroundColor Yellow
docker exec -it squig-postgres psql -U squig_user -d squig_db -c "SELECT id, username, email, is_verified FROM users;"

Write-Host ""
Write-Host "Method 2: Via backend container..." -ForegroundColor Yellow
$pythonScript = @'
import asyncio
from squire.database import get_db
from squire.models import User
from sqlalchemy import select

async def list_users():
    async for db in get_db():
        result = await db.execute(select(User))
        users = result.scalars().all()
        if users:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - {user.username} ({user.email}) - Verified: {user.is_verified}")
        else:
            print("No users found in database")
        break

asyncio.run(list_users())
'@

docker exec squig python -c $pythonScript

Write-Host ""
Write-Host "If no users found, run: .\scripts\runner.ps1 create-user-alakkhaine.ps1" -ForegroundColor Yellow
