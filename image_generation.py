"""Image generation for auto-generated cover photos."""

import io
import random
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw

from hf_config import get_huggingface_api_token, get_pollinations_api_key

DEFAULT_PROMPT = (
    "A beautiful peaceful landscape with mountains, lake, and soft natural lighting, "
    "photorealistic, high quality, calm scenery"
)
DEFAULT_SIZE = (1024, 1024)
HF_MODEL = "black-forest-labs/FLUX.1-schnell"
POLLINATIONS_MODEL = "flux"
POLLINATIONS_URL = "https://gen.pollinations.ai/image"


def get_inference_headers() -> dict[str, str]:
    """Return HTTP headers for Hugging Face Inference API image generation requests."""
    from hf_config import get_hf_authorization_header

    headers = {"Content-Type": "application/json"}
    headers.update(get_hf_authorization_header())
    return headers


def _save_pil_image(image: Image.Image, output_path: str, size: tuple[int, int]) -> str:
    image = image.convert("RGB")
    if image.size != size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    image.save(output_path, format="PNG")
    return output_path


def _bytes_to_pil(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes))


def _generate_local_fallback_image(size: tuple[int, int]) -> Image.Image:
    """Create a decorative landscape-style image when all APIs are unavailable."""
    width, height = size
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(70 + ratio * 120)
        g = int(120 + ratio * 80)
        b = int(180 - ratio * 40)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    mountain_color = (45, 75, 55)
    draw.polygon([(0, height), (width * 0.25, height * 0.55), (width * 0.5, height)], fill=mountain_color)
    draw.polygon(
        [(width * 0.35, height), (width * 0.7, height * 0.45), (width, height)],
        fill=(35, 65, 48),
    )

    lake_top = int(height * 0.72)
    draw.rectangle([(0, lake_top), (width, height)], fill=(30, 90, 130))
    sun_x, sun_y = int(width * 0.78), int(height * 0.18)
    draw.ellipse([(sun_x - 40, sun_y - 40), (sun_x + 40, sun_y + 40)], fill=(255, 220, 120))

    for _ in range(120):
        x = random.randint(0, width - 1)
        y = random.randint(lake_top, height - 1)
        shade = random.randint(20, 60)
        draw.point((x, y), fill=(20 + shade, 90 + shade, 130 + shade))

    return image


def _generate_with_pollinations(prompt: str, size: tuple[int, int]) -> Image.Image:
    api_key = get_pollinations_api_key()
    if not api_key:
        raise ValueError("POLLINATIONS_API_KEY is not set.")

    width, height = size
    url = f"{POLLINATIONS_URL}/{quote(prompt)}"
    params = {
        "model": POLLINATIONS_MODEL,
        "width": width,
        "height": height,
        "nologo": "true",
        "key": api_key,
    }

    response = requests.get(url, params=params, timeout=120)
    if response.status_code == 200 and response.content:
        return _bytes_to_pil(response.content)

    if response.status_code in (401, 403):
        raise ValueError(
            "Pollinations API rejected the key. Check POLLINATIONS_API_KEY in .env."
        )
    if response.status_code == 402:
        raise ValueError("Pollinations credits exhausted. Add more pollen at enter.pollinations.ai.")

    raise ValueError(f"Pollinations image generation failed: {response.text[:200]}")


def _generate_with_huggingface(prompt: str, size: tuple[int, int]) -> Image.Image:
    token = get_huggingface_api_token()
    if not token:
        raise ValueError("HUGGINGFACE_API_TOKEN is not set.")

    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise ValueError("huggingface_hub is not installed. Run: pip install huggingface_hub") from exc

    client = InferenceClient(api_key=token, provider="auto")
    return client.text_to_image(prompt, model=HF_MODEL)


def generate_cover_image(
    output_path: str,
    prompt: str | None = None,
    width: int = 1024,
    height: int = 1024,
    allow_fallback: bool = True,
) -> tuple[str, str]:
    """
    Generate a cover image and save as PNG.
    Returns (output_path, source) where source is:
    pollinations | huggingface | local_fallback
    """
    prompt = (prompt or DEFAULT_PROMPT).strip() or DEFAULT_PROMPT
    size = (width, height)

    providers = []
    if get_pollinations_api_key():
        providers.append(("pollinations", _generate_with_pollinations))
    if get_huggingface_api_token():
        providers.append(("huggingface", _generate_with_huggingface))

    for source_name, generator in providers:
        try:
            image = generator(prompt, size)
            _save_pil_image(image, output_path, size)
            return output_path, source_name
        except Exception:
            continue

    if not allow_fallback:
        raise ValueError(
            "No image API available. Add POLLINATIONS_API_KEY or a valid HUGGINGFACE_API_TOKEN to .env."
        )

    image = _generate_local_fallback_image(size)
    _save_pil_image(image, output_path, size)
    return output_path, "local_fallback"
