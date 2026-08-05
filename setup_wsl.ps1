# 用管理员身份运行本脚本（右键 PowerShell -> 以管理员身份运行）
# 作用：安装 WSL2 + Ubuntu 发行版（首次会要求重启）
$ErrorActionPreference = 'Stop'

Write-Host '=== 第 1/3 步：启用 WSL2 功能 ===' -ForegroundColor Cyan
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

Write-Host '=== 第 2/3 步：设置 WSL 默认版本 2 ==='
wsl.exe --set-default-version 2

Write-Host '=== 第 3/3 步：安装 Ubuntu ==='
wsl.exe --install -d Ubuntu

Write-Host ''
Write-Host '==============================================================' -ForegroundColor Green
Write-Host '如果提示需要重启，请先重启电脑，然后重新打开"Ubuntu"应用完成初始设置'
Write-Host '（设置用户名/密码），再运行 build_android.sh 打包'
Write-Host '==============================================================' -ForegroundColor Green
