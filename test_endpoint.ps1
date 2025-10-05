# Test script for AirGuardian notification endpoint
Write-Host "🧪 Testing AirGuardian Notification Endpoint" -ForegroundColor Cyan
Write-Host "=" * 50

# Test 1: Check if backend is running
Write-Host "1. Checking if backend is running..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000" -Method GET
    Write-Host "✅ Backend is running: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is not running. Please start it with: python backend/main.py" -ForegroundColor Red
    exit 1
}

# Test 2: Test notification endpoint
Write-Host "`n2. Testing notification endpoint..." -ForegroundColor Yellow
try {
    $body = @{
        name = "Test User"
        email = "test@example.com"
        phone = "+1234567890"
        city = "Lima"
        location = @{
            latitude = -12.0464
            longitude = -77.0428
        }
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/send-notification" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ Notification sent successfully: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error testing notification endpoint:" -ForegroundColor Red
    Write-Host "   Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🏁 Test completed" -ForegroundColor Cyan
Write-Host "If you see errors, make sure:" -ForegroundColor Yellow
Write-Host "1. Backend is running on http://localhost:8000" -ForegroundColor White
Write-Host "2. Frontend is running on http://localhost:5173" -ForegroundColor White
Write-Host "3. Both servers are started" -ForegroundColor White
