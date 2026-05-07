import cv2
from pathlib import Path

BASE_DIR = Path("dataset/images/new")

VALID_EXTENSIONS = [".jpg", ".jpeg", ".JPG", ".JPEG"]

for img_path in BASE_DIR.rglob("*"):
    if img_path.suffix not in VALID_EXTENSIONS:
        continue

    img = cv2.imread(str(img_path))

    if img is None:
        print(f"Skipped, could not read: {img_path}")
        continue

    png_path = img_path.with_suffix(".png")

    success = cv2.imwrite(str(png_path), img)

    if success:
        img_path.unlink()
        print(f"Converted and deleted original: {img_path.name} -> {png_path.name}")
    else:
        print(f"Failed to save PNG for: {img_path}")

print("Done. All JPG/JPEG images were converted to PNG.")