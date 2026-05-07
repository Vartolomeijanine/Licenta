from pathlib import Path
import cv2

INPUT_DIR = Path("dataset/images/new")

cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)


def crop_face_inplace(image_path: Path) -> bool:
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

    if image is None:
        print(f"{image_path.name}: FAILED | Could not read image")
        return False

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=3,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        print(f"{image_path.name}: FAILED | No face detected")
        return False

    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

    img_h, img_w = image.shape[:2]

    # padding optim pentru analiză cromatică
    pad_x = int(w * 0.22)
    pad_top = int(h * 0.35)
    pad_bottom = int(h * 0.18)

    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_top)
    x2 = min(img_w, x + w + pad_x)
    y2 = min(img_h, y + h + pad_bottom)

    cropped = image[y1:y2, x1:x2]

    if cropped.size == 0:
        print(f"{image_path.name}: FAILED | Empty crop")
        return False

    # suprascrie aceeași imagine
    success = cv2.imwrite(str(image_path), cropped)

    if not success:
        print(f"{image_path.name}: FAILED | Save error")
        return False

    print(f"{image_path.name}: OK")
    return True


def main():
    image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]

    image_paths = []
    for ext in image_extensions:
        image_paths.extend(INPUT_DIR.rglob(ext))

    total = len(image_paths)
    success = 0
    failed = 0

    for image_path in image_paths:
        if crop_face_inplace(image_path):
            success += 1
        else:
            failed += 1

    print("\n==============================")
    print("CROP SUMMARY")
    print("==============================")
    print(f"Processed: {total}")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print("==============================")


if __name__ == "__main__":
    main()