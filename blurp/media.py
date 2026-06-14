import asyncio
from io import BytesIO
from typing import Optional

import cv2
import numpy as np
import requests
from PIL import Image


def _blur(url: str, blur_strength: int) -> Optional[BytesIO]:
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")

        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        ksize = max(1, blur_strength | 1)
        blurred_cv = cv2.GaussianBlur(img_cv, (ksize, ksize), 0)

        result_image = Image.fromarray(cv2.cvtColor(blurred_cv, cv2.COLOR_BGR2RGB))
        buffer = BytesIO()
        result_image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
    except Exception:
        return None


async def blur_image_from_url(url: str, blur_strength: int = 25) -> Optional[BytesIO]:
    """Download an image, Gaussian blur it, and return a PNG BytesIO buffer."""
    return await asyncio.to_thread(_blur, url, blur_strength)
