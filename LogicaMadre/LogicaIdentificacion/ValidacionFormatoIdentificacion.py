"""Validate account identifiers (institutional email for ChemClasify)."""

from typing import Optional

from Configuraciones.ConfiguracionLogin.DominioPermitido import (
    dominio_correo_normalizado,
    dominio_en_cuenta_es_permitido,
    ejemplo_correo_institucional,
)


def validar_identificador_cuenta(cuenta: str) -> Optional[str]:
    """
    Ensure the account string matches institutional email rules.

    Rules:
    - Non-empty local part before @
    - Exactly one @
    - Domain after @ with at least one dot (FQDN-style)
    - Domain must match Configuraciones.ConfiguracionLogin.DominioPermitido

    Returns None if valid, otherwise a short user-facing error message.
    """
    ejemplo = ejemplo_correo_institucional()
    dominio_cfg = dominio_correo_normalizado()

    cuenta = cuenta.strip()
    if not cuenta:
        return None

    if '@' not in cuenta:
        return f'Enter an email with @ and your institutional domain (e.g. {ejemplo}).'

    if cuenta.count('@') != 1:
        return f'Use a single @ in your account (e.g. {ejemplo}).'

    local, domain = cuenta.split('@', 1)
    if not local:
        return f'Enter the part before @ (e.g. {ejemplo}).'
    if not domain:
        return f'Enter your institutional domain after @ (e.g. @{dominio_cfg}).'
    if '.' not in domain:
        return 'The domain after @ must include a name and extension (e.g. .edu).'

    if not dominio_en_cuenta_es_permitido(domain):
        return f'Use your institutional email only (e.g. {ejemplo}).'

    return None
