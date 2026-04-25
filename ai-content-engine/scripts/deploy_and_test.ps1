<#
Run full deploy and test sequence:
- docker-compose up --build -d
- run alembic migrations
- run DB connectivity check
- POST a test /generate job
- show backend and worker logs

Run from PowerShell in repository root (ai-content-engine):
  .\scripts\deploy_and_test.ps1
#>

param(
    [string]$ProjectPath = (Get-Location).Path
)

Set-StrictMode -Version Latest

Write-Host "Switching to project path: $ProjectPath"
Set-Location -Path $ProjectPath

Write-Host "Starting docker-compose (build & detach)"
docker-compose up --build -d

Write-Host "Services status:"
docker-compose ps

Write-Host "Running Alembic migrations inside backend container"
docker-compose run --rm backend alembic upgrade head

Write-Host "Running DB connectivity check inside backend container"
docker-compose exec backend python scripts/check_db.py

Write-Host "Posting test job to /generate"
$body = @{ topic = 'test-job' } | ConvertTo-Json
try {
    $resp = Invoke-RestMethod -Method Post -Uri 'http://localhost:2000/generate' -Body $body -ContentType 'application/json'
    Write-Host "POST response:`n" ($resp | ConvertTo-Json -Depth 3)
} catch {
    Write-Error "Failed to POST /generate: $_"
}

Write-Host "Sleeping 3s to let worker pick up task"
Start-Sleep -Seconds 3

Write-Host "Backend logs (last 200 lines):"
docker-compose logs --no-color --tail=200 backend

Write-Host "Worker logs (last 200 lines):"
docker-compose logs --no-color --tail=200 worker

Write-Host "If you want to stream logs live, run: docker-compose logs -f backend worker"

Write-Host "Done"
