from pathlib import Path
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ==============================
# CONFIG
# ==============================

DATASET_PATH = Path("dataset/training_features.csv")
MODEL_PATH = Path("dataset/season_random_forest.pkl")

TARGET_COL = "season"
NAME_COL = "image_name"
RANDOM_STATE = 42


# ==============================
# LOAD DATA
# ==============================

df = pd.read_csv(DATASET_PATH)

print("\n==============================")
print("DATASET INFO")
print("==============================")
print(f"Total samples: {len(df)}")
print("\nClass distribution:")
print(df[TARGET_COL].value_counts())
print("\nClass distribution (%):")
print((df[TARGET_COL].value_counts(normalize=True) * 100).round(2))


# ==============================
# FEATURES / TARGET
# ==============================

if NAME_COL in df.columns:
    X = df.drop(columns=[NAME_COL, TARGET_COL])
else:
    X = df.drop(columns=[TARGET_COL])

y = df[TARGET_COL].astype(str)


categorical_cols = [
    "is_hair_visible",
    "is_hair_natural",
    "natural_hair_color",
    "used_observed_hair",
]

categorical_cols = [col for col in categorical_cols if col in X.columns]
numeric_cols = [col for col in X.columns if col not in categorical_cols]


for col in categorical_cols:
    X[col] = X[col].astype("string").fillna("missing")

for col in numeric_cols:
    X[col] = pd.to_numeric(X[col], errors="coerce")


# ==============================
# TRAIN / VALIDATION / TEST
# ==============================
# 60% train, 20% validation, 20% test

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_train_full,
    y_train_full,
    test_size=0.25,
    random_state=RANDOM_STATE,
    stratify=y_train_full
)

print("\n==============================")
print("SPLIT INFO")
print("==============================")
print(f"Train samples:      {len(X_train)}")
print(f"Validation samples: {len(X_val)}")
print(f"Test samples:       {len(X_test)}")


# ==============================
# PREPROCESSING
# ==============================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
            ]),
            numeric_cols
        ),
        (
            "cat",
            Pipeline([
                ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]),
            categorical_cols
        ),
    ]
)


# ==============================
# RANDOM FOREST MODEL
# ==============================
# Parametri aleși pentru rezultat stabil, nu exagerat.
# Dacă datasetul tău e ok, ar trebui să fie în zona 0.48 - 0.55.

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=700,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features="sqrt",
            bootstrap=True,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ]
)


# ==============================
# TRAIN
# ==============================

model.fit(X_train, y_train)


# ==============================
# VALIDATION EVALUATION
# ==============================

y_val_pred = model.predict(X_val)
val_accuracy = accuracy_score(y_val, y_val_pred)

labels = sorted(y.unique())

print("\n==============================")
print("VALIDATION RESULTS")
print("==============================")
print(f"Validation accuracy: {val_accuracy:.4f}")
print(f"Validation accuracy percentage: {val_accuracy * 100:.2f}%")

print("\nValidation classification report:")
print(classification_report(y_val, y_val_pred, labels=labels, zero_division=0))

print("\nValidation confusion matrix:")
print(confusion_matrix(y_val, y_val_pred, labels=labels))

print("\nClass order:")
print(labels)


# ==============================
# FINAL TRAINING ON TRAIN + VALIDATION
# ==============================
# După ce validarea e ok, antrenăm modelul final pe mai multe date.

final_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=700,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features="sqrt",
            bootstrap=True,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ]
)

final_model.fit(X_train_full, y_train_full)


# ==============================
# TEST EVALUATION
# ==============================

y_test_pred = final_model.predict(X_test)
test_accuracy = accuracy_score(y_test, y_test_pred)

print("\n==============================")
print("TEST RESULTS")
print("==============================")
print(f"Test accuracy: {test_accuracy:.4f}")
print(f"Test accuracy percentage: {test_accuracy * 100:.2f}%")

print("\nTest classification report:")
print(classification_report(y_test, y_test_pred, labels=labels, zero_division=0))

print("\nTest confusion matrix:")
print(confusion_matrix(y_test, y_test_pred, labels=labels))

print("\nClass order:")
print(labels)


# ==============================
# SAVE MODEL
# ==============================

joblib.dump(final_model, MODEL_PATH)

print("\n==============================")
print("MODEL SAVED")
print("==============================")
print(f"Saved to: {MODEL_PATH}")


# ==============================
# SIMPLE MESSAGE
# ==============================

if test_accuracy >= 0.50:
    print("\n✅ Accuracy is around or above 50%. Good enough for this RF baseline.")
else:
    print("\n⚠️ Accuracy is below 50%. Try the alternative RF parametercd bs below.")