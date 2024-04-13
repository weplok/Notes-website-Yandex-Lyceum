from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, ColorField, FileField
from wtforms.validators import DataRequired, Length


class CreateNoteForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=64)])
    text = TextAreaField('Заметка', validators=[DataRequired()])
    background_image = FileField('Вы можете добавить красивую картинку в качестве баннера заметки')
    background_color = ColorField('Вы можете выбрать красивый цвет для своей заметки')

    submit = SubmitField('Добавить заметку')


class EditNoteForm(FlaskForm):
    pass
