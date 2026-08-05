# 用法: 先到 GitHub 网页新建一个空仓库(不要勾选初始化)，然后运行：
#   powershell -ExecutionPolicy Bypass -File push_to_github.ps1 "你的仓库地址"
# 例：push_to_github.ps1 https://github.com/你的用户名/MonkeyPet-Android.git

param([string]$RepoUrl)

$ErrorActionPreference = 'Stop'
$proj = 'C:\Users\boyun\Documents\Default Project\AndroidPet'

if (-not $RepoUrl) {
    Write-Host '用法: push_to_github.ps1 "https://github.com/用户名/仓库名.git"' -ForegroundColor Yellow
    exit 1
}

Set-Location $proj
git remote remove origin 2>$null
git remote add origin $RepoUrl
git push -u origin main

Write-Host ''
Write-Host '推送成功！GitHub 会自动开始云端打包。' -ForegroundColor Green
Write-Host '查看进度: 打开仓库页面 -> Actions 标签 -> Build Android APK' -ForegroundColor Green
Write-Host '下载 APK: 构建完成后点进该任务 -> 底部 Artifacts -> monkeypet-apk' -ForegroundColor Green
