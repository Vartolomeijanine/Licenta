import sys
from pathlib import Path
import cv2

from coloranalysis.ai.predictor import SeasonPredictorService
from coloranalysis.ai.color_features import ColorFeatureService


def save_region_crops(image_path: str, out_dir: Path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not load image: {image_path}")
        return

    cf = ColorFeatureService()
    regions_res = cf.region_service.extract_regions(image_path)
    if not regions_res.get("success"):
        print("Region extraction failed:", regions_res)
        return

    regions = regions_res["regions"]
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, region in regions.items():
        x1, y1, x2, y2 = region["x1"], region["y1"], region["x2"], region["y2"]
        crop = image[y1:y2, x1:x2]
        path = out_dir / f"crop_{name}.jpg"
        cv2.imwrite(str(path), crop)
        print(f"Saved region {name} -> {path}")


def debug_image(image_path: str):
    predictor = SeasonPredictorService()
    print("Running feature extraction and prediction for:", image_path)
    res = predictor.feature_service.extract_color_features(image_path)

    if not res.get("success"):
        print("Feature extraction failed:", res)
        return

    features = res["features"]
    agg = features["skin"]["aggregated_features"]

    print("Aggregated skin features:")
    for k, v in agg.items():
        print(f"  {k}: {v}")

    print("Patch counts:")
    print(f"  left_cheek: {features['skin']['left_cheek_patch_count']}")
    print(f"  right_cheek: {features['skin']['right_cheek_patch_count']}")
    print(f"  forehead: {features['skin']['forehead_patch_count']}")
    print(f"  total_valid_patch_count: {features['skin']['total_valid_patch_count']}")

    print("Running model-backed prediction:")
    pred_res = predictor.predict_from_image(image_path)
    print(pred_res.get("prediction"))

    out = Path("debug_outputs") / Path(image_path).stem
    save_region_crops(image_path, out)
    print("Wrote debug crops to:", out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python debug_prediction.py path/to/image.jpg")
        sys.exit(1)

    img = sys.argv[1]
    debug_image(img)
