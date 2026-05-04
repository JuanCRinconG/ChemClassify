"""Validacion de cuenta de correo (Para la pagina ChemClasify)."""

from typing import Any, Dict, Optional

from Configuraciones.ConfiguracionLogin.DominioPermitido import (
    PERMITIR_SUBDOMINIOS_DEL_DOMINIO,
    dominio_correo_normalizado,
    dominio_en_cuenta_es_permitido,
    ejemplo_correo_institucional,
)


def validar_identificador_cuenta(cuenta: str) -> Optional[str]:
    """
    Asegurar que la string introducida sea la correcta segun el parametro de configuracion.

    Reglas que verifica este modulo:
    - Que la parte antes del @ no este vacia
    - que solo exista un @
    - Que el dominio introducido despues del @ tenga un punto (FQDN-style)
    - El dominio introducido debe coincidir con el de Configuraciones.ConfiguracionLogin.DominioPermitido

    Regresa un None si es valido, de otra forma se utiliza el manejador de errores del sistema.
    """
    ejemplo = ejemplo_correo_institucional()
    dominio_cfg = dominio_correo_normalizado()

    cuenta = cuenta.strip()
    if not cuenta:
        return None

    if '@' not in cuenta:
        return f'Ingresa un correo con @ y tu dominio institucional (e.g. {ejemplo}).'

    if cuenta.count('@') != 1:
        return f'Ingresa solo un @ en el correo (e.g. {ejemplo}).'

    local, domain = cuenta.split('@', 1)
    if not local:
        return f'Ingresa el nombre del correo (e.g. {ejemplo}).'
    if not domain:
        return f'Ingresa el dominio del correo despues del @ (e.g. @{dominio_cfg}).'
    if '.' not in domain:
        return 'El dominio despues del @ debe tener nombre y extension (e.g. .edu).'

    if not dominio_en_cuenta_es_permitido(domain):
        return f'Utiliza solo cuentas institucionales (e.g. {ejemplo}).'

    return None


def contexto_validacion_correo_cliente() -> Dict[str, Any]:
    """
    Reglas para la validacion de correo del cliente antes de Firebase Auth.

    Mantiene las verificaciones institucionales fuera de Firebase hasta que el formato de correo sea permitido.
    """
    return {
        'ejemploCorreo': ejemplo_correo_institucional(),
        'dominioPermitido': dominio_correo_normalizado(),
        'permitirSubdominios': PERMITIR_SUBDOMINIOS_DEL_DOMINIO,
    }
