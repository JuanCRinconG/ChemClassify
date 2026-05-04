"""
Correo del sistema vía **SMTP** (`smtplib`).

Configura `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_HOST`, `SMTP_PORT` y opcionalmente
`SMTP_FROM` en el archivo `.env` en la raíz del proyecto (junto a `main.py`).
Plantilla: `env.graph.example`.
"""

# Reservado por si se fija un remitente solo en código; hoy se usa `SMTP_FROM` / `SMTP_USER` en `.env`.
CORREO_REMITENTE_SMTP_PREDETERMINADO = ''
