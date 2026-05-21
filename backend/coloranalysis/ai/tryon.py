from __future__ import annotations

from importlib import util
from pathlib import Path
from typing import Any, Callable


_cached_generate: Callable[[str, str, str], dict[str, list[dict[str, str]]]] | None = None


def _load_generate_function() -> Callable[[str, str, str], dict[str, list[dict[str, str]]]]:
    global _cached_generate
    if _cached_generate:
        return _cached_generate

    module_path = Path(__file__).resolve().parents[2] / "google" / "seasonal_tryon.py"
    spec = util.spec_from_file_location("seasonal_tryon", module_path)
    if not spec or not spec.loader:
        raise RuntimeError("Unable to load seasonal_tryon module.")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]

    generate_fn = getattr(module, "generate_tryon_images_for_analysis", None)
    if not callable(generate_fn):
        raise RuntimeError("generate_tryon_images_for_analysis not found.")

    _cached_generate = generate_fn
    return generate_fn


def generate_tryon_images_for_analysis(
    image_path: str,
    season: str,
    analysis_id: str,
) -> dict[str, list[dict[str, str]]]:
    generate_fn = _load_generate_function()
    return generate_fn(image_path=image_path, season=season, analysis_id=analysis_id)
