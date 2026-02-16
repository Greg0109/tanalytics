import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from src.config import settings

from . import logger


class TwitchClient:
    """
    Twitch API client.
    Handles authentication, token management, and API requests to Twitch.
    """

    TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    TWITCH_HELIX_URL = "https://api.twitch.tv/helix"

    def __init__(self):
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._http_client = httpx.AsyncClient()
        self._rate_limit_reset: Optional[datetime] = None

    async def _get_access_token(self) -> str:
        """
        Obtains an OAuth2 access token from Twitch.
        """
        response = await self._http_client.post(
            self.TWITCH_TOKEN_URL,
            params={
                "client_id": settings.TWITCH_CLIENT_ID,
                "client_secret": settings.TWITCH_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
        )
        response.raise_for_status()
        data = response.json()
        self._access_token = data["access_token"]
        self._token_expiry = datetime.now() + timedelta(
            seconds=data["expires_in"] - 300
        )
        logger.info(f"Twitch: New access token obtained, expires at {self._token_expiry}")
        return self._access_token

    async def _get_valid_access_token(self) -> str:
        """
        Returns a valid access token, refreshing it if expired.
        """
        if not self._access_token or (
            self._token_expiry and datetime.now() >= self._token_expiry
        ):
            logger.info("Twitch: Access token expired or not available, refreshing...")
            await self._get_access_token()
        return self._access_token

    async def _request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """
        Makes an authenticated request to the Twitch Helix API, handling token refresh and retries.
        """
        token = await self._get_valid_access_token()

        request_headers = {
            "Authorization": f"Bearer {token}",
            "Client-Id": settings.TWITCH_CLIENT_ID,
        }
        if headers:
            request_headers.update(headers)

        if self._rate_limit_reset and datetime.now() < self._rate_limit_reset:
            wait_time = (self._rate_limit_reset - datetime.now()).total_seconds() + 1
            logger.warning(f"Twitch: Rate limit hit, waiting for {wait_time:.2f} seconds.")
            await asyncio.sleep(wait_time)

        try:
            response = await self._http_client.request(
                method,
                f"{self.TWITCH_HELIX_URL}{path}",
                headers=request_headers,
                params=params,
                json=json,
                timeout=10,
            )

            if "Ratelimit-Reset" in response.headers:
                reset_timestamp = int(response.headers["Ratelimit-Reset"])
                self._rate_limit_reset = datetime.fromtimestamp(reset_timestamp)

            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401 and retry_count < 1:
                logger.warning(
                    "Twitch: Received 401, token might be invalid. Refreshing and retrying..."
                )
                self._access_token = None
                return await self._request(
                    method, path, headers, params, json, retry_count + 1
                )
            elif e.response.status_code == 429:
                logger.warning("Twitch: Received 429 (Rate Limit Exceeded).")
                if "Ratelimit-Reset" in e.response.headers:
                    reset_timestamp = int(e.response.headers["Ratelimit-Reset"])
                    self._rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
                else:
                    self._rate_limit_reset = datetime.now() + timedelta(
                        seconds=60
                    )

                if retry_count < 2:
                    await asyncio.sleep(1)
                    return await self._request(
                        method, path, headers, params, json, retry_count + 1
                    )

            raise

    async def get_users(
        self,
        user_ids: Optional[list[str]] = None,
        user_logins: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        Fetches user information from Twitch.
        """
        params = {}
        if user_ids:
            params["id"] = user_ids
        if user_logins:
            params["login"] = user_logins

        if not params:
            raise ValueError("Either user_ids or user_logins must be provided.")

        response = await self._request("GET", "/users", params=params)
        return response.json()

    async def get_streams(
        self,
        user_ids: Optional[list[str]] = None,
        user_logins: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        Fetches active streams from Twitch.
        """
        params = {}
        if user_ids:
            params["user_id"] = user_ids
        if user_logins:
            params["user_login"] = user_logins

        response = await self._request("GET", "/streams", params=params)
        return response.json()

    async def close(self):
        """
        Closes the HTTP client.
        """
        await self._http_client.aclose()


twitch_client = TwitchClient()
