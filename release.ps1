# 一键发布脚本：推送代码 + 打 tag + 推 tag（触发 GitHub 自动构建 exe+apk 并发布 Release）
# 用法:
#   powershell -ExecutionPolicy Bypass -File release.ps1 "https://github.com/用户名/仓库名.git" v1.0.0
# 例:
#   powershell -ExecutionPolicy Bypass -File release.ps1 "https://github.com/boring114514/sui-pet.git" v1.0.0

param([string]$RepoUrl, [string]$Version)

$ErrorActionPreference = 'Stop'
$proj = 'C:\Users\boyun\Documents\Default Project\AndroidPet'

if (-not $RepoUrl -or -not $Version) {
    Write-Host '用法: release.ps1 "仓库地址" "版本号"' -ForegroundColor Yellow
    Write-Host '例:   release.ps1 "https://github.com/用户名/仓库名.git" v1.0.0' -ForegroundColor Yellow
    exit 1
}

Set-Location $proj

Write-Host '=== 1/4 提交所有改动 ===' -ForegroundColor Cyan
git add -A
git commit -m "release $Version" 2>$null

Write-Host '=== 2/4 推送代码 ===' -ForegroundColor Cyan
git remote remove origin 2>&1 | Out-Null
git remote add origin $RepoUrl
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host '推送失败，请检查网络或仓库地址' -ForegroundColor Red
    exit 1
}

Write-Host '=== 3/4 打版本 tag ===' -ForegroundColor Cyan
git tag -f "$Version"

Write-Host '=== 4/4 推送 tag（触发 GitHub 自动构建+发布）===' -ForegroundColor Cyan
git push origin "$Version" --force
if ($LASTEXITCODE -ne 0) {
    Write-Host '推送 tag 失败' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host '发布已触发！GitHub 正在自动构建 exe + apk（约 20-30 分钟）' -ForegroundColor Green
Write-Host '查看进度: 仓库页面 -> Actions 标签 -> Build Release' -ForegroundColor Green
Write-Host '完成后: 仓库页面 -> Releases 标签 即可下载安装包' -ForegroundColor Green
