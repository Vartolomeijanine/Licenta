from pathlib import Path
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC


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

    df["global_L_range"] = df[["avg_skin_L", "avg_eye_L", "hair_L"]].max(axis=1) - df[
        ["avg_skin_L", "avg_eye_L", "hair_L"]
    ].min(axis=1)

    df["warm_vs_cool_skin"] = df["avg_skin_b_lab"] - df["avg_skin_a"]

    df["eye_skin_chroma_ratio"] = df["avg_eye_C"] / (df["avg_skin_C"] + EPS)
    df["hair_skin_chroma_ratio"] = df["hair_C"] / (df["avg_skin_C"] + EPS)

    df["eye_skin_lightness_ratio"] = df["avg_eye_L"] / (df["avg_skin_L"] + EPS)
    df["hair_skin_lightness_ratio"] = df["hair_L"] / (df["avg_skin_L"] + EPS)

    df["hair_skin_darkness_diff"] = df["hair_darkness"] - df["skin_darkness"]

    return df


def get_feature_sets(df):
    baseline_skin = [
        col for col in df.columns
        if col.startswith("avg_skin_")
        or col.startswith("cheek_")
        or col.startswith("forehead_vs_cheeks_")
    ]

    unstable_hue_features = [
        "skin_eye_H_diff",
        "skin_hair_H_diff",
        "eye_hair_H_diff",
    ]

    engineered_final = [
        col for col in df.columns
        if col not in ["image_name", "season"]
        and col not in unstable_hue_features
    ]

    engineered_no_metadata = [
        col for col in engineered_final
        if col not in [
            "is_hair_visible",
            "is_hair_natural",
            "natural_hair_color",
            "used_observed_hair",
        ]
    ]

    return {
        "baseline_skin_only": baseline_skin,
        "engineered_no_metadata": engineered_no_metadata,
        "engineered_final_all": engineered_final,
    }


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


def build_models():
    return {
        "Random Forest": RandomForestClassifier(
            n_estimators=800,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),

        "Extra Trees": ExtraTreesClassifier(
            n_estimators=800,
            max_features="sqrt",
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),

        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=250,
            learning_rate=0.03,
            max_depth=3,
            random_state=42,
        ),

        "SVM": SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            class_weight="balanced",
        ),
    }


def evaluate(df, feature_set_name, selected_features, model_name, classifier):
    X = df[selected_features].copy()
    y = df["season"]

    preprocessor = build_preprocessor(X)

    if model_name == "SVM":
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("scaler", StandardScaler(with_mean=False)),
            ("classifier", classifier),
        ])
    else:
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ])

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    scores = cross_val_score(
        pipeline,
        X,
        y,
        cv=cv,
        scoring="accuracy",
        error_score="raise",
    )

    return {
        "feature_set": feature_set_name,
        "model": model_name,
        "num_features": len(selected_features),
        "mean_accuracy": scores.mean(),
        "std": scores.std(),
        "scores": scores,
    }


def main():
    df = pd.read_csv(DATASET_PATH)
    df = add_final_features(df)

    print("\n==============================")
    print("DATASET INFO")
    print("==============================")
    print(f"Total samples: {len(df)}")
    print(df["season"].value_counts())

    feature_sets = get_feature_sets(df)
    models = build_models()

    results = []

    for feature_set_name, selected_features in feature_sets.items():
        for model_name, classifier in models.items():
            result = evaluate(
                df,
                feature_set_name,
                selected_features,
                model_name,
                classifier,
            )

            results.append(result)

            print("\n==============================")
            print(f"FEATURE SET: {feature_set_name}")
            print(f"MODEL: {model_name}")
            print("==============================")
            print(f"Features: {result['num_features']}")
            print(f"CV scores: {result['scores']}")
            print(f"Mean accuracy: {result['mean_accuracy']:.4f}")
            print(f"Std: {result['std']:.4f}")

    summary = pd.DataFrame([
        {
            "feature_set": r["feature_set"],
            "model": r["model"],
            "num_features": r["num_features"],
            "mean_accuracy": round(r["mean_accuracy"], 4),
            "std": round(r["std"], 4),
        }
        for r in results
    ])

    summary = summary.sort_values(
        by="mean_accuracy",
        ascending=False,
    )

    print("\n==============================")
    print("FINAL SUMMARY")
    print("==============================")
    print(summary.to_string(index=False))

    summary.to_csv("dataset/final_cv_summary.csv", index=False)
    print("\nSaved summary to: dataset/final_cv_summary.csv")


if __name__ == "__main__":
    main()