$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting ASA Observatory from: $projectPath"

$pythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
}

if (-not $pythonCmd) {
    Write-Error "Python launcher not found. Install Python and ensure 'py' or 'python' is available in PATH."
    exit 1
}

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$projectPath'; $pythonCmd -m uvicorn api.asa3_api_graph_v4:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$projectPath'; $pythonCmd -m streamlit run dashboard/asa3_dashboard_v4.py"
)
