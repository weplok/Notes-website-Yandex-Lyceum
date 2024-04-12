from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_restful import Api
import data.db_session as db_session

from data.users import User
from data.notes import Note

import data.users_resources as users_resources
import data.notes_resources as notes_resources

from forms.user import RegisterForm, LoginForm

import os
import dotenv
import requests

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', default='flask_secret_key')
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init('db/base.db')

    api.add_resource(users_resources.UsersListResource, '/api/users')
    api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')

    api.add_resource(notes_resources.NoteListResource, '/api/notes')
    api.add_resource(notes_resources.NoteResource, '/api/notes/<int:note_id>')

    app.run(port=5000)


@app.route('/')
@app.route('/index')
def index():
    return app.config.get('SECRET_KEY')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nick == form.nick.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/register")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.nick == form.nick.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user_params = {
            'surname': form.surname.data.capitalize(),
            'name': form.name.data.capitalize(),
            'nick': form.nick.data,
            'password': form.password.data
        }
        requests.post('http://localhost:5000/api/users', json=user_params)
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    main()
