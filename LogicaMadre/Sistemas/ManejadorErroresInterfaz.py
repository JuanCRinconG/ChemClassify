"""
Lugar central para el texto de error y el contexto de las plantillas.

Plantillas que usan el alerta naranja compartido deben recibir `error_message`
(str o vacío). Mantiene los mensajes aquí para que la redacción sea consistente en toda la aplicación.
"""

from typing import Any, Dict, Optional


class ManejadorErroresInterfaz:
    """Construye cadenas de error estandarizadas y un contexto opcional para las plantillas."""

    # Login (auth form)
    LOGIN_CUENTA_Y_CLAVE_VACIOS = 'Por favor, ingresa ambos nombres de cuenta y contraseña'
    LOGIN_CUENTA_VACIA = 'Por favor, ingresa un nombre de cuenta'
    LOGIN_CLAVE_VACIA = 'Por favor, ingresa una contraseña'

    @classmethod
    def contexto_error(cls, mensaje: str, base: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Combina `error_message` en un diccionario de contexto para las plantillas."""
        ctx: Dict[str, Any] = dict(base or {})
        ctx['error_message'] = mensaje
        return ctx

    @classmethod
    def limpiar_error_en_contexto(cls, base: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ctx: Dict[str, Any] = dict(base or {})
        ctx['error_message'] = ''
        return ctx
