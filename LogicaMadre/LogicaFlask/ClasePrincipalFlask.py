import os
from pathlib import Path

from firebase_admin import auth

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

import LogicaMadre.LogicaFirebase.FirebaseConfig  # noqa: F401 — init Admin SDK before auth

from Configuraciones.ConfiguracionLogin.DominioPermitido import (
    ejemplo_correo_institucional,
)
from Configuraciones.ConfiguracionLogin.FirebaseClienteWeb import (
    firebase_web_config_dict,
)
from LogicaMadre.LogicaIdentificacion.ValidacionFormatoIdentificacion import (
    contexto_validacion_correo_cliente,
    validar_identificador_cuenta,
)
from LogicaMadre.LogicaCorreo.ServicioCorreo import ErrorEnvioCorreo, enviar_correo_prueba
from LogicaMadre.Sistemas.ManejadorErroresInterfaz import ManejadorErroresInterfaz

BASE_DIR = Path(__file__).resolve().parents[2]
PlataformaWeb = Flask(
    __name__,
    template_folder=str(BASE_DIR / 'templates'),
    static_folder=str(BASE_DIR / 'static'),
)
PlataformaWeb.secret_key = os.environ.get(
    'FLASK_SECRET_KEY',
    'chemclassify-dev-secret-change-in-production',
)


@PlataformaWeb.route('/', methods=['GET'])
def index():
    """Root URL: send users straight to the login screen (no separate index template)."""
    return redirect(url_for('login'), code=302)


def _session_apply_from_token(decoded: dict) -> None:
    session['uid'] = decoded['uid']
    session['email'] = decoded.get('email') or ''


@PlataformaWeb.route('/login', methods=['GET', 'POST'])
def login():
    error_message = ''
    success_message = ''
    account_value = ''

    if request.method == 'POST' and request.is_json:
        payload = request.get_json(silent=True) or {}
        id_token = (payload.get('idToken') or '').strip()
        if not id_token:
            return jsonify(error='Falta el idToken.'), 400
        try:
            decoded = auth.verify_id_token(id_token)
        except Exception:
            return jsonify(error='Ingreso inválido o expirado. Por favor, inténtalo de nuevo.'), 401

        email = (decoded.get('email') or '').strip()
        if not email:
            return jsonify(error='Tu cuenta no tiene un correo electrónico registrado.'), 400

        ident_error = validar_identificador_cuenta(email)
        if ident_error:
            return jsonify(error=ident_error), 400

        _session_apply_from_token(decoded)
        return jsonify(redirect=url_for('principal'))

    if request.method == 'POST':
        account_value = request.form.get('accountName', '').strip()
        password = request.form.get('password', '')

        if not account_value and not password:
            error_message = ManejadorErroresInterfaz.LOGIN_CUENTA_Y_CLAVE_VACIOS
        elif not account_value:
            error_message = ManejadorErroresInterfaz.LOGIN_CUENTA_VACIA
        elif not password:
            error_message = ManejadorErroresInterfaz.LOGIN_CLAVE_VACIA
        else:
            ident_error = validar_identificador_cuenta(account_value)
            if ident_error:
                error_message = ident_error
            else:
                error_message = (
                    'Use los botones de Ingresar o Crear cuenta para que Firebase pueda verificar tu contraseña.'
                )

    if request.method == 'GET' and session.get('uid'):
        return redirect(url_for('principal'))

    return render_template(
        'PaginasAutenticacion/login.html',
        error_message=error_message,
        success_message=success_message,
        account_value=account_value,
        ejemplo_correo=ejemplo_correo_institucional(),
        firebase_web_config=firebase_web_config_dict(),
        login_email_rules=contexto_validacion_correo_cliente(),
    )


@PlataformaWeb.route('/principal', methods=['GET'])
def principal():
    if not session.get('uid'):
        return redirect(url_for('login'))
    return render_template(
        'PaginasSistema/principal.html',
        session_email=session.get('email', ''),
    )


@PlataformaWeb.route('/enviar-correo-prueba', methods=['POST'])
def enviar_correo_prueba_vista():
    """POST: envía un correo de prueba al email de la sesión (SMTP_* en .env)."""
    if not session.get('uid'):
        return redirect(url_for('login'))

    destinatario = (session.get('email') or '').strip()
    if not destinatario:
        flash('No existe un correo en la sesión.', 'error')
        return redirect(url_for('principal'))

    try:
        enviar_correo_prueba(destinatario)
    except ErrorEnvioCorreo as exc:
        flash(str(exc), 'error')
    except Exception:
        flash('Error al enviar el correo de prueba.', 'error')
    else:
        flash(f'Correo de prueba enviado a {destinatario}.', 'success')

    return redirect(url_for('principal'))


@PlataformaWeb.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))
