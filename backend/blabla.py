from pathlib import Path

csv_path = Path("dataset/labels.csv")

text = csv_path.read_text(encoding="utf-8")

text = text.replace(".jpg", ".png")
text = text.replace(".jpeg", ".png")
text = text.replace(".JPG", ".png")
text = text.replace(".JPEG", ".png")

csv_path.write_text(text, encoding="utf-8")

print("Done: all jpg/jpeg extensions were changed to png in labels.csv")