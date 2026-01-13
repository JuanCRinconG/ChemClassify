from flask import Flask, render_template

from FirebaseConfig import db

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    if db:
        print('ok')
    app.run(debug=True)
