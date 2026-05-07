import pandas as pd
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURES_PATH = Path("dataset/training_features.csv")

OUTPUT_ALL = Path("dataset/suspicious_samples_strict.csv")
OUTPUT_SUMMER = Path("dataset/suspicious_summer_strict.csv")

NAME_COL = "image_name"
LABEL_COL = "season"

df = pd.read_csv(FEATURES_PATH)

feature_cols = [
    col for col in df.columns
    if col not in [NAME_COL, LABEL_COL]
    and pd.api.types.is_numeric_dtype(df[col])
]

X = df[feature_cols]
y = df[LABEL_COL]

classes = sorted(y.unique())

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


models = {
    "RandomForest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=700,
            max_depth=8,
            min_samples_leaf=4,
            random_state=42,
            class_weight="balanced"
        ))
    ]),

    "ExtraTrees": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", ExtraTreesClassifier(
            n_estimators=700,
            max_depth=8,
            min_samples_leaf=4,
            random_state=42,
            class_weight="balanced"
        ))
    ])
}


all_predictions = {}

for model_name, model in models.items():
    probas = cross_val_predict(
        model,
        X,
        y,
        cv=cv,
        method="predict_proba"
    )

    all_predictions[model_name] = probas


results = []

for i, row in df.iterrows():
    true_label = row[LABEL_COL]

    model_votes = []
    confidences = []
    true_confidences = []

    for model_name, probas in all_predictions.items():
        probs = probas[i]

        pred_idx = probs.argmax()
        pred_label = classes[pred_idx]

        confidence = float(probs[pred_idx])
        true_idx = classes.index(true_label)
        true_confidence = float(probs[true_idx])

        model_votes.append(pred_label)
        confidences.append(confidence)
        true_confidences.append(true_confidence)

    # ambele modele trebuie să fie de acord că label-ul e greșit
    same_prediction = len(set(model_votes)) == 1
    predicted_label = model_votes[0]

    avg_confidence = sum(confidences) / len(confidences)
    avg_true_confidence = sum(true_confidences) / len(true_confidences)
    margin = avg_confidence - avg_true_confidence

    # schimbă doar condiția din script:

    if (
            same_prediction
            and predicted_label != true_label
            and true_label == "summer"
            and avg_confidence >= 0.55
            and avg_true_confidence <= 0.35
            and margin >= 0.20
    ):
        results.append({
            "filename": row[NAME_COL],
            "label": true_label,
            "model_prediction": predicted_label,
            "avg_prediction_confidence": round(avg_confidence, 3),
            "avg_true_label_confidence": round(avg_true_confidence, 3),
            "margin": round(margin, 3),
            "rf_prediction": model_votes[0],
            "et_prediction": model_votes[1],
            "decision": "manual_review_strict"
        })


result_df = pd.DataFrame(results)

if result_df.empty:
    print("No strict suspicious samples found.")
else:
    result_df = result_df.sort_values(
        by=["label", "model_prediction", "avg_prediction_confidence", "margin"],
        ascending=[True, True, False, False]
    )

    result_df.to_csv(OUTPUT_ALL, index=False)

    summer_df = result_df[result_df["label"] == "summer"].copy()
    summer_df.to_csv(OUTPUT_SUMMER, index=False)

    print("\nSaved all strict suspicious samples to:")
    print(OUTPUT_ALL)

    print("\nSaved strict suspicious SUMMER samples to:")
    print(OUTPUT_SUMMER)

    print("\nSummary:")
    print(result_df.groupby(["label", "model_prediction"]).size())

    print("\nStrict suspicious samples:")
    print(result_df.to_string(index=False))

    print("\nStrict suspicious SUMMER samples:")
    if summer_df.empty:
        print("No strict suspicious summer samples found.")
    else:
        print(summer_df.to_string(index=False))