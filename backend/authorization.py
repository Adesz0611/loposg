# authorization.py

class Authorization:
    def __init__(self, keycloak_openid):
        """Inicializálja az Authorization objektumot KeycloakOpenID instanciával."""
        self.keycloak_openid = keycloak_openid

    async def authorize(self, token, required_roles=None):
        """Ellenőrzi, hogy a tokenhez tartozó felhasználó rendelkezik-e a szükséges szerepekkel.

        :param token: Felhasználói hozzáférési token
        :param required_roles: Szükséges szerepek listája
        :return: True, ha engedélyezett, különben False
        """
        try:
            # Felhasználói információk lekérése a token alapján
            user_info = await self.keycloak_openid.userinfo(token)
            user_roles = user_info.get('realm_access', {}).get('roles', [])

            if required_roles:
                # Ellenőrzi, hogy a felhasználó rendelkezik-e az összes szükséges szereppel
                return all(role in user_roles for role in required_roles)
            else:
                # Ha nincsenek meghatározva szerepek, akkor engedélyezett
                return True
        except Exception as e:
            print(f"Authorization failed: {e}")
            return False