from setuptools import setup

APP = ['mix2kmac.py']
DATA_FILES = [('',['ffmpeg'])]  # Include FFmpeg binary in the bundle
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter'],
    'iconfile': None,  # Add .icns file if you have one for macOS app icon
    'plist': {
        'CFBundleName': 'Mix2kmac',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.indexbox.mix2kmac',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)