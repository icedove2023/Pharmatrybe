$ErrorActionPreference = 'Stop'
Set-Location 'c:\Users\Adetokunbo\Desktop\Pharmatrybe_project\Pharmatrybe'
Write-Output 'Stopping stale Node/npm processes...'
Get-CimInstance Win32_Process | Where-Object { $PSItem.Name -match 'node|npm|vite' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Write-Output 'Removing node_modules and lockfile...'
Remove-Item -Recurse -Force .\node_modules -ErrorAction SilentlyContinue
Remove-Item -Force .\package-lock.json -ErrorAction SilentlyContinue
Write-Output 'Cleaning npm cache...'
npm cache clean --force
Write-Output 'Installing dependencies...'
npm install --no-fund --no-audit --loglevel=error
Write-Output '--- VITE VERSION ---'
node .\node_modules\vite\bin\vite.js --version
Write-Output '--- DEPENDENCY TREE ---'
npm ls vite @tanstack/react-router @tanstack/react-start --depth=0
Write-Output '--- BUILD CHECK ---'
npm run build
