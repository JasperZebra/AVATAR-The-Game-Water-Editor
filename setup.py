from cx_Freeze import setup, Executable
import os
import sys
from PIL import Image

def convert_png_to_ico(png_path, ico_path):
    # Open the PNG image
    img = Image.open(png_path)
    
    # Resize to standard icon sizes (16x16, 32x32, 48x48, 256x256)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
    
    # Save as ICO
    img.save(ico_path, format='ICO', sizes=icon_sizes)
    print(f"Converted {png_path} to {ico_path}")

# Convert water_editor_icon.png to water_editor_icon.ico if it exists
icon_png = 'assets/water_editor_icon.png'
icon_ico = 'water_editor_icon.ico'

if os.path.exists(icon_png):
    convert_png_to_ico(icon_png, icon_ico)
else:
    print(f"Warning: {icon_png} not found. Skipping icon conversion.")
    icon_ico = None

# Define the base directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Build options
build_options = {
    'include_files': [
        # Add any assets or icon files here if you have them
        # ('assets/water_editor_icon.png', 'assets/water_editor_icon.png'),
    ],
    'packages': [
        # Standard libraries
        'os', 'sys', 'tkinter', 'struct',
        
        # Tkinter related
        'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
    ],
    'excludes': [
        # Packages you want to exclude to reduce size
        'test', 'unittest', 'matplotlib', 'scipy', 'pandas', 'numpy',
        'xml', 'email', 'http', 'urllib', 'ssl', 'pydoc'
    ],
    'include_msvcr': True,  # Include Microsoft Visual C Runtime
}

# Set up the executable
executables = [
    Executable(
        'add_water.py',  # Your main script
        base='Win32GUI' if sys.platform == 'win32' else None,  # GUI application
        target_name='CSDat_Water_Editor.exe',  # Name of the final executable
        icon=icon_ico if icon_ico and os.path.exists(icon_ico) else None,  # Converted icon file
    )
]

# Setup
setup(
    name='CSDat Water Editor',
    version='1.0',
    description='CSDat Water Editor - Add and manage water blocks in sector files',
    author='Your Name',
    options={'build_exe': build_options},
    executables=executables
)

# python setup.py build