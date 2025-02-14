import PyInstaller.__main__
import subprocess
import sys

def install_pillow():
    """安装 Pillow 库"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])

def build_executable():
    """构建可执行文件"""
    PyInstaller.__main__.run([
        'Main.py',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',
        '--add-data=icon.ico;.',
        '--name=Auto Piano v1.0',
        '--manifest=app.manifest'
    ])

if __name__ == "__main__":
    try:
        import PIL
    except ImportError:
        install_pillow()
    build_executable()