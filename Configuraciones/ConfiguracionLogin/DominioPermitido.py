"""
Allowed email domain for ChemClasify institutional login.

Edit DOMINIO_CORREO_PERMITIDO for your organization, or set the environment
variable CHEMCLASSIFY_DOMINIO_CORREO (e.g. on the server) without changing code.
"""

import os

# Default when env is unset: change this to your institution's domain (no @).
_DOMINIO_PREDETERMINADO = 'ucundinamarca.edu.co'

_DOMINIO_ENV = os.environ.get('CHEMCLASSIFY_DOMINIO_CORREO', '').strip()
DOMINIO_CORREO_PERMITIDO: str = _DOMINIO_ENV or _DOMINIO_PREDETERMINADO

# If True, addresses like user@alumnos.institucion.edu match DOMINIO institucion.edu
PERMITIR_SUBDOMINIOS_DEL_DOMINIO = False


def dominio_correo_normalizado() -> str:
    """dominio de correo en minusculas sin el @ al inicio."""
    return DOMINIO_CORREO_PERMITIDO.strip().lower().lstrip('@')


def ejemplo_correo_institucional(parte_local: str = 'user') -> str:
    """ejemplo de correo para las sugerencias de la interfaz y los mensajes de error."""
    return f'{parte_local.strip()}@{dominio_correo_normalizado()}'


def dominio_en_cuenta_es_permitido(dominio_tras_arroba: str) -> bool:
    """True si el dominio despues del @ es permitido (exacto o subdominio cuando esta habilitado)."""
    d = dominio_tras_arroba.strip().lower()
    permitido = dominio_correo_normalizado()
    if not d or not permitido:
        return False
    if d == permitido:
        return True
    if PERMITIR_SUBDOMINIOS_DEL_DOMINIO and d.endswith('.' + permitido):
        return True
    return False
