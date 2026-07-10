import shutil
import glob
import os

base_path = os.path.expanduser('~/.gemini/antigravity/brain/178886d5-6a74-486a-9f19-ebacff0daff1')
static_path = '/Users/adityak/Desktop/mini_project/static'

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
        shutil.copy(matches[0], os.path.join(static_path, dest_name))
        print(f"Copied {matches[0]} to {dest_name}")
    else:
        print(f"No match found for {pattern}")
