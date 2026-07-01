"""VeyaShip - Replicate FLUX Image Generation Service.

Integrates with Replicate API to generate product images
using the black-forest-labs/flux-schnell model.
"""

from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

REPLICATE_BASE_URL = "https://api.replicate.com/v1"


class ReplicateService:
    """Service for AI image generation via Replicate's FLUX model."""

    def __init__(self):
        self.api_key = settings.REPLICATE_API_KEY
        self.model = settings.REPLICATE_MODEL

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_product_prompt(
        self,
        product_title: str,
        custom_prompt: Optional[str] = None,
        style: str = "professional product photography",
    ) -> str:
        """Build an optimized image generation prompt for products."""
        if custom_prompt:
            return custom_prompt

        return (
            f"Professional e-commerce product photo of {product_title}. "
            f"{style}. Clean white background, studio lighting, "
            f"high resolution, 8K, product photography, photorealistic, "
            f"sharp focus, commercial photography."
        )

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=8),
    )
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_outputs: int = 1,
        aspect_ratio: str = "1:1",
    ) -> List[str]:
        """Generate product images using FLUX model.

        Args:
            prompt: Text description of the desired image.
            negative_prompt: Elements to avoid in the output.
            num_outputs: Number of images (1-4).
            aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4).

        Returns:
            List of generated image URLs.
        """
        if not self.api_key:
            raise ValueError("Replicate API key not configured")

        input_data = {
            "prompt": prompt,
            "num_outputs": min(num_outputs, 4),
            "aspect_ratio": aspect_ratio,
            "output_format": "webp",
            "quality": 90,
        }

        if negative_prompt:
            input_data["negative_prompt"] = negative_prompt

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Start prediction
            response = await client.post(
                f"{REPLICATE_BASE_URL}/models/{self.model}/predictions",
                headers=self._build_headers(),
                json={"input": input_data},
            )
            response.raise_for_status()
            prediction = response.json()

            # Poll for completion
            prediction_url = f"{REPLICATE_BASE_URL}/predictions/{prediction['id']}"
            while prediction["status"] not in ("succeeded", "failed", "canceled"):
                await client.get(prediction_url, headers=self._build_headers())
                response = await client.get(
                    prediction_url, headers=self._build_headers()
                )
                response.raise_for_status()
                prediction = response.json()

            if prediction["status"] == "failed":
                raise RuntimeError(f"Image generation failed: {prediction.get('error', 'Unknown error')}")

            return prediction.get("output", [])

    async def generate_product_image(
        self,
        product_title: str,
        product_description: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        style: str = "professional product photography",
        aspect_ratio: str = "1:1",
    ) -> List[str]:
        """Generate a product image from product information.

        Args:
            product_title: The product name.
            product_description: Optional product description for context.
            custom_prompt: Override the auto-generated prompt.
            style: Photography style description.
            aspect_ratio: Image aspect ratio.

        Returns:
            List of generated image URLs.
        """
        prompt = self._build_product_prompt(product_title, custom_prompt, style)
        if product_description:
            prompt += f" Product features: {product_description[:200]}"

        return await self.generate_image(
            prompt=prompt,
            num_outputs=1,
            aspect_ratio=aspect_ratio,
        )
