#!/bin/bash
# 在 WSL (Ubuntu) 内运行：先确保能访问 Windows 项目目录
# 用法: bash /mnt/c/Users/boyun/Documents/Default\ Project/AndroidPet/build_android.sh

set -e

echo "=== 1/4 安装构建依赖 ==="
sudo apt-get update -y
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev libffi-dev cmake \
    libncurses-dev

echo "=== 2/4 安装 buildozer ==="
pip3 install --upgrade pip
pip3 install buildozer cython --user

echo "=== 3/4 拷贝项目到 WSL 内（避免 drvfs 兼容问题）==="
SRC="/mnt/c/Users/boyun/Documents/Default Project/AndroidPet/android"
DEST="$HOME/AndroidPet"
rm -rf "$DEST"
mkdir -p "$DEST"
cp -r "$SRC/." "$DEST/"
cd "$DEST"

echo "=== 4/4 开始打包 APK（首次会下载 Android SDK/NDK，约 10 分钟+）==="
python3 -m buildozer android debug

echo ""
echo "=============================================================="
APK=$(find bin -name '*.apk' | head -1)
if [ -n "$APK" ]; then
    cp "$APK" "$SRC/dist_apk/"
    echo "打包完成！APK 已复制到:"
    echo "  C:\\Users\\boyun\\Documents\\Default Project\\AndroidPet\\dist_apk\\"
    echo "（可通过 Windows 文件管理器访问，拷贝到手机安装即可）"
else
    echo "打包失败，请查看上方错误信息"
fi
echo "=============================================================="
