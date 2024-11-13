# exceptions.py

class KeycloakAuthenticationError(Exception):
    """Hiba az authentikáció során."""
    pass

class KeycloakAuthorizationConfigError(Exception):
    """Hiba az engedélyezési konfigurációban."""
    pass

class KeycloakDeprecationError(Exception):
    """Elavult funkció használata."""
    pass

class KeycloakGetError(Exception):
    """Hiba GET kérés során."""
    pass

class KeycloakInvalidTokenError(Exception):
    """Érvénytelen token hiba."""
    pass

class KeycloakPostError(Exception):
    """Hiba POST kérés során."""
    pass

class KeycloakRPTNotFound(Exception):
    """RPT nem található."""
    pass

def raise_error_from_response(response, error_class):
    """Hibát dob, ha a válasz állapota hibát jelez."""
    if response.status >= 400:
        raise error_class(f"{response.status}: {response.reason}")