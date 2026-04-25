<#
.SYNOPSIS
    Run Alembic migrations for the project in PowerShell.

.DESCRIPTION
    This helper finds a Python executable (optionally provided), ensures
    the working directory is the project root, sets PYTHONPATH so alembic
    can import `app`, and runs `alembic upgrade head`.

.PARAMETER PythonExe
    Optional path to the python executable. If not specified, uses 'python'.

Usage:
    .\scripts\run_migrations.ps1
    .\scripts\run_migrations.ps1 -PythonExe C:\path\to\python.exe
#>

param(
    [string]$PythonExe = "python"
)

Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $projectRoot

Write-Host "Using Python executable: $PythonExe"

# Ensure PYTHONPATH includes project root to allow alembic to import app
$env:PYTHONPATH = $projectRoot.Path

try {
    & $PythonExe -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Alembic returned non-zero exit code: $LASTEXITCODE"
        exit $LASTEXITCODE
    }
} catch {
    Write-Error "Failed to run alembic: $_"
    exit 10
}
