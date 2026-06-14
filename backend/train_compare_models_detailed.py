from pathlib import Path
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC


DATASET_PATH = Path("dataset/training_features.csv")
BEST_MODEL_PATH = Path("dataset/best_season_model.pkl")


def add_final_features(df):
    EPS = 1e-6

    # ==============================
    # CONTRAST FEATURES
    # ==============================

    df["true_lightness_range"] = (
        df[["avg_skin_L", "avg_eye_L", "hair_L"]].max(axis=1)
        - df[["avg_skin_L", "avg_eye_L", "hair_L"]].min(axis=1)
    )

    df["normalized_true_contrast"] = (
        df["true_lightness_range"] / (df["avg_skin_L"] + EPS)
    )

    df["global_contrast"] = (
        df["skin_eye_L_diff"].fillna(0)
        + df["skin_hair_L_diff"].fillna(0)
        + df["eye_hair_L_diff"].fillna(0)
    ) / 3

    df["hair_skin_lightness_ratio"] = df["hair_L"] / (df["avg_skin_L"] + EPS)
    df["eye_skin_lightness_ratio"] = df["avg_eye_L"] / (df["avg_skin_L"] + EPS)

    df["hair_skin_darkness_diff"] = df["hair_darkness"] - df["skin_darkness"]

    # ==============================
    # CHROMA / SATURATION FEATURES
    # ==============================

    df["chroma_balance"] = (
        df["avg_skin_C"].fillna(0)
        + df["avg_eye_C"].fillna(0)
        + df["hair_C"].fillna(0)
    ) / 3

    df["overall_chroma_score"] = df["chroma_balance"]

    df["eye_skin_chroma_ratio"] = df["avg_eye_C"] / (df["avg_skin_C"] + EPS)
    df["hair_skin_chroma_ratio"] = df["hair_C"] / (df["avg_skin_C"] + EPS)

    # ==============================
    # WARM / COOL FEATURES
    # ==============================

    df["skin_undertone_index"] = df["avg_skin_b_lab"] / (
        df["avg_skin_a"].abs() + EPS
    )

    df["warm_cool_score"] = (
        df["avg_skin_b_lab"].fillna(0)
        + df["avg_eye_b_lab"].fillna(0)
        + df["hair_b_lab"].fillna(0)
    ) / 3

    df["a_axis_balance"] = (
        df["avg_skin_a"].fillna(0)
        + df["avg_eye_a"].fillna(0)
        + df["hair_a"].fillna(0)
    ) / 3

    df["warm_vs_cool_skin"] = df["avg_skin_b_lab"] - df["avg_skin_a"]

    df["skin_eye_warmth_diff"] = df["avg_skin_b_lab"] - df["avg_eye_b_lab"]
    df["skin_hair_warmth_diff"] = df["avg_skin_b_lab"] - df["hair_b_lab"]
    df["hair_skin_warmth_diff"] = df["hair_b_lab"] - df["avg_skin_b_lab"]

    return df


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

    return preprocessor, numeric_features, categorical_features


def print_feature_importance(pipeline, numeric_features, categorical_features):
    classifier = pipeline.named_steps["classifier"]

    if not hasattr(classifier, "feature_importances_"):
        return

    feature_names = list(numeric_features)

    if categorical_features:
        encoder = pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["encoder"]
        feature_names.extend(list(encoder.get_feature_names_out(categorical_features)))

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": classifier.feature_importances_,
    }).sort_values(by="importance", ascending=False)

    print("\n==============================")
    print("TOP FEATURE IMPORTANCES")
    print("==============================")
    print(importance_df.head(30).to_string(index=False))


def evaluate_holdout(
    name,
    model,
    X_train,
    y_train,
    X_val,
    y_val,
    X_test,
    y_test,
    numeric_features,
    categorical_features,
):
    model.fit(X_train, y_train)

    if name in ["Random Forest", "Extra Trees"]:
        print_feature_importance(model, numeric_features, categorical_features)

    val_pred = model.predict(X_val)
    test_pred = model.predict(X_test)

    val_accuracy = accuracy_score(y_val, val_pred)
    test_accuracy = accuracy_score(y_test, test_pred)

    print("\n==============================")
    print(f"MODEL: {name}")
    print("==============================")
    print(f"Validation accuracy: {val_accuracy:.4f}")
    print(f"Test accuracy: {test_accuracy:.4f}")

    print("\nClassification report on TEST:")
    print(classification_report(y_test, test_pred))

    print("\nConfusion matrix on TEST:")
    print(confusion_matrix(y_test, test_pred, labels=model.classes_))

    print("\nClass order:")
    print(list(model.classes_))

    return {
        "name": name,
        "model": model,
        "val_accuracy": val_accuracy,
        "test_accuracy": test_accuracy,
    }


