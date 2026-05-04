"""
Envío de correo de prueba vía **SMTP** (`smtplib`).

Carga `.env` al importar el módulo de configuración. Variables: `SMTP_HOST`,
`SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` (opcional; por defecto
igual que `SMTP_USER`). Ver `env.graph.example`.

Gmail: `smtp.gmail.com`, puerto 587, STARTTLS, y **contraseña de aplicación**
(con 2-Step Verification). Otros proveedores: ajusta `SMTP_HOST` / puerto
(465 → SSL implícito).
"""

from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage

import Configuraciones.ConfiguracionCorreo.VariablesGraphCorreo  # noqa: F401 — carga .env


class ErrorEnvioCorreo(Exception):
    """Fallo al enviar correo (mensaje apto para mostrar al usuario)."""


def enviar_correo_prueba(destinatario: str) -> None:
    """Envía un correo de prueba al destinatario usando SMTP."""
    destinatario = (destinatario or '').strip()
    if not destinatario:
        raise ErrorEnvioCorreo('No recipient address.')

    host = (os.environ.get('SMTP_HOST') or 'smtp.gmail.com').strip()
    port_raw = (os.environ.get('SMTP_PORT') or '587').strip()
    try:
        port = int(port_raw)
    except ValueError:
        port = 587
    user = os.environ.get('SMTP_USER', '').strip()
    password = os.environ.get('SMTP_PASSWORD', '').strip()
    sender = (os.environ.get('SMTP_FROM') or user).strip()

    if not user or not password:
        raise ErrorEnvioCorreo(
            'SMTP no esta configurado: pon SMTP_USER y SMTP_PASSWORD en .env '
            '(misma carpeta que main.py; ver env.graph.example).'
        )
    if not sender:
        raise ErrorEnvioCorreo('SMTP: sender esta vacio (pon SMTP_FROM o SMTP_USER).')

    
    ## Si toda la configuracion de SMTP es correcta, se envía el correo de prueba:

    msg = EmailMessage()
    msg['Subject'] = 'ChemClassify — correo de prueba'
    msg['From'] = sender
    msg['To'] = destinatario
    msg.set_content(
        'Este es un correo de prueba de ChemClassify.\n\n'
        'Si recibiste este correo, SMTP esta configurado correctamente.'
    )

    ctx = ssl.create_default_context()
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=45, context=ctx) as smtp:
                smtp.ehlo()
                smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=45) as smtp:
                smtp.ehlo()
                smtp.starttls(context=ctx)
                smtp.ehlo()
                smtp.login(user, password)
                smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError as exc:
        detalle = ''
        if getattr(exc, 'smtp_code', None) is not None:
            detalle = f' [{exc.smtp_code}'
            err = getattr(exc, 'smtp_error', b'') or b''
            if isinstance(err, bytes):
                try:
                    detalle += f' {err.decode("utf-8", errors="replace").strip()}'
                except Exception:
                    detalle += f' {err!r}'
            else:
                detalle += f' {err}'
            detalle += ']'
        raise ErrorEnvioCorreo(
            'Fallo la autenticacion de SMTP. Usa la misma cuenta de Google en SMTP_USER como la '
            'donde creaste la contraseña de aplicacion (16 chars, no espacios). Habilita la Verificacion en 2 pasos. '
            'Si SMTP_* fue alguna vez configurado en Windows / IDE, los valores antiguos se ignoran ahora '
            f'(`.env` wins).{detalle}'
        ) from exc
    except smtplib.SMTPException as exc:
        raise ErrorEnvioCorreo(f'Error de SMTP: {exc}') from exc
