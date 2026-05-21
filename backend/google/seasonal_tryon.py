import asyncio
import mimetypes
import os
import re
import time
import traceback
from io import BytesIO
from pathlib import Path
from typing import Any

from google import genai
from google.genai.types import GenerateContentConfig, Modality
from PIL import Image


MODEL_NAME = "gemini-3.1-flash-image-preview"

REQUEST_DELAY_SECONDS = 0


SEASON_COLORS = {
    "SPRING": {
        "good": [
            {"name": "Soft Pink", "hex": "#FF8FAB"},
        ],
        "bad": [
            {"name": "Cool Dark Green", "hex": "#232B2B"},
        ],
    },
    "SUMMER": {
        "good": [
            {"name": "Slate Blue", "hex": "#708090"},
        ],
        "bad": [
            {"name": "Neon Orange", "hex": "#FF4500"},
        ],
    },
    "AUTUMN": {
        "good": [
            {"name": "Olive Green", "hex": "#556B2F"},
        ],
        "bad": [
            {"name": "Cool Pink", "hex": "#ffd9fd"},
        ],
    },
    "WINTER": {
        "good": [
            {"name": "Royal Berry", "hex": "#C21E56"},
        ],
        "bad": [
            {"name": "Warm Beige", "hex": "#DEB887"},
        ],
    },
}


def sanitize_filename(value: str) -> str:
    value = value.strip().replace(" ", "_")
    value = re.sub(r"[^A-Za-z0-9_\-]", "", value)
    return value


def get_mime_type(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(image_path))

    allowed = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if mime_type in allowed:
        return mime_type

    print(f"Warning: unknown mime type for {image_path}. Detected: {mime_type}")
    return mime_type or "image/jpeg"


def get_palette_for_season(season: str) -> list[dict[str, str]]:
    season_key = season.upper().strip()

    if season_key not in SEASON_COLORS:
        valid = ", ".join(SEASON_COLORS.keys())
        raise ValueError(f"Invalid season '{season}'. Valid seasons: {valid}")

    colors: list[dict[str, str]] = []

    for index, color in enumerate(SEASON_COLORS[season_key]["good"], start=1):
        colors.append(
            {
                "type": "good",
                "index": str(index),
                "name": color["name"],
                "hex": color["hex"],
            }
        )

    for index, color in enumerate(SEASON_COLORS[season_key]["bad"], start=1):
        colors.append(
            {
                "type": "bad",
                "index": str(index),
                "name": color["name"],
                "hex": color["hex"],
            }
        )

    return colors


def build_prompt(hex_code: str) -> str:
    return (
        f"Edit the uploaded portrait as a realistic virtual clothing try-on. "
        f"Add a beautiful, natural-looking plain blouse or elegant casual top in exactly HEX color {hex_code}. "

        f"The garment must look real and naturally worn by the person, not like a color overlay or painted texture. "
        f"Do not simply recolor the original clothing. Replace the visible clothing with a new garment. "

        f"The top should have a flattering, natural neckline. "
        f"It should NOT be a turtleneck and NOT a tight high-neck shirt. "
        f"It may have a soft open collar, a subtle blouse-style neckline, or a simple elegant feminine neckline. "
        f"It should look stylish, clean, natural, and realistic. "

        f"Very important: keep the SAME framing and crop as the original image. "
        f"Do not zoom out. Do not reveal more of the body than in the original. "
        f"Do not add extra shoulders, extra torso, or extra chest area beyond what is already naturally visible. "
        f"Do not widen the body shape. "

        f"Only modify the clothing area. "
        f"Preserve the face, hair, skin tone, eyes, expression, pose, jewelry, background, and lighting. "
        f"Do not change identity. Do not beautify the face. Do not alter the background. "

        f"The result must look like the person is wearing a real elegant top or blouse in color {hex_code}, "
        f"with natural folds and realistic fabric."
    )


def build_output_filename(color_info: dict[str, str]) -> str:
    color_type = color_info["type"]
    index = color_info["index"]
    name = sanitize_filename(color_info["name"])
    hex_code = color_info["hex"].replace("#", "")

    return f"{color_type}_{index}_{name}_{hex_code}.png"


