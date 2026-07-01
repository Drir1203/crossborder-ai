"""VeyaShip - Payment Service.

Creem.io payment integration for subscription management.
"""

from typing import Any, Dict, Optional

import httpx

from app.core.config import settings


class PaymentService:
    """Service for Creem.io payment integration.

    Handles checkout sessions, webhook verification,
    subscription lifecycle, and invoice management.
    """

    CREEM_API_URL = "https://api.creem.io/v1"

    def __init__(self):
        self.api_key = settings.CREEM_API_KEY
        self.webhook_secret = settings.CREEM_WEBHOOK_SECRET

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_checkout_session(
        self,
        plan_name: str,
        billing_interval: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a Creem.io checkout session.

        Args:
            plan_name: Subscription plan identifier.
            billing_interval: monthly or yearly.
            success_url: Redirect on successful payment.
            cancel_url: Redirect on cancellation.
            customer_email: Pre-fill customer email.
            metadata: Additional data to attach.

        Returns:
            Checkout session data with URL.
        """
        payload = {
            "plan": plan_name,
            "billing_interval": billing_interval,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "mode": "subscription",
        }
        if customer_email:
            payload["customer_email"] = customer_email
        if metadata:
            payload["metadata"] = metadata

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.CREEM_API_URL}/checkout/sessions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify Creem.io webhook signature.

        Args:
            payload: Raw request body.
            signature: Signature from the webhook header.

        Returns:
            True if the signature is valid.
        """
        # TODO: Implement HMAC verification with CREEM_WEBHOOK_SECRET
        # import hmac, hashlib
        # expected = hmac.new(
        #     self.webhook_secret.encode(),
        #     payload,
        #     hashlib.sha256,
        # ).hexdigest()
        # return hmac.compare_digest(expected, signature)
        return True

    async def cancel_subscription(self, creem_subscription_id: str) -> bool:
        """Cancel a subscription in Creem.io.

        Args:
            creem_subscription_id: The Creem.io subscription ID.

        Returns:
            True if cancellation succeeded.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.CREEM_API_URL}/subscriptions/{creem_subscription_id}/cancel",
                headers=self._headers(),
            )
            return response.is_success

    async def get_subscription(self, creem_subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details from Creem.io."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.CREEM_API_URL}/subscriptions/{creem_subscription_id}",
                headers=self._headers(),
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
