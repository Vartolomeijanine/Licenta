from pathlib import Path
import pandas as pd

from coloranalysis.ai.color_features import ColorFeatureService


DATASET_DIR = Path("dataset")
IMAGES_ROOT = DATASET_DIR / "images" / "01_labeled_images"
LABELS_PATH = DATASET_DIR / "labels.csv"
OUTPUT_PATH = DATASET_DIR / "training_features.csv"

service = ColorFeatureService()


def clean_value(v):
    if pd.isna(v):
        return None
    value = str(v).strip().lower()
    return value if value else None


def get_season(row):
    return clean_value(row.get("season_label", row.get("season")))


def build_image_path(image_name: str, season: str) -> Path:
    return IMAGES_ROOT / season / image_name


def hue_distance(h1, h2):
    if h1 is None or h2 is None:
        return None
    diff = abs(h1 - h2)
    return round(min(diff, 360 - diff), 2)


def safe_diff(a, b):
    if a is None or b is None:
        return None
    return round(abs(a - b), 2)


def safe_ratio(a, b):
    if a is None or b is None or b == 0:
        return None
    return round(a / b, 4)


def safe_normalized_contrast(a, b):
    if a is None or b is None or max(a, b) == 0:
        return None
    return round(abs(a - b) / max(a, b), 4)


def safe_average(values, decimals=4):
    valid = [v for v in values if v is not None]
    if not valid:
        return None
    return round(sum(valid) / len(valid), decimals)