def extract_and_save_image(response: Any, output_path: Path) -> bool:
    """
    Gemini can return text and image parts.
    This saves the first returned image part as PNG.
    """
    if not response.candidates:
        print("No candidates returned.")
        return False

    content = response.candidates[0].content

    if not content or not content.parts:
        print("No content parts returned.")
        return False

    for part in content.parts:
        if getattr(part, "text", None):
            print(f"Model text: {part.text}")

        inline_data = getattr(part, "inline_data", None)

        if inline_data and getattr(inline_data, "data", None):
            try:
                image = Image.open(BytesIO(inline_data.data))
                image.save(output_path)
                return True
            except Exception:
                print(f"Failed to decode/save image to {output_path}")
                traceback.print_exc()
                return False

    print("No image part found in the response.")
    return False


def create_vertex_client() -> genai.Client:
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "project-189ae7e3-e06f-4a6a-925")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

    return genai.Client(
        vertexai=True,
        project=project,
        location=location,
    )


def generate_one_variant_sync(
    client: genai.Client,
    model_name: str,
    image_path: Path,
    color_info: dict[str, str],
    output_path: Path,
) -> str | None:
    hex_code = color_info["hex"]
    color_name = color_info["name"]
    color_type = color_info["type"]

    prompt = build_prompt(hex_code)

    print(f"Generating {color_type.upper()} color: {color_name} ({hex_code})")

    try:
        image = Image.open(image_path)

        response = client.models.generate_content(
            model=model_name,
            contents=[image, prompt],
            config=GenerateContentConfig(
                response_modalities=[Modality.TEXT, Modality.IMAGE]
            ),
        )

        saved = extract_and_save_image(response, output_path)

        if saved:
            print(f"Saved: {output_path}")
            return str(output_path)

        print(f"Failed to save image for {color_name} ({hex_code})")
        return None

    except Exception:
        print(f"Generation failed for {color_name} ({hex_code})")
        traceback.print_exc()
        raise


