from pathlib import Path
import shutil

SOURCE_DIR = Path(r"C:\Users\Janine\Downloads\cfd\cfd\CFD Version 3.0\Images\CFD\LATINA MALE")
OUTPUT_DIR = Path(r"C:\Users\Janine\Downloads\cfd\cfd\CFD Version 3.0\Images\CFD\LATINA MALE ALL")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

copied = 0
skipped = 0

for file_path in SOURCE_DIR.rglob("*"):
    if file_path.name == ".DS_Store":
        skipped += 1
        continue

    if not file_path.is_file():
        continue

    if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
        skipped += 1
        continue

    new_name = file_path.name
    destination = OUTPUT_DIR / new_name

    shutil.copy2(file_path, destination)
    copied += 1

print("==============================")
print("DONE")
print("==============================")
print(f"Source: {SOURCE_DIR}")
print(f"Copied images: {copied}")
print(f"Skipped files: {skipped}")
print(f"Saved in: {OUTPUT_DIR}")
print("==============================")