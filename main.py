from flask import Flask, request

import os
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', default='flask_secret_key')


def main():
    app.run(port=5000)


@app.route('/')
@app.route('/index')
def index():
    return app.config.get('SECRET_KEY')


if __name__ == '__main__':
    main()
