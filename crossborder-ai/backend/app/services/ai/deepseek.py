"""VeyaShip - DeepSeek LLM Service.

Wrapper around the DeepSeek API for text generation tasks.
Supports listing content generation, translation, SEO optimization, and more.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


class DeepSeekService:
    """Service for interacting with the DeepSeek LLM API."""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL
        self.temperature = settings.DEEPSEEK_TEMPERATURE
        self.base_url = DEEPSEEK_BASE_URL

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2000,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate text using DeepSeek chat completion.

        Args:
            system_prompt: System-level instruction for the AI.
            user_prompt: The user's request / source material.
            max_tokens: Maximum tokens in the response.
            temperature: Override the default temperature.

        Returns:
            Generated text content.
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._build_headers(),
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature or self.temperature,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate_product_description(
        self,
        product_title: str,
        product_features: Optional[str] = None,
        tone: str = "professional",
        platform: str = "amazon",
        target_language: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> str:
        """Generate an optimized product listing description.

        Args:
            product_title: The product name.
            product_features: Key features or bullet points.
            tone: Writing tone (professional, casual, luxury, etc.).
            platform: Target e-commerce platform.
            target_language: Optional language code for translation.
            max_length: Maximum output length.

        Returns:
            Generated product description.
        """
        system_prompt = (
            f"You are an expert cross-border e-commerce copywriter specializing in {platform} listings. "
            f"Write compelling, conversion-optimized product content in a {tone} tone. "
            f"Include relevant SEO keywords naturally. "
            f"Format the output for the {platform} platform's requirements."
        )

        user_prompt = f"Product: {product_title}\n"
        if product_features:
            user_prompt += f"Features: {product_features}\n"
        if target_language:
            user_prompt += f"\nWrite the description in {target_language}."
        if max_length:
            user_prompt += f"\nKeep the description under {max_length} characters."

        return await self.generate(system_prompt, user_prompt)

    async def generate_bullet_points(
        self,
        product_title: str,
        features: str,
        count: int = 5,
        platform: str = "amazon",
    ) -> List[str]:
        """Generate key selling points / bullet points.

        Args:
            product_title: Product name.
            features: Product features or specs.
            count: Number of bullet points.
            platform: Target platform.

        Returns:
            List of bullet point strings.
        """
        system_prompt = (
            f"You are an expert Amazon/eBay listing optimizer. "
            f"Generate {count} compelling bullet points that highlight key benefits and features. "
            f"Each bullet should start with a capitalized benefit word followed by a colon."
        )

        user_prompt = (
            f"Product: {product_title}\n"
            f"Features/Specs: {features}\n"
            f"Generate exactly {count} bullet points for {platform}."
        )

        result = await self.generate(system_prompt, user_prompt, max_tokens=1000)

        # Parse bullet points from response
        bullets = []
        for line in result.strip().split("\n"):
            line = line.strip()
            if line and (line.startswith("-") or line.startswith("*") or line[0].isdigit()):
                bullets.append(line.lstrip("-*0123456789. ").strip())
            elif line and len(line) > 10:
                bullets.append(line)

        return bullets[:count]

    async def translate_content(
        self,
        text: str,
        target_language: str,
        source_language: str = "en",
    ) -> str:
        """Translate e-commerce content to a target language.

        Args:
            text: Source text to translate.
            target_language: Destination language (e.g., 'ja', 'de', 'fr').
            source_language: Source language code.

        Returns:
            Translated text.
        """
        system_prompt = (
            f"You are a professional e-commerce translator. "
            f"Translate the following product content from {source_language} to {target_language}. "
            f"Maintain SEO keywords, tone, and marketing appeal. "
            f"Adapt cultural references appropriately for the target market."
        )

        user_prompt = (
            f"Translate the following e-commerce content to {target_language}:\n\n{text}"
        )

        return await self.generate(system_prompt, user_prompt)

    async def optimize_seo(
        self,
        title: str,
        description: str,
        platform: str = "amazon",
    ) -> Dict[str, str]:
        """Optimize listing content for better search ranking.

        Returns:
            Dict with 'seo_title' and 'seo_description' keys.
        """
        system_prompt = (
            f"You are an SEO specialist for {platform}. "
            f"Output ONLY a JSON object with 'seo_title' and 'seo_description'. "
            f"No markdown, no bold markers, no extra text. "
            f"Front-load important keywords. Keep the title under 200 characters."
        )

        user_prompt = (
            f"Original Title: {title}\n"
            f"Original Description: {description}\n\n"
            f"Return JSON: {{\"seo_title\": \"...\", \"seo_description\": \"...\"}}"
        )

        result = await self.generate(system_prompt, user_prompt, max_tokens=500)

        # Try parsing JSON from response
        import json
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                seo_title = data.get("seo_title", "")
                seo_description = data.get("seo_description", "")
                # 如果返回了有效内容就用，否则 fallback
                if seo_title and seo_title != "**" and len(seo_title) > 5:
                    return {"seo_title": seo_title, "seo_description": seo_description or description}
            except json.JSONDecodeError:
                pass

        # Fallback: 直接返回原标题和描述
        return {"seo_title": title, "seo_description": description}
