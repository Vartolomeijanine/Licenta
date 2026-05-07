from pathlib import Path

# CHANGE ONLY THIS
SEASON = "winter"   # "autumn", "spring", "summer", "winter"

BASE_PATH = Path(r"C:\Users\Janine\Desktop\Licenta\backend\dataset\images\new")

CONFIG = {
    "autumn": {
        "folder": BASE_PATH / "autumn",
        "prefix": "AUT_CFD",
        "start": 48
    },
    "spring": {
        "folder": BASE_PATH / "spring",
        "prefix": "SPR_CFD",
        "start": 31
    },
    "summer": {
        "folder": BASE_PATH / "summer",
        "prefix": "SUM_CFD",
        "start": 40
    },
    "winter": {
        "folder": BASE_PATH / "winter",
        "prefix": "WIN",
        "start": 46
    },
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

cfg = CONFIG[SEASON]
folder = cfg["folder"]
prefix = cfg["prefix"]
start_index = cfg["start"]

images = sorted([
    file for file in folder.iterdir()
    if file.is_file()
    and file.suffix.lower() in IMAGE_EXTENSIONS
    and not file.stem.startswith(prefix)
])

print(f"Season: {SEASON}")
print(f"Folder: {folder}")
print(f"Found {len(images)} new images.")

for offset, image_path in enumerate(images):
    index = start_index + offset
    new_name = f"{prefix}_{index:04d}{image_path.suffix.lower()}"
    new_path = folder / new_name

    if new_path.exists():
        raise FileExistsError(f"File already exists: {new_path}")

    image_path.rename(new_path)
    print(f"{image_path.name} -> {new_name}")

print("Done.")