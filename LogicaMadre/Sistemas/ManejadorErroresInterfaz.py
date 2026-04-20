"""
Central place for user-facing error text and template context.

Templates that use the shared orange alert should receive `error_message`
(str or empty). Keep messages here so wording stays consistent app-wide.
"""

from typing import Any, Dict, Optional


class ManejadorErroresInterfaz:
    """Builds standardized error strings and optional render_template context."""

    # Login (auth form)
    LOGIN_CUENTA_Y_CLAVE_VACIOS = 'Please enter both account name and password'
    LOGIN_CUENTA_VACIA = 'Please enter an account name'
    LOGIN_CLAVE_VACIA = 'Please enter a password'

    @classmethod
    def contexto_error(cls, mensaje: str, base: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Merge `error_message` into a template context dict."""
        ctx: Dict[str, Any] = dict(base or {})
        ctx['error_message'] = mensaje
        return ctx

    @classmethod
    def limpiar_error_en_contexto(cls, base: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ctx: Dict[str, Any] = dict(base or {})
        ctx['error_message'] = ''
        return ctx
