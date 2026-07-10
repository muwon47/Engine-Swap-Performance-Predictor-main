import os
import shutil
import glob
from app.server import main

def copy_generated_images():
    base_path = os.path.expanduser('~/.gemini/antigravity/brain/178886d5-6a74-486a-9f19-ebacff0daff1')
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    files = {
        'mx5_na*.png': 'mx5_na.webp',
        'supra_jza80*.png': 'supra_jza80.webp',
        'brz*.png': 'brz.webp',
        's13*.png': 's13.webp',
        'e36*.png': 'e36.webp',
        'k20a*.png': 'k20a.webp',
        '2jz*.png': '2jz.webp',
        'ls3*.png': 'ls3.webp'
    }
    for pattern, dest_name in files.items():
        matches = glob.glob(os.path.join(base_path, pattern))
        if matches:
            shutil.copy(matches[-1], os.path.join(static_path, dest_name))

if __name__ == "__main__":
    copy_generated_images()
    main()