async def generate_one_variant_with_retry(
    client: genai.Client,
    model_name: str,
    image_path: Path,
    color_info: dict[str, str],
    output_path: Path,
    max_retries: int = 3,
) -> str | None:
    """
    The Google GenAI SDK call is synchronous, so we run it inside asyncio.to_thread().
    This keeps Django from blocking the event loop logic here while still using the SDK.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return await asyncio.to_thread(
                generate_one_variant_sync,
                client,
                model_name,
                image_path,
                color_info,
                output_path,
            )

        except Exception as error:
            wait_seconds = 2 * attempt

            print(
                f"Error for {color_info['name']} ({color_info['hex']}), "
                f"attempt {attempt}/{max_retries}: {error}"
            )

            if attempt < max_retries:
                print(f"Retrying in {wait_seconds} seconds...")
                await asyncio.sleep(wait_seconds)
            else:
                print(f"Giving up on {color_info['name']}.")

    return None


async def generate_variants_with_metadata(
    image_path: str,
    season: str,
    output_dir: str,
) -> list[dict[str, str | None]]:
    image_file = Path(image_path)

    if not image_file.exists():
        raise FileNotFoundError(f"Input image not found: {image_file}")

    get_mime_type(image_file)

    season_key = season.upper().strip()
    colors = get_palette_for_season(season_key)

    season_output_dir = Path(output_dir) / season_key
    season_output_dir.mkdir(parents=True, exist_ok=True)

    client = create_vertex_client()

    jobs: list[tuple[dict[str, str], Path]] = []

    for color_info in colors:
        filename = build_output_filename(color_info)
        output_path = season_output_dir / filename
        jobs.append((color_info, output_path))

    print("=== TRY-ON BATCH START ===")
    print(f"Launching {len(jobs)} Gemini image-editing requests SEQUENTIALLY...")
    print(f"Input image: {image_file}")
    print(f"Input image exists: {image_file.exists()}")
    print(f"Season: {season_key}")
    print(f"Output dir: {season_output_dir}")
    print(f"Model: {MODEL_NAME}")
    print(f"Delay between requests: {REQUEST_DELAY_SECONDS} seconds")

    start = time.perf_counter()

    results: list[str | None | Exception] = []
    output_paths: list[Path] = []

    for index, (color_info, output_path) in enumerate(jobs, start=1):
        print(
            f"Request {index}/{len(jobs)}: "
            f"{color_info['type'].upper()} {color_info['name']} ({color_info['hex']})"
        )

        try:
            result = await generate_one_variant_with_retry(
                client=client,
                model_name=MODEL_NAME,
                image_path=image_file,
                color_info=color_info,
                output_path=output_path,
            )
            results.append(result)
        except Exception as error:
            print(
                f"Sequential request failed for "
                f"{color_info['name']} ({color_info['hex']}): {error}"
            )
            traceback.print_exc()
            results.append(error)

        output_paths.append(output_path)

        if REQUEST_DELAY_SECONDS > 0 and index < len(jobs):
            print(f"Waiting {REQUEST_DELAY_SECONDS} seconds before next Gemini request...")
            await asyncio.sleep(REQUEST_DELAY_SECONDS)

    elapsed = time.perf_counter() - start
    print(f"Finished in {elapsed:.2f} seconds.")
    print("=== TRY-ON BATCH END ===")

    enriched: list[dict[str, str | None]] = []

    for color_info, output_path, result in zip(colors, output_paths, results):
        entry = {
            "type": color_info["type"],
            "name": color_info["name"],
            "hex": color_info["hex"],
            "filename": output_path.name,
            "saved_path": None,
        }

        if isinstance(result, Exception):
            print(f"Task failed for {color_info['name']} ({color_info['hex']}):")
            traceback.print_exception(type(result), result, result.__traceback__)
        elif result:
            entry["saved_path"] = result
        else:
            print(f"No image generated for {color_info['name']} ({color_info['hex']})")

        enriched.append(entry)

    return enriched


async def generate_all_variants(
    image_path: str,
    season: str,
    output_dir: str = "output",
) -> list[str]:
    results = await generate_variants_with_metadata(
        image_path=image_path,
        season=season,
        output_dir=output_dir,
    )

    return [entry["saved_path"] for entry in results if entry.get("saved_path")]


def generate_tryon_images_for_analysis(
    image_path: str,
    season: str,
    analysis_id: str,
) -> dict[str, list[dict[str, str]]]:
    try:
        from django.conf import settings
    except Exception as error:
        raise RuntimeError("Django settings are required for try-on generation") from error

    try:
        season_key = season.upper().strip()

        print("=== TRY-ON GENERATION START ===")
        print(f"Analysis ID: {analysis_id}")
        print(f"Season: {season_key}")
        print(f"Image path: {image_path}")
        print(f"Image exists: {Path(image_path).exists()}")

        # Base output folder for this analysis.
        # generate_variants_with_metadata will create the season subfolder.
        base_output_dir = Path(settings.MEDIA_ROOT) / "tryon" / str(analysis_id)

        results = asyncio.run(
            generate_variants_with_metadata(
                image_path=image_path,
                season=season_key,
                output_dir=str(base_output_dir),
            )
        )

        good_images: list[dict[str, str]] = []
        bad_images: list[dict[str, str]] = []

        for entry in results:
            if not entry.get("saved_path"):
                print(f"Skipping failed try-on image: {entry}")
                continue

            image_url = (
                f"{settings.MEDIA_URL}tryon/"
                f"{analysis_id}/{season_key}/{entry['filename']}"
            )

            payload = {
                "name": str(entry["name"]),
                "hex": str(entry["hex"]),
                "imageUrl": image_url,
                "type": str(entry["type"]),
            }

            if entry["type"] == "good":
                good_images.append(payload)
            else:
                bad_images.append(payload)

        print(f"Generated good images: {len(good_images)}")
        print(f"Generated bad images: {len(bad_images)}")
        print("=== TRY-ON GENERATION END ===")

        if not good_images and not bad_images:
            raise RuntimeError("No try-on images were generated.")

        return {
            "good": good_images,
            "bad": bad_images,
        }

    except Exception:
        print("=== TRY-ON GENERATION FAILED ===")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    saved_files = asyncio.run(
        generate_all_variants(
            image_path="input/selfie.png",
            season="SUMMER",
            output_dir="output",
        )
    )

    print("\nGenerated files:")
    for file_path in saved_files:
        print(file_path)


# HOW TO RUN ON WINDOWS POWERSHELL
#
# 1. Activate your backend venv:
#    cd "C:\Users\Janine\Desktop\Licenta\backend"
#    .\.venv311\Scripts\Activate.ps1
#
# 2. Install packages:
#    python -m pip install --upgrade google-genai pillow
#
# 3. Authenticate:
#    gcloud auth application-default login
#
# 4. Set environment variables in the SAME terminal:
#    $env:GOOGLE_CLOUD_PROJECT="project-189ae7e3-e06f-4a6a-925"
#    $env:GOOGLE_CLOUD_LOCATION="global"
#    $env:GOOGLE_GENAI_USE_VERTEXAI="True"
#
# 5. Manual test:
#    cd google
#    python seasonal_tryon.py
#
# 6. Django usage:
#    cd ..
#    python manage.py runserver