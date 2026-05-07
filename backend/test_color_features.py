from coloranalysis.ai.color_features import ColorFeatureService

service = ColorFeatureService()

result = service.extract_color_features(
    "1.jpeg",
    is_hair_visible="yes",
    is_hair_natural="no",
    natural_hair_color="dark_brown",
)

print(result)