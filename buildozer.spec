
[app]
android.permissions = INTERNET,RECORD_AUDIO
p4a.branch = develop
title = Security Voice Command AI
package.name = securityassistant
package.domain = org.securityai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1
requirements = python3,kivy,plyer,cryptography
orientation = portrait
fullscreen = 0
android.accept_sdk_license = True
android.api = 35
android.minapi = 24
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1

