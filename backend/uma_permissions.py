# uma_permissions.py

def build_permission_param(permissions):
    """Összeállítja a jogosultsági paramétereket az UMA engedélyezéshez.

    :param permissions: Jogosultságok listája
    :return: Permissziós paraméterek szótára
    """
    return {'permission': permissions}

class AuthStatus:
    def __init__(self, is_authorized, message=None):
        """Inicializálja az AuthStatus objektumot.

        :param is_authorized: Boolean érték, amely jelzi az engedélyezés sikerességét
        :param message: Hibaüzenet vagy egyéb információ
        """
        self.is_authorized = is_authorized
        self.message = message