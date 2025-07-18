"""
setup.py for building the FFmpeg Mixer App with py2app.

To build the app:
1. Make sure you have py2app installed: pip install py2app
2. Download the FFmpeg binary for macOS and place it in the same directory as this setup.py file.
   You can get it from https://ffmpeg.org/download.html or via Homebrew (`brew install ffmpeg`).
   Extract the downloaded archive and find the ffmpeg executable file (it's usually inside a bin folder).
   https://ffbinaries.com/downloads
3. Run: python setup.py py2app
"""

from setuptools import setup

# Define the main script of your application
APP = ['mix2kmac_dragdrop2.py'] # Assuming your Python script is named main.py

# Define any additional data files that need to be included in the app bundle.
# This is crucial for including the FFmpeg binary.
# The 'ffmpeg' binary will be placed in the 'Contents/Resources' directory of the app bundle.
DATA_FILES = [
    ('Resources', ['ffmpeg']) # (destination_folder_in_bundle, [source_file_paths])
]

# Options for py2app
OPTIONS = {
    'argv_emulation': True, # Allows arguments to be passed to the app
    'iconfile': 'app_icon.icns', # Optional: Path to your .icns icon file
    'plist': { # Info.plist customization
        'CFBundleName': 'FFmpeg Mixer',
        'CFBundleDisplayName': 'FFmpeg Mixer',
        'CFBundleGetInfoString': 'FFmpeg Video and Audio Mixer',
        'CFBundleIdentifier': 'com.yourcompany.ffmpegmixer', # Change this to your unique identifier
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': '© 2024 Your Name/Company',
        # Add LSUIElement to make it a menubar app if desired (not typical for this app)
        # 'LSUIElement': True,
    },
    'packages': ['tkinter'], # Explicitly include tkinter if py2app misses it
    'includes': ['os', 'subprocess', 'sys', 'tkinter', 'tkinter.filedialog', 'tkinter.messagebox'], # Explicitly include modules
    'excludes': [], # Exclude modules you don't need to reduce size
    'optimize': 2, # Optimize bytecode
    'bdist_base': 'build', # Directory for intermediate build files
    'dist_dir': 'dist', # Directory where the final .app bundle will be created
    'emulate_shell_environment': False, # Avoid issues with PATH in bundled apps
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
