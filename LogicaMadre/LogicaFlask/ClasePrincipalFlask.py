from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from Configuraciones.ConfiguracionLogin.DominioPermitido import (
    ejemplo_correo_institucional,
)
from LogicaMadre.LogicaIdentificacion.ValidacionFormatoIdentificacion import (
    validar_identificador_cuenta,
)
from LogicaMadre.Sistemas.ManejadorErroresInterfaz import ManejadorErroresInterfaz

BASE_DIR = Path(__file__).resolve().parents[2]
PlataformaWeb = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


@PlataformaWeb.route('/', methods=['GET'])
def index():
    """Root URL: send users straight to the login screen (no separate index template)."""
    return redirect(url_for('login'), code=302)


@PlataformaWeb.route('/login', methods=['GET', 'POST'])
def login():
    error_message = ''
    success_message = ''
    account_value = ''

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
                # Placeholder for real authentication logic.
                success_message = f'Login POST received for: {account_value}'

    return render_template(
        'PaginasAutenticacion/login.html',
        error_message=error_message,
        success_message=success_message,
        account_value=account_value,
        ejemplo_correo=ejemplo_correo_institucional(),
    )
