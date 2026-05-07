import cv2
import numpy as np
from pathlib import Path

img1_path = Path("dataset/images/new/autumn/CFD-WF-018-017-N.png")
img2_path = Path("dataset/CFD-WF-018-017-N.jpg")  # poza direct în dataset

print("Current working directory:", Path.cwd())
print("Img1 exists:", img1_path.exists(), img1_path)
print("Img2 exists:", img2_path.exists(), img2_path)

print("\nFiles directly inside dataset:")
for p in Path("dataset").iterdir():
    if p.is_file():
        print("-", p.name)

img1 = cv2.imread(str(img1_path), cv2.IMREAD_UNCHANGED)
img2 = cv2.imread(str(img2_path), cv2.IMREAD_UNCHANGED)

if img1 is None:
    raise ValueError(f"Nu pot citi prima imagine: {img1_path}")

if img2 is None:
    raise ValueError(f"Nu pot citi a doua imagine: {img2_path}")

print("Image 1 shape:", img1.shape)
print("Image 2 shape:", img2.shape)

if img1.shape != img2.shape:
    raise ValueError("Imaginile au dimensiuni/canale diferite. Nu pot compara pixel cu pixel.")

diff = np.abs(img1.astype(np.int16) - img2.astype(np.int16))

print("Pixels identical:", np.array_equal(img1, img2))
print("Mean difference:", diff.mean())
print("Max difference:", diff.max())