from coloranalysis.ai.predictor import SeasonPredictorService


def ask_yes_no(question: str) -> str:
    while True:
        answer = input(question).strip().lower()
        if answer in {"yes", "no"}:
            return answer
        print("Please type only 'yes' or 'no'.")


def ask_optional_choice(question: str) -> str | None:
    answer = input(question).strip().lower()
    return answer if answer else None


image_path = input("Image path (default: 1.jpeg): ").strip() or "1.jpeg"

is_hair_visible = ask_yes_no("Is the hair visible? (yes/no): ")
is_hair_natural = ask_yes_no("Is the hair natural? (yes/no): ")

natural_hair_color = None
visible_hair_reliable = is_hair_visible == "yes" and is_hair_natural == "yes"

if is_hair_visible == "yes" and is_hair_natural == "no":
    natural_hair_color = ask_optional_choice(
        "What is the natural hair color? "
        "(blonde/brown/black/red/gray/other): "
    )

service = SeasonPredictorService()
result = service.predict_from_image(image_path)

user_metadata = {
    "is_hair_visible": is_hair_visible,
    "is_hair_natural": is_hair_natural,
    "natural_hair_color": natural_hair_color,
    "visible_hair_reliable": visible_hair_reliable,
}

print("\n==============================")
print("USER METADATA")
print("==============================")
print(user_metadata)

if not result.get("success"):
    print("\n==============================")
    print("ERROR")
    print("==============================")
    print(result.get("error"))
else:
    prediction = result["prediction"]
    features = result["features"]
    aggregated = features["aggregated_features"]

    print("\n==============================")
    print("FINAL RESULT")
    print("==============================")
    print(f"Predicted season: {prediction['predicted_season']}")
    print(f"Reason: {prediction['reason']}")

    print("\n==============================")
    print("USED FEATURES")
    print("==============================")
    print(f"avg_skin_L: {aggregated['avg_skin_L']}")
    print(f"avg_skin_C: {aggregated['avg_skin_C']}")
    print(f"avg_skin_H: {aggregated['avg_skin_H']}")

    print("\n==============================")
    print("PATCH COUNTS")
    print("==============================")
    print(f"left_cheek: {features['left_cheek_patch_count']}")
    print(f"right_cheek: {features['right_cheek_patch_count']}")
    print(f"forehead: {features['forehead_patch_count']}")
    print(f"total: {features['total_valid_patch_count']}")

    print("\n==============================")
    print("REGION CONSISTENCY")
    print("==============================")
    print(f"cheek_H_diff: {aggregated['cheek_H_diff']}")
    print(f"forehead_vs_cheeks_H_diff: {aggregated['forehead_vs_cheeks_H_diff']}")