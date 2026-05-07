from pathlib import Path
import pandas as pd


INPUT_PATH = Path("dataset/training_features.csv")
OUTPUT_PATH = Path("dataset/training_features_filtered.csv")
REMOVED_PATH = Path("dataset/removed_ambiguous_samples.csv")


def is_ambiguous(row):
    season = row["season"]

    skin_hair_contrast = row.get("skin_hair_L_diff")
    overall_contrast = row.get("overall_contrast_score")
    skin_c = row.get("avg_skin_C")
    hair_l = row.get("hair_L")

    if pd.isna(overall_contrast):
        return False

    if season == "winter":
        if not pd.isna(skin_hair_contrast) and skin_hair_contrast < 3:
            return True
        if not pd.isna(overall_contrast) and overall_contrast < 0.03:
            return True

    if season == "summer":
        if not pd.isna(overall_contrast) and overall_contrast > 0.70:
            return True
        if not pd.isna(skin_c) and skin_c > 55:
            return True

    if season == "autumn":
        if not pd.isna(overall_contrast) and overall_contrast > 0.75:
            return True
        if not pd.isna(skin_hair_contrast) and skin_hair_contrast > 80:
            return True

    if season == "spring":
        if not pd.isna(hair_l) and hair_l < 5:
            return True
        if not pd.isna(overall_contrast) and overall_contrast > 0.75:
            return True

    return False


def main():
    df = pd.read_csv(INPUT_PATH)

    print("\n==============================")
    print("BEFORE FILTERING")
    print("==============================")
    print(f"Total samples: {len(df)}")
    print(df["season"].value_counts())

    df["is_ambiguous"] = df.apply(is_ambiguous, axis=1)

    removed_df = df[df["is_ambiguous"]].copy()
    filtered_df = df[~df["is_ambiguous"]].copy()

    removed_df.to_csv(REMOVED_PATH, index=False)
    filtered_df.drop(columns=["is_ambiguous"]).to_csv(OUTPUT_PATH, index=False)

    print("\n==============================")
    print("REMOVED AMBIGUOUS")
    print("==============================")
    print(f"Removed samples: {len(removed_df)}")
    print(removed_df["season"].value_counts())

    print("\n==============================")
    print("AFTER FILTERING")
    print("==============================")
    print(f"Remaining samples: {len(filtered_df)}")
    print(filtered_df["season"].value_counts())

    print("\nSaved filtered dataset to:")
    print(OUTPUT_PATH)

    print("\nSaved removed samples to:")
    print(REMOVED_PATH)


if __name__ == "__main__":
    main()