[app]

# Application name
title = MY SHOP

# Package
package.name = myshop
package.domain = org.myshop

# Source
source.dir = .
source.include_exts = py,json,png,jpg,jpeg,kv,atlas

# Version
version = 1.0

# Python / Kivy dependencies
requirements = python3,kivy

# Application orientation
orientation = portrait

# Fullscreen
fullscreen = 0


[buildozer]

# Buildozer logging
log_level = 2

# Allow running as root inside GitHub Actions container
warn_on_root = 1


[app:android]

# Android settings
android.api = 35
android.minapi = 21

# Accept Android SDK license
android.accept_sdk_license = True

# Android architecture
android.archs = arm64-v8a

# Android permissions
android.permissions = INTERNET


[buildozer:android]

# Keep Android build configuration explicit
android.ndk_api = 21
