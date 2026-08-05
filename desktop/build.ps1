$ErrorActionPreference = 'Stop'

$candidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
)
$py = $null
foreach ($c in $candidates) {
    if (Test-Path $c) { $py = $c; break }
}
if (-not $py) {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notlike '*WindowsApps*') { $py = $cmd.Source }
}
if (-not $py) { throw '未找到 Python，请在 build.ps1 中手动指定 python.exe 路径' }

Write-Host "使用 Python: $py"

& $py -m pip show pyinstaller | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host '安装 pyinstaller ...'
    & $py -m pip install pyinstaller
}

& $py -m PyInstaller --noconfirm --onefile --noconsole --name DesktopPet main.py
if ($LASTEXITCODE -eq 0) {
    Write-Host '打包完成: dist\DesktopPet.exe'
}
