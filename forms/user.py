from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ColorField, BooleanField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    nick = StringField('Никнейм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])

    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    nick = StringField('Никнейм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')

    submit = SubmitField('Войти')


class EditProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    background_color = ColorField('Вы можете изменить цвет фона на сайте')
    notes_background_color = ColorField('Вы можете изменить стандартный цвет фона заметки')

    submit = SubmitField('Изменить данные')
