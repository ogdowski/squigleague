# Test Login Endpoint
$ErrorActionPreference = "Continue"

Write-Host "Testing login endpoint..." -ForegroundColor Cyan
Write-Host ""

# Test login with the credentials
Write-Host "Attempting login with Alakkhaine / FinFan11..." -ForegroundColor Yellow

$loginBody = @{
    username = "Alakkhaine"
    password = "FinFan11"
} | ConvertTo-Json

Write-Host "Request body: $loginBody" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    
    Write-Host "SUCCESS: Login worked!" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor White
    Write-Host "Response: $($response.Content)" -ForegroundColor White
}
catch {
    Write-Host "FAILED: Login failed" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $responseBody = $reader.ReadToEnd()
    Write-Host "Error response: $responseBody" -ForegroundColor Yellow
    
    # Check if it's a verification issue
    if ($responseBody -match "verify|verification") {
        Write-Host ""
        Write-Host "Email verification required!" -ForegroundColor Yellow
        Write-Host "Check MailHog at http://localhost:8025" -ForegroundColor Cyan
    }
    
    # Check if user even exists
    Write-Host ""
    Write-Host "Checking if user exists in database..." -ForegroundColor Yellow
    $checkScript = @'
import asyncio
from squire.database import get_db
from squire.models import User
from sqlalchemy import select

async def check_user():
    async for db in get_db():
        result = await db.execute(select(User).where(User.username == "alakkhaine"))
        user = result.scalar_one_or_none()
        if user:
            print(f"User found: {user.username} ({user.email})")
            print(f"Verified: {user.is_verified}")
        else:
            print("User NOT found in database")
        break

asyncio.run(check_user())
'@
    docker exec squig python -c $checkScript
}

Write-Host ""
Write-Host "Frontend error '[object Object]' means error object not being displayed properly" -ForegroundColor Yellow
