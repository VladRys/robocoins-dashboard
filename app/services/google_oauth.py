import asyncio
import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token
import requests

from app.core.config import Config as cfg
from app.core.enums import GoogleOAuthFlow
from app.repositories.google_oauth import GoogleOAuthRepository, PendingGoogleOAuth

GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class GoogleOAuthError(Exception):
    pass


@dataclass(frozen=True)
class GoogleIdentity:
    sub: str
    email: str


@dataclass(frozen=True)
class GoogleAuthorizationRequest:
    url: str
    state: str


class GoogleOAuthService:
    def __init__(self, repository: GoogleOAuthRepository):
        self.repository = repository

    @staticmethod
    def _client_configuration() -> tuple[str, str, str]:
        client_id = cfg.GOOGLE_CLIENT_ID
        client_secret = cfg.GOOGLE_CLIENT_SECRET
        redirect_uri = cfg.GOOGLE_REDIRECT_URI
        if not client_id or not client_secret or not redirect_uri:
            raise GoogleOAuthError("Google sign-in is not configured")
        return client_id, client_secret, redirect_uri

    async def create_authorization_url(
        self,
        flow: GoogleOAuthFlow,
        user_id: int | None = None,
    ) -> GoogleAuthorizationRequest:
        client_id, _, redirect_uri = self._client_configuration()
        if flow not in {GoogleOAuthFlow.LOGIN, GoogleOAuthFlow.LINK} or (
            flow == GoogleOAuthFlow.LINK
        ) != (user_id is not None):
            raise ValueError("Invalid Google OAuth flow")

        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode("ascii")).digest()
        ).rstrip(b"=").decode("ascii")
        expires_at = _utc_now() + timedelta(minutes=10)
        await self.repository.create_state(
            state_hash=hashlib.sha256(state.encode("ascii")).hexdigest(),
            flow=flow,
            user_id=user_id,
            nonce=nonce,
            code_verifier=code_verifier,
            expires_at=expires_at,
        )

        authorization_url = f"{GOOGLE_AUTHORIZE_URL}?{urlencode({
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'nonce': nonce,
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
            'prompt': 'select_account',
        })}"
        return GoogleAuthorizationRequest(url=authorization_url, state=state)

    async def consume_state(self, state: str) -> PendingGoogleOAuth | None:
        state_hash = hashlib.sha256(state.encode("utf-8")).hexdigest()
        return await self.repository.consume_state(state_hash, _utc_now())

    async def exchange_code(
        self,
        code: str,
        code_verifier: str,
        expected_nonce: str,
    ) -> GoogleIdentity:
        client_id, client_secret, redirect_uri = self._client_configuration()
        try:
            claims = await asyncio.to_thread(
                self._exchange_and_verify,
                code,
                code_verifier,
                client_id,
                client_secret,
                redirect_uri,
            )
        except (GoogleAuthError, requests.RequestException, ValueError, KeyError) as exc:
            raise GoogleOAuthError("Google could not verify the sign-in") from exc

        nonce = claims.get("nonce")
        subject = claims.get("sub")
        email = claims.get("email")
        if (
            not isinstance(nonce, str)
            or not nonce.isascii()
            or not hmac.compare_digest(nonce, expected_nonce)
            or not isinstance(subject, str)
            or not subject
            or not isinstance(email, str)
            or not email
            or claims.get("email_verified") is not True
        ):
            raise GoogleOAuthError("Google returned an invalid account")
        return GoogleIdentity(sub=subject, email=email)

    @staticmethod
    def _exchange_and_verify(
        code: str,
        code_verifier: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> dict:
        response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
            },
            timeout=(3.05, 10),
        )
        response.raise_for_status()
        token_response = response.json()
        if not isinstance(token_response, dict):
            raise ValueError("Unexpected Google token response")
        token = token_response.get("id_token")
        if not isinstance(token, str) or not token:
            raise ValueError("Google response did not contain an ID token")
        return id_token.verify_oauth2_token(
            token,
            GoogleOAuthService._certificate_request,
            audience=client_id,
        )

    @staticmethod
    def _certificate_request(url: str, **kwargs):
        return GoogleRequest()(url, timeout=10, **kwargs)
