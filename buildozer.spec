[app]
title = Security Assistant
package.name = securityassistant
package.domain = org.securityai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 11.0.0
android.numeric_version = 110000

requirements = python3,kivy,plyer,cryptography

orientation = portrait
fullscreen = 0

icon.filename = assets/icon.png

android.permissions = INTERNET,FOREGROUND_SERVICE
android.add_src = android_src

p4a.branch = develop
android.accept_sdk_license = True
android.api = 35
android.minapi = 24
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
