# keycloak_openid.py

import aiohttp
from .exceptions import (
    KeycloakAuthenticationError,
    KeycloakPostError,
)

class KeycloakOpenID:
    """Keycloak OpenID kliens."""

    def __init__(
            self,
            server_url,
            realm_name,
            client_id,
            client_secret_key="M8fQJjPAPE23JaFejL1XrIsagv75PS58",
            verify=True,
            timeout=60,
    ):
        """Inicializálja a KeycloakOpenID klienst."""
        self.server_url = server_url.rstrip('/')
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret_key = client_secret_key
        self.verify = verify
        self.timeout = timeout
        # Ne hozz létre ClientSession-t itt!

    async def init_session(self):
        """Aszinkron módszer a ClientSession létrehozására."""
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Aszinkron módszer a ClientSession bezárására."""
        await self.session.close()

    async def token(
            self,
            grant_type ,
            code=None,
            redirect_uri= "http://localhost:3000callback",
            username=None,
            password=None,
            scope="openid",
            **extra_params
    ):
        """Token lekérése a megadott grant_type alapján."""
        # Ellenőrizd, hogy a session létezik-e
        if not hasattr(self, 'session'):
            raise RuntimeError("Session not initialized. Call 'init_session()' before using this method.")

        token_url = f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/token"
        payload = {
            "grant_type": grant_type,
            "client_id": self.client_id,
            "scope": scope,
        }
        if self.client_secret_key:
            payload["client_secret"] = self.client_secret_key

        if grant_type == "authorization_code":
            payload["code"] = code
            payload["redirect_uri"] = redirect_uri
        elif grant_type == "password":
            payload["username"] = username
            payload["password"] = password

        payload.update(extra_params)

        async with self.session.post(token_url, data=payload, ssl=self.verify, timeout=self.timeout) as response:
            if response.status >= 400:
                raise KeycloakPostError(f"Hiba a token lekérése során: {response.status} {response.reason}")
            return await response.json()

    async def userinfo(self, token):
        """Felhasználói információk lekérése a hozzáférési token alapján."""
        if not hasattr(self, 'session'):
            raise RuntimeError("Session not initialized. Call 'init_session()' before using this method.")

        userinfo_url = f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/userinfo"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with self.session.get(userinfo_url, headers=headers, ssl=self.verify, timeout=self.timeout) as response:
            if response.status >= 400:
                raise KeycloakAuthenticationError(f"Hiba a felhasználói információk lekérése során: {response.status} {response.reason}")
            return await response.json()

    async def logout(self, refresh_token):
        """Felhasználó kijelentkeztetése a refresh token érvénytelenítésével."""
        if not hasattr(self, 'session'):
            raise RuntimeError("Session not initialized. Call 'init_session()' before using this method.")

        logout_url = f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/logout"
        payload = {
            "client_id": self.client_id,
            "refresh_token": refresh_token,
        }
        if self.client_secret_key:
            payload["client_secret"] = self.client_secret_key

        async with self.session.post(logout_url, data=payload, ssl=self.verify, timeout=self.timeout) as response:
            if response.status >= 400:
                raise KeycloakPostError(f"Hiba a kijelentkeztetés során: {response.status} {response.reason}")

    # További metódusok, ha szükséges