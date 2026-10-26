[app]

title = Security Voice Command AI
package.name = securityassistant
package.domain = org.securityai

source.dir = .
source.include_exts = py,kv,png,jpg,atlas

version = 0.1

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 23

android.archs = arm64-v8a

android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
