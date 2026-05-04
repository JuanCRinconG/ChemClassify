"""
Carga variables desde `.env` en la raíz de **AplicacionWeb** (junto a `main.py`).

1. Crea el archivo `.env` si no existe.
2. Puedes partir de `env.graph.example` como plantilla (no subas `.env` a git).

Si está instalado **`python-dotenv`**, se usa `load_dotenv(..., override=True)` para
que **`.env` mande** sobre variables viejas del sistema o del IDE.

Si no hay dotenv, el lector mínimo también aplica los valores del archivo (sobrescribe).

Variables típicas de correo (las lee `ServicioCorreo`):
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM

También puedes definir variables solo en el entorno del sistema o del IDE.
"""

from __future__ import annotations

import os
from pathlib import Path

# Raíz del proyecto web (carpeta que contiene main.py)
_RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
_ARCHIVO_ENV = _RAIZ_PROYECTO / '.env'


def _cargar_env_desde_archivo(ruta: Path) -> None:
    """
    Aplica líneas KEY=VALUE del archivo al entorno solo si la clave aún no existe.

    Soporta comillas simples/dobles alrededor del valor y líneas # comentario.
    """
    if not ruta.is_file():
        return
    try:
        texto = ruta.read_text(encoding='utf-8')
    except OSError:
        return

    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith('#'):
            continue
        if '=' not in linea:
            continue
        clave, _, valor = linea.partition('=')
        clave = clave.strip()
        if not clave:
            continue
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        os.environ[clave] = valor


def _cargar_env() -> None:
    """Carga `.env` con python-dotenv si existe; si no, lector mínimo."""
    try:
        from dotenv import load_dotenv

        load_dotenv(_ARCHIVO_ENV, override=True)
    except ImportError:
        _cargar_env_desde_archivo(_ARCHIVO_ENV)


_cargar_env()


def ruta_archivo_env() -> Path:
    """Ruta esperada del `.env` (útil para mensajes de error o documentación)."""
    return _ARCHIVO_ENV
