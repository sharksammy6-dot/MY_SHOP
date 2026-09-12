[app]

title = MY SHOP
package.name = myshop
package.domain = org.myshop

source.dir = .
source.include_exts = py,json,png,jpg,jpeg,kv,atlas

version = 1.0

requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1

orientation = portrait
fullscreen = 0

p4a.branch = master


[buildozer]

log_level = 2
warn_on_root = 1

android.accept_sdk_license = True
android.api = 35
android.minapi = 21