def process_row(row):
    image_name = str(row["image_name"]).strip()
    season = get_season(row)

    image_path = build_image_path(image_name, season)

    if not image_path.exists():
        print(f"{image_name}: MISSING | Expected path: {image_path}")
        return None

    is_hair_visible = clean_value(row.get("is_hair_visible", "yes")) or "yes"
    is_hair_natural = clean_value(row.get("is_hair_natural", "yes")) or "yes"
    natural_hair_color = clean_value(row.get("natural_hair_color"))

    result = service.extract_color_features(
        image_path=image_path,
        is_hair_visible=is_hair_visible,
        is_hair_natural=is_hair_natural,
        natural_hair_color=natural_hair_color,
    )

    if not result["success"]:
        reason = result.get("error") or result.get("message") or "Unknown error"
        print(f"{image_name}: FAILED | {reason}")
        return None

    skin = result["features"]["skin"]["aggregated_features"]
    eyes = result["features"]["eyes"]["aggregated_features"]
    hair = result["features"]["hair"]

    skin_L = skin["avg_skin_L"]
    skin_a = skin["avg_skin_a"]
    skin_b = skin["avg_skin_b_lab"]
    skin_C = skin["avg_skin_C"]
    skin_H = skin["avg_skin_H"]

    eye_L = eyes["avg_eye_L"] if eyes is not None else None
    eye_a = eyes["avg_eye_a"] if eyes is not None else None
    eye_b = eyes["avg_eye_b_lab"] if eyes is not None else None
    eye_C = eyes["avg_eye_C"] if eyes is not None else None
    eye_H = eyes["avg_eye_H"] if eyes is not None else None

    hair_L = None
    hair_a = None
    hair_b = None
    hair_C = None
    hair_H = None

    if hair["used_observed_hair"] and hair["hair_lab_lch"] is not None:
        hair_L = hair["hair_lab_lch"]["L"]
        hair_a = hair["hair_lab_lch"]["a"]
        hair_b = hair["hair_lab_lch"]["b"]
        hair_C = hair["hair_lab_lch"]["C"]
        hair_H = hair["hair_lab_lch"]["H"]

    # L contrast features
    skin_eye_L_diff = safe_diff(skin_L, eye_L)
    skin_hair_L_diff = safe_diff(skin_L, hair_L)
    eye_hair_L_diff = safe_diff(eye_L, hair_L)

    normalized_skin_eye_L_contrast = safe_normalized_contrast(skin_L, eye_L)
    normalized_skin_hair_L_contrast = safe_normalized_contrast(skin_L, hair_L)
    normalized_eye_hair_L_contrast = safe_normalized_contrast(eye_L, hair_L)

    overall_contrast_score = safe_average(
        [
            normalized_skin_eye_L_contrast,
            normalized_skin_hair_L_contrast,
            normalized_eye_hair_L_contrast,
        ],
        decimals=4,
    )

    # chroma features
    skin_eye_C_diff = safe_diff(skin_C, eye_C)
    skin_hair_C_diff = safe_diff(skin_C, hair_C)
    eye_hair_C_diff = safe_diff(eye_C, hair_C)

    skin_eye_C_ratio = safe_ratio(skin_C, eye_C)
    skin_hair_C_ratio = safe_ratio(skin_C, hair_C)
    eye_hair_C_ratio = safe_ratio(eye_C, hair_C)

    overall_chroma_score = safe_average(
        [skin_C, eye_C, hair_C],
        decimals=2,
    )

    # hue distance features
    skin_eye_H_diff = hue_distance(skin_H, eye_H)
    skin_hair_H_diff = hue_distance(skin_H, hair_H)
    eye_hair_H_diff = hue_distance(eye_H, hair_H)

    # warm/cool relation
    skin_eye_a_diff = safe_diff(skin_a, eye_a)
    skin_eye_b_diff = safe_diff(skin_b, eye_b)
    skin_hair_a_diff = safe_diff(skin_a, hair_a)
    skin_hair_b_diff = safe_diff(skin_b, hair_b)

    # extra simple descriptors
    eye_darkness = eyes["eye_darkness"] if eyes is not None else None
    hair_darkness = round(100 - hair_L, 2) if hair_L is not None else None
    skin_darkness = round(100 - skin_L, 2) if skin_L is not None else None

    features = {
        "image_name": image_name,
        "season": season,

        # skin RGB
        "avg_skin_r": skin["avg_skin_r"],
        "avg_skin_g": skin["avg_skin_g"],
        "avg_skin_b": skin["avg_skin_b"],

        # skin LAB/LCH
        "avg_skin_L": skin_L,
        "avg_skin_a": skin_a,
        "avg_skin_b_lab": skin_b,
        "avg_skin_C": skin_C,
        "avg_skin_H": skin_H,
        "skin_darkness": skin_darkness,

        # skin consistency
        "cheek_L_diff": skin["cheek_L_diff"],
        "cheek_a_diff": skin["cheek_a_diff"],
        "cheek_b_diff": skin["cheek_b_diff"],
        "cheek_C_diff": skin["cheek_C_diff"],
        "cheek_H_diff": skin["cheek_H_diff"],
        "forehead_vs_cheeks_L_diff": skin["forehead_vs_cheeks_L_diff"],
        "forehead_vs_cheeks_a_diff": skin["forehead_vs_cheeks_a_diff"],
        "forehead_vs_cheeks_b_diff": skin["forehead_vs_cheeks_b_diff"],
        "forehead_vs_cheeks_C_diff": skin["forehead_vs_cheeks_C_diff"],
        "forehead_vs_cheeks_H_diff": skin["forehead_vs_cheeks_H_diff"],

        # eye features
        "avg_eye_L": eye_L,
        "avg_eye_a": eye_a,
        "avg_eye_b_lab": eye_b,
        "avg_eye_C": eye_C,
        "avg_eye_H": eye_H,
        "eye_vs_skin_L_diff": eyes["eye_vs_skin_L_diff"] if eyes is not None else None,
        "eye_darkness": eye_darkness,

        # hair metadata
        "is_hair_visible": is_hair_visible,
        "is_hair_natural": is_hair_natural,
        "natural_hair_color": natural_hair_color,
        "used_observed_hair": hair["used_observed_hair"],

        # observed hair features
        "hair_L": hair_L,
        "hair_a": hair_a,
        "hair_b_lab": hair_b,
        "hair_C": hair_C,
        "hair_H": hair_H,
        "hair_darkness": hair_darkness,

        # L contrast / relative lightness
        "skin_eye_L_diff": skin_eye_L_diff,
        "skin_hair_L_diff": skin_hair_L_diff,
        "eye_hair_L_diff": eye_hair_L_diff,

        "normalized_skin_eye_L_contrast": normalized_skin_eye_L_contrast,
        "normalized_skin_hair_L_contrast": normalized_skin_hair_L_contrast,
        "normalized_eye_hair_L_contrast": normalized_eye_hair_L_contrast,
        "overall_contrast_score": overall_contrast_score,

        # chroma / saturation-like features
        "skin_eye_C_diff": skin_eye_C_diff,
        "skin_hair_C_diff": skin_hair_C_diff,
        "eye_hair_C_diff": eye_hair_C_diff,

        "skin_eye_C_ratio": skin_eye_C_ratio,
        "skin_hair_C_ratio": skin_hair_C_ratio,
        "eye_hair_C_ratio": eye_hair_C_ratio,
        "overall_chroma_score": overall_chroma_score,

        # hue relation
        "skin_eye_H_diff": skin_eye_H_diff,
        "skin_hair_H_diff": skin_hair_H_diff,
        "eye_hair_H_diff": eye_hair_H_diff,

        # LAB warm/cool relation
        "skin_eye_a_diff": skin_eye_a_diff,
        "skin_eye_b_diff": skin_eye_b_diff,
        "skin_hair_a_diff": skin_hair_a_diff,
        "skin_hair_b_diff": skin_hair_b_diff,
    }

    return features


def main():
    df = pd.read_csv(LABELS_PATH)
    df.columns = [str(c).strip().lower() for c in df.columns]

    total_initial = len(df)
    rows = []
    failed_count = 0

    for _, row in df.iterrows():
        result = process_row(row)

        if result is not None:
            rows.append(result)
        else:
            failed_count += 1

    output_df = pd.DataFrame(rows)
    output_df.to_csv(OUTPUT_PATH, index=False)

    print("\n==============================")
    print("DATASET BUILD SUMMARY")
    print("==============================")
    print(f"Initial images in labels.csv: {total_initial}")
    print(f"Successfully processed images: {len(output_df)}")
    print(f"Skipped / failed images: {failed_count}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("==============================")


if __name__ == "__main__":
    main()