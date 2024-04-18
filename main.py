from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_restful import Api
from werkzeug.utils import secure_filename
import data.db_session as db_session

from data.users import User
from data.notes import Note

import data.errors_handler as errors_handler
import data.users_resources as users_resources
import data.notes_resources as notes_resources

from forms.user import RegisterForm, LoginForm, EditProfileForm
from forms.notes import CreateNoteForm, EditNoteForm

import os
import dotenv
import random
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

    app.register_blueprint(errors_handler.blueprint)

    api.add_resource(users_resources.UsersListResource, '/api/users')
    api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')

    api.add_resource(notes_resources.NoteListResource, '/api/notes')
    api.add_resource(notes_resources.NoteResource, '/api/notes/<int:note_id>')

    app.run(port=5000)


@app.route('/')
@app.route('/index')
def index():
    user = current_user
    # Если пользователь не авторизован - покажем страницу-презентацию сайта
    if not user.is_authenticated:
        return render_template('index.html', title='Заметки')
    # Если авторизован - покажем кастомную страницу с заметками пользователя
    notes = requests.get('http://localhost:5000/api/notes').json()['notes']

    # Булевая функция. True, если есть скрытые заметки, чтобы на странице отобразить текст "Скрытые заметки"
    is_hide_notes = not all([note['is_active'] for note in notes]) and len(notes) != 0

    return render_template('notes.html', user=current_user, notes=notes, is_hide_notes=is_hide_notes, title='Заметки')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nick == form.nick.data).first()
        # Если юзер ввёл верный логин/пароль - система авторизует его
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        # Иначе высветится ошибка о неверном логине/пароле
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
        # Валидируются пароли и почта, проверяется, есть ли добавляемый юзер в системе
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

        # Пользователь создаётся, юзера перекидывает на страницу авторизации
        requests.post('http://localhost:5000/api/users', json=user_params)
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@login_required
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    if user_id != current_user.id:
        return 'Вы не можете редактировать чужой профиль'
    form = EditProfileForm()
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if request.method == 'GET':
        form.name.data = user.name
        form.surname.data = user.surname
        form.background_color.data = user.background_color
        form.notes_background_color.data = user.notes_background_color
    if form.validate_on_submit():
        user.name = form.name.data
        user.surname = form.surname.data
        user.background_color = form.background_color.data
        user.notes_background_color = form.notes_background_color.data
        session.commit()
        return redirect('/')
    return render_template('edit_profile.html', title='Профиль', form=form)


@app.route('/create_note', methods=['GET', 'POST'])
def create_note():
    form = CreateNoteForm()

    if request.method == "GET":
        # Установить значение цвета заметки на дефолтное из настроек пользователя
        form.background_color.data = current_user.notes_background_color

    if form.validate_on_submit() and request.method == 'POST':
        note_params = {
            'title': form.title.data,
            'text': form.text.data,
            'background_color': form.background_color.data
        }
        # Формируется ссылка на картинку
        if 'background_image' in request.files:
            # Если юзер загрузил картинку, она получит случайное имя (во избежание загрузки картинок с одинаковыми
            # названиями) и сохранится в static/user_images
            file = request.files['background_image']
            filename = secure_filename(file.filename)
            frmt = filename.split('.')[-1]
            if frmt in ['jpg', 'jpeg', 'png', 'gif']:
                filename = f"{random.randint(1000000, 9999999)}.{frmt}"
                file.save(os.path.join('static/user_images', filename))
                note_params['background_image'] = f'static/user_images/{filename}'
            else:
                note_params['background_image'] = 'static/user_images/default.jpg'
        else:
            # Если юзер не загрузил картинку, будет использоваться стандартная
            note_params['background_image'] = 'static/user_images/default.jpg'
        # Владельцем заметки назначается авторизованный в данный момент юзер
        note_params['owner_user'] = current_user.id

        # Заметка создаётся, юзер возвращается на главную страницу со всеми заметками
        requests.post('http://localhost:5000/api/notes', json=note_params)
        return redirect('/')

    return render_template('create_note.html', title='Новая заметка', form=form)


@app.route('/note/<int:note_id>/<int:user_id>')
def read_note(note_id, user_id):
    if user_id == current_user.id:
        note = requests.get(f'http://localhost:5000/api/notes/{note_id}').json()['note']
        return render_template('read_note.html', note=note, title=note['title'])
    return redirect('/')


@app.route('/edit_note/<int:note_id>/<int:user_id>')
def edit_note():
    pass


@app.route('/delete_note/<int:note_id>/<int:user_id>')
def delete_note(note_id, user_id):
    if user_id == current_user.id:
        requests.delete(f'http://localhost:5000/api/notes/{note_id}')
    return redirect('/')


@app.route('/hide_note/<int:note_id>/<int:user_id>')
def hide_note(note_id, user_id):
    if user_id == current_user.id:
        session = db_session.create_session()
        note = session.query(Note).filter(Note.id == note_id).first()
        note.is_active = not note.is_active
        session.commit()
    return redirect('/')


if __name__ == '__main__':
    main()