def evaluate_cv(name, classifier, X, y):
    X_cv = X.copy()
    preprocessor, _, _ = build_preprocessor(X_cv)

    if name in ["SVM", "Logistic Regression"]:
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

    return scores


def main():
    df = pd.read_csv(DATASET_PATH)
    #df = add_final_features(df)

    print("\n==============================")
    print("DATASET INFO")
    print("==============================")
    print(f"Total samples: {len(df)}")
    print(df["season"].value_counts())

    target_column = "season"

    # excluded_features = [
    #     "image_name",
    #     target_column,

    #     # hue features removed because they are unstable under lighting changes
    #     "avg_skin_H",
    #     "avg_eye_H",
    #     "hair_H",
    #     "skin_eye_H_diff",
    #     "skin_hair_H_diff",
    #     "eye_hair_H_diff",
    #     "cheek_H_diff",
    #     "forehead_vs_cheeks_H_diff",
    # ]

    # selected_features = [
    #     col for col in df.columns
    #     if col not in excluded_features
    # ]

    # print("\n==============================")
    # print("FEATURE INFO")
    # print("==============================")
    # print(f"Selected features: {len(selected_features)}")
    # print(selected_features)

    # X = df[selected_features].copy()
    # y = df[target_column]

    if "image_name" in df.columns:
        X = df.drop(columns=["image_name", target_column]).copy()
    else:
        X = df.drop(columns=[target_column]).copy()

    y = df[target_column].astype(str)

    print("\n==============================")
    print("FEATURE INFO")
    print("==============================")
    print(f"Selected features: {len(X.columns)}")
    print(list(X.columns))        

    categorical_cols = [
        "is_hair_visible",
        "is_hair_natural",
        "natural_hair_color",
        "used_observed_hair",
    ]

    for col in categorical_cols:
        if col in X.columns:
            X[col] = X[col].astype("string").fillna("missing")

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.25,
        random_state=42,
        stratify=y_train_val,
    )

    print("\n==============================")
    print("SPLIT INFO")
    print("==============================")
    print(f"Train samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}")

    preprocessor, numeric_features, categorical_features = build_preprocessor(X.copy())

    models = {
        "Extra Trees": ExtraTreesClassifier(
            n_estimators=1000,
            max_features=0.6,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=700,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features="sqrt",
            bootstrap=True,
            class_weight="balanced_subsample",
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
            probability=True,
        ),

        "Logistic Regression": LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
        ),
    }

    print("\n==============================")
    print("5-FOLD CROSS-VALIDATION")
    print("==============================")

    cv_results = []

    for name, classifier in models.items():
        scores = evaluate_cv(name, classifier, X.copy(), y)

        print(f"\n{name}")
        print(f"CV scores: {scores}")
        print(f"Mean accuracy: {scores.mean():.4f}")
        print(f"Std: {scores.std():.4f}")

        cv_results.append({
            "name": name,
            "mean_accuracy": scores.mean(),
            "std": scores.std(),
        })

    print("\n==============================")
    print("HOLDOUT EVALUATION")
    print("==============================")

    holdout_results = []

    for name, classifier in models.items():
        if name in ["SVM", "Logistic Regression"]:
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

        result = evaluate_holdout(
            name,
            pipeline,
            X_train,
            y_train,
            X_val,
            y_val,
            X_test,
            y_test,
            numeric_features,
            categorical_features,
        )

        holdout_results.append(result)

    best_holdout = max(holdout_results, key=lambda item: item["val_accuracy"])

    print("\n==============================")
    print("BEST HOLDOUT MODEL BY VALIDATION")
    print("==============================")
    print(f"Best model: {best_holdout['name']}")
    print(f"Validation accuracy: {best_holdout['val_accuracy']:.4f}")
    print(f"Test accuracy: {best_holdout['test_accuracy']:.4f}")

    joblib.dump(best_holdout["model"], BEST_MODEL_PATH)

    print("\n==============================")
    print("BEST MODEL SAVED")
    print("==============================")
    print(f"Saved to: {BEST_MODEL_PATH}")

    cv_summary = pd.DataFrame(cv_results).sort_values(
        by="mean_accuracy",
        ascending=False,
    )

    print("\n==============================")
    print("CV SUMMARY")
    print("==============================")
    print(cv_summary.to_string(index=False))


if __name__ == "__main__":
    main()