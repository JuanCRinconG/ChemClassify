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
            'SMTP not configured: set SMTP_USER and SMTP_PASSWORD in .env '
            '(same folder as main.py; see env.graph.example).'
        )
    if not sender:
        raise ErrorEnvioCorreo('SMTP: sender is empty (set SMTP_FROM or SMTP_USER).')

    msg = EmailMessage()
    msg['Subject'] = 'ChemClassify — test email'
    msg['From'] = sender
    msg['To'] = destinatario
    msg.set_content(
        'This is a test message from ChemClassify.\n\n'
        'If you received this email, SMTP is configured correctly.'
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
            'SMTP authentication failed. Use the same Google account in SMTP_USER as the one '
            'where you created the app password (16 chars, no spaces). Enable 2-Step Verification. '
            'If SMTP_* was ever set in Windows / IDE environment, stale values are ignored now '
            f'(`.env` wins).{detalle}'
        ) from exc
    except smtplib.SMTPException as exc:
        raise ErrorEnvioCorreo(f'SMTP error: {exc}') from exc
