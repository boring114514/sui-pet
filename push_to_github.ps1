# 用法: 先到 GitHub 网页新建一个空仓库(不要勾选初始化)，然后运行：
#   powershell -ExecutionPolicy Bypass -File push_to_github.ps1 "你的仓库地址"
# 例：push_to_github.ps1 https://github.com/你的用户名/MonkeyPet-Android.git

param([string]$RepoUrl)

$proj = 'C:\Users\boyun\Documents\Default Project\AndroidPet'

if (-not $RepoUrl) {
    Write-Host '用法: push_to_github.ps1 "https://github.com/用户名/仓库名.git"' -ForegroundColor Yellow
    exit 1
}

Set-Location $proj

# 如果已有 origin 先移除（不存在时忽略错误）
git remote remove origin 2>&1 | Out-Null
git remote add origin $RepoUrl

git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host '推送失败。常见原因：' -ForegroundColor Red
    Write-Host '  1. 仓库地址填错'
    Write-Host '  2. 未登录 GitHub（会弹出登录窗口，需授权）'
    Write-Host '  3. 网络无法访问 github.com'
    exit 1
}

Write-Host ''
Write-Host '推送成功！GitHub 会自动开始云端打包。' -ForegroundColor Green
Write-Host '查看进度: 打开仓库页面 -> Actions 标签 -> Build Android APK' -ForegroundColor Green
Write-Host '下载 APK: 构建完成后点进该任务 -> 底部 Artifacts -> monkeypet-apk' -ForegroundColor Green
