#!/usr/bin/env python3
"""Build script for packaging QuickTranslate into a desktop executable."""
import os
import sys
import subprocess
import shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def build_executable():
    print("=== 1. Starting PyInstaller Build ===")
    venv_pyinstaller = os.path.join(PROJECT_DIR, "venv", "bin", "pyinstaller")
    if not os.path.exists(venv_pyinstaller):
        venv_pyinstaller = "pyinstaller"

    cmd = [
        venv_pyinstaller,
        "--name=QuickTranslate",
        "--noconfirm",
        "--clean",
        "--windowed",
        f"--add-data={os.path.join(PROJECT_DIR, 'assets')}:assets",
        f"--icon={os.path.join(PROJECT_DIR, 'assets', 'icon.png')}",
        "--hidden-import=pynput.keyboard._xorg",
        "--hidden-import=pynput.mouse._xorg",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        os.path.join(PROJECT_DIR, "run.py")
    ]

    print("Running command:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=PROJECT_DIR)
    print("=== PyInstaller Build Completed Successfully! ===")

def create_desktop_entry():
    print("=== 2. Creating Linux Desktop Entry ===")
    dist_bin = os.path.join(PROJECT_DIR, "dist", "QuickTranslate", "QuickTranslate")
    icon_path = os.path.join(PROJECT_DIR, "assets", "icon.png")

    desktop_content = f"""[Desktop Entry]
Name=QuickTranslate
GenericName=极速桌面翻译
Comment=支持全局自定义快捷键、自动聚焦、标准发音、词性释义与双语例句的极速桌面翻译工具
Exec={dist_bin}
Icon={icon_path}
Terminal=false
Type=Application
Categories=Utility;Translation;Education;
StartupNotify=true
"""
    desktop_file = os.path.join(PROJECT_DIR, "quicktranslate.desktop")
    with open(desktop_file, "w", encoding="utf-8") as f:
        f.write(desktop_content)
    os.chmod(desktop_file, 0o755)
    print(f"Desktop entry created at: {desktop_file}")

    # Optionally copy to ~/.local/share/applications so it appears in system app launcher
    user_apps_dir = os.path.expanduser("~/.local/share/applications")
    if os.path.exists(user_apps_dir):
        dest_desktop = os.path.join(user_apps_dir, "quicktranslate.desktop")
        shutil.copy2(desktop_file, dest_desktop)
        print(f"Installed desktop shortcut to: {dest_desktop}")

if __name__ == "__main__":
    build_executable()
    create_desktop_entry()
    print("\n🎉 All Done! Executable is located at: dist/QuickTranslate/QuickTranslate")
