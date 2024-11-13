# connection.py

import aiohttp

class ConnectionManager:
    def __init__(self, timeout=60, verify_ssl=True):
        """Inicializálja a ConnectionManager objektumot."""
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = aiohttp.ClientSession()

    async def post(self, url, data=None, headers=None):
        """HTTP POST kérést küld a megadott URL-re."""
        async with self.session.post(url, data=data, headers=headers, ssl=self.verify_ssl, timeout=self.timeout) as response:
            response.raise_for_status()
            return await response.json()

    async def get(self, url, params=None, headers=None):
        """HTTP GET kérést küld a megadott URL-re."""
        async with self.session.get(url, params=params, headers=headers, ssl=self.verify_ssl, timeout=self.timeout) as response:
            response.raise_for_status()
            return await response.json()

    async def close(self):
        """Bezárja az HTTP kapcsolatot."""
        await self.session.close()