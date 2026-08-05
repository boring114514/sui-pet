[app]
title = 猴子宠物
package.name = monkeypet
package.domain = org.example
source.dir = .
source.include_exts = py,png,kv,atlas
source.exclude_dirs = test,__pycache__,bin
version = 1.0.0
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
icon.filename = assets/icon.png
presplash.filename = assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
