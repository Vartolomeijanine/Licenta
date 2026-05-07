from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


DATASET_PATH = Path("dataset/training_features.csv")


def add_final_features(df):
    EPS = 1e-6

    df["skin_undertone_index"] = df["avg_skin_b_lab"] / (df["avg_skin_a"].abs() + EPS)

    df["warm_cool_score"] = (
        df["avg_skin_b_lab"]
        + df["avg_eye_b_lab"].fillna(0)
        + df["hair_b_lab"].fillna(0)
    ) / 3

    df["a_axis_balance"] = (
        df["avg_skin_a"]
        + df["avg_eye_a"].fillna(0)
        + df["hair_a"].fillna(0)
    ) / 3

    df["global_contrast"] = (
        df["skin_eye_L_diff"].fillna(0)
        + df["skin_hair_L_diff"].fillna(0)
        + df["eye_hair_L_diff"].fillna(0)
    ) / 3

    df["global_L_range"] = (
        df[["avg_skin_L", "avg_eye_L", "hair_L"]].max(axis=1)
        - df[["avg_skin_L", "avg_eye_L", "hair_L"]].min(axis=1)
    )

    df["warm_vs_cool_skin"] = df["avg_skin_b_lab"] - df["avg_skin_a"]

    df["eye_skin_chroma_ratio"] = df["avg_eye_C"] / (df["avg_skin_C"] + EPS)
    df["hair_skin_chroma_ratio"] = df["hair_C"] / (df["avg_skin_C"] + EPS)

    df["eye_skin_lightness_ratio"] = df["avg_eye_L"] / (df["avg_skin_L"] + EPS)
    df["hair_skin_lightness_ratio"] = df["hair_L"] / (df["avg_skin_L"] + EPS)

    df["hair_skin_darkness_diff"] = df["hair_darkness"] - df["skin_darkness"]

    return df


def season_to_temperature(season):
    if season in ["spring", "autumn"]:
        return "warm"
    if season in ["summer", "winter"]:
        return "cool"
    raise ValueError(f"Unknown season: {season}")


def build_preprocessor(X):
    categorical_features = [
        "is_hair_visible",
        "is_hair_natural",
        "natural_hair_color",
        "used_observed_hair",
    ]

    categorical_features = [c for c in categorical_features if c in X.columns]

    for col in categorical_features:
        X[col] = X[col].astype("string").fillna("missing")

    numeric_features = [c for c in X.columns if c not in categorical_features]

    for col in numeric_features:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])

    categorical_transformer = Pipeline([
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ])

    return preprocessor


def build_model():
    return Pipeline([
        ("preprocessor", None),
        ("classifier", ExtraTreesClassifier(
            n_estimators=800,
            max_features="sqrt",
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])


def make_pipeline(X):
    preprocessor = build_preprocessor(X)
    model = build_model()
    model.set_params(preprocessor=preprocessor)
    return model


def main():
    df = pd.read_csv(DATASET_PATH)
    df = add_final_features(df)

    df["temperature"] = df["season"].apply(season_to_temperature)

    unstable_hue_features = [
        "skin_eye_H_diff",
        "skin_hair_H_diff",
        "eye_hair_H_diff",
    ]

    feature_cols = [
        col for col in df.columns
        if col not in ["image_name", "season", "temperature"]
        and col not in unstable_hue_features
    ]

    X = df[feature_cols].copy()
    y_final = df["season"]
    y_temp = df["temperature"]

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    all_true = []
    all_pred = []

    fold_accuracies = []

    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y_final), start=1):
        X_train = X.iloc[train_idx].copy()
        X_test = X.iloc[test_idx].copy()

        y_train_final = y_final.iloc[train_idx].copy()
        y_test_final = y_final.iloc[test_idx].copy()

        y_train_temp = y_temp.iloc[train_idx].copy()

        # ==========================
        # STEP 1: warm vs cool model
        # ==========================
        temp_model = make_pipeline(X_train.copy())
        temp_model.fit(X_train, y_train_temp)

        pred_temp = temp_model.predict(X_test)

        # ==========================
        # STEP 2A: warm model
        # spring vs autumn
        # ==========================
        warm_mask_train = y_train_temp == "warm"
        X_train_warm = X_train[warm_mask_train].copy()
        y_train_warm = y_train_final[warm_mask_train].copy()

        warm_model = make_pipeline(X_train_warm.copy())
        warm_model.fit(X_train_warm, y_train_warm)

        # ==========================
        # STEP 2B: cool model
        # summer vs winter
        # ==========================
        cool_mask_train = y_train_temp == "cool"
        X_train_cool = X_train[cool_mask_train].copy()
        y_train_cool = y_train_final[cool_mask_train].copy()

        cool_model = make_pipeline(X_train_cool.copy())
        cool_model.fit(X_train_cool, y_train_cool)

        # ==========================
        # FINAL PREDICTION
        # ==========================
        final_preds = []

        for i, temp in enumerate(pred_temp):
            sample = X_test.iloc[[i]].copy()

            if temp == "warm":
                pred = warm_model.predict(sample)[0]
            else:
                pred = cool_model.predict(sample)[0]

            final_preds.append(pred)

        acc = accuracy_score(y_test_final, final_preds)
        fold_accuracies.append(acc)

        all_true.extend(list(y_test_final))
        all_pred.extend(final_preds)

        print(f"Fold {fold} accuracy: {acc:.4f}")

    print("\n==============================")
    print("TWO-STEP CLASSIFIER RESULTS")
    print("==============================")
    print("CV scores:", np.array(fold_accuracies))
    print(f"Mean accuracy: {np.mean(fold_accuracies):.4f}")
    print(f"Std: {np.std(fold_accuracies):.4f}")

    print("\nClassification report:")
    print(classification_report(all_true, all_pred))

    print("\nConfusion matrix:")
    labels = ["autumn", "spring", "summer", "winter"]
    print(confusion_matrix(all_true, all_pred, labels=labels))

    print("\nClass order:")
    print(labels)


if __name__ == "__main__":
    main()