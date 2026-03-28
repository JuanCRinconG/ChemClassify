from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from LogicaMadre.LogicaFirebase.FirebaseConfig import db

BASE_DIR = Path(__file__).resolve().parents[2]
PlataformaWeb = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


@PlataformaWeb.route('/', methods=['GET'])
def index():
    return redirect(url_for('login'))


@PlataformaWeb.route('/login', methods=['GET', 'POST'])
def login():
    error_message = ''
    success_message = ''
    account_value = ''

    if request.method == 'POST':
        account_value = request.form.get('accountName', '').strip()
        password = request.form.get('password', '')

        if not account_value and not password:
            error_message = 'Please enter both account name and password'
        elif not account_value:
            error_message = 'Please enter an account name'
        elif not password:
            error_message = 'Please enter a password'
        else:
            # Placeholder for real authentication logic.
            success_message = f'Login POST received for: {account_value}'

    return render_template(
        'PaginasAutenticacion/login.html',
        error_message=error_message,
        success_message=success_message,
        account_value=account_value,
    )


if __name__ == '__main__':
    if db:
        print('ok')
    PlataformaWeb.run(debug=True)
