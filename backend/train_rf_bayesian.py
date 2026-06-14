from pathlib import Path
import joblib
import optuna
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = Path("dataset/training_features.csv")
MODEL_PATH = Path("dataset/season_random_forest_bayesian_cv.pkl")
CONFUSION_MATRIX_PATH = Path("dataset/confusion_matrix_rf_bayesian_cv.png")
CV_RESULTS_PATH = Path("dataset/optuna_rf_cv_results.csv")

TARGET_COL = "season"
NAME_COL = "image_name"

RANDOM_STATE = 42
N_TRIALS = 100
N_SPLITS = 5


def main():
    print("\nSCRIPT STARTED")
    print("==============================")

    # ============================================================
    # 1. LOAD DATASET
    # ============================================================

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH.resolve()}")

    df = pd.read_csv(DATASET_PATH)

    print("\n==============================")
    print("DATASET INFO")
    print("==============================")
    print(f"Dataset path: {DATASET_PATH.resolve()}")
    print(f"Total samples: {len(df)}")

    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column '{TARGET_COL}' not found in dataset.")

    print("\nClass distribution:")
    print(df[TARGET_COL].value_counts())

    # ============================================================
    # 2. PREPARE FEATURES AND TARGET
    # ============================================================

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    if NAME_COL in X.columns:
        X = X.drop(columns=[NAME_COL])

    numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "bool", "string"]).columns.tolist()

    for col in categorical_features:
        X[col] = X[col].astype(str)

    print("\n==============================")
    print("FEATURE INFO")
    print("==============================")
    print(f"Numeric features: {len(numeric_features)}")
    print(f"Categorical features: {len(categorical_features)}")
    print("Categorical columns:", categorical_features)

    # ============================================================
    # 3. TRAIN / TEST SPLIT
    # ============================================================

    # Test set remains untouched until the very end.
    # Optuna will only work on X_train_full.
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y
    )

    print("\n==============================")
    print("SPLIT INFO")
    print("==============================")
    print(f"Training + CV samples: {len(X_train_full)}")
    print(f"Final test samples: {len(X_test)}")

    print("\nTrain/CV class distribution:")
    print(y_train_full.value_counts())

    print("\nTest class distribution:")
    print(y_test.value_counts())

    # ============================================================
    # 4. PREPROCESSING PIPELINE
    # ============================================================

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median"))
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore"))
        ]
    )

    transformers = []

    if len(numeric_features) > 0:
        transformers.append(("num", numeric_transformer, numeric_features))

    if len(categorical_features) > 0:
        transformers.append(("cat", categorical_transformer, categorical_features))

    preprocessor = ColumnTransformer(transformers=transformers)

    # ============================================================
    # 5. RANDOM BASELINE
    # ============================================================

    random_baseline = 1 / y.nunique()

    print("\n==============================")
    print("BASELINE")
    print("==============================")
    print(f"Number of classes: {y.nunique()}")
    print(f"Random baseline accuracy: {random_baseline:.4f}")
    print("For four balanced classes, random guessing is approximately 25%.")

    # ============================================================
    # 6. CROSS-VALIDATION SETUP
    # ============================================================

    cv = StratifiedKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    # ============================================================
    # 7. OPTUNA OBJECTIVE FUNCTION WITH CROSS-VALIDATION
    # ============================================================

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 700),
            "max_depth": trial.suggest_int("max_depth", 3, 30),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
            "bootstrap": trial.suggest_categorical("bootstrap", [True, False]),
            "class_weight": trial.suggest_categorical("class_weight", [None, "balanced"])
        }

        model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", RandomForestClassifier(
                    **params,
                    random_state=RANDOM_STATE,
                    n_jobs=-1
                ))
            ]
        )

        scores = cross_val_score(
            model,
            X_train_full,
            y_train_full,
            cv=cv,
            scoring="accuracy",
            n_jobs=-1
        )

        mean_accuracy = scores.mean()
        std_accuracy = scores.std()

        trial.set_user_attr("cv_std", std_accuracy)
        trial.set_user_attr("cv_scores", scores.tolist())

        return mean_accuracy

    # ============================================================
    # 8. RUN BAYESIAN OPTIMIZATION
    # ============================================================

    print("\n==============================")
    print("BAYESIAN OPTIMIZATION WITH 5-FOLD CV STARTED")
    print("==============================")
    print(f"Number of trials: {N_TRIALS}")
    print(f"CV folds: {N_SPLITS}")

    optuna.logging.set_verbosity(optuna.logging.INFO)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=N_TRIALS)

    print("\n==============================")
    print("BEST CROSS-VALIDATION RESULT")
    print("==============================")
    print(f"Best mean CV accuracy: {study.best_value:.4f}")
    print(f"Best CV std: {study.best_trial.user_attrs['cv_std']:.4f}")
    print(f"Best CV scores: {study.best_trial.user_attrs['cv_scores']}")

    print("\nBest hyperparameters:")
    for key, value in study.best_params.items():
        print(f"{key}: {value}")

    # Save Optuna trials to CSV for documentation.
    trials_df = study.trials_dataframe()
    trials_df.to_csv(CV_RESULTS_PATH, index=False)

    # ============================================================
    # 9. TRAIN FINAL MODEL ON FULL TRAINING DATA
    # ============================================================

    print("\n==============================")
    print("TRAINING FINAL MODEL")
    print("==============================")

    final_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(
                **study.best_params,
                random_state=RANDOM_STATE,
                n_jobs=-1
            ))
        ]
    )

    final_model.fit(X_train_full, y_train_full)

    # ============================================================
    # 10. FINAL TEST EVALUATION
    # ============================================================

    print("\n==============================")
    print("FINAL TEST RESULTS")
    print("==============================")

    y_test_pred = final_model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)

    print(f"Final test accuracy: {test_accuracy:.4f}")

    print("\nClassification report:")
    print(classification_report(y_test, y_test_pred))

    print("\nConfusion matrix:")
    cm = confusion_matrix(y_test, y_test_pred)
    print(cm)

    # ============================================================
    # 11. SAVE CONFUSION MATRIX
    # ============================================================

    labels = final_model.named_steps["classifier"].classes_

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=labels
    )

    disp.plot(values_format="d")
    plt.title("Random Forest + Bayesian Optimization + 5-Fold CV")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH, dpi=300)
    plt.close()

    # ============================================================
    # 12. SAVE MODEL
    # ============================================================

    joblib.dump(final_model, MODEL_PATH)

    print("\n==============================")
    print("FILES SAVED")
    print("==============================")
    print(f"Model saved to: {MODEL_PATH.resolve()}")
    print(f"Confusion matrix saved to: {CONFUSION_MATRIX_PATH.resolve()}")
    print(f"Optuna CV results saved to: {CV_RESULTS_PATH.resolve()}")

    print("\nSCRIPT FINISHED SUCCESSFULLY")


if __name__ == "__main__":
    main()