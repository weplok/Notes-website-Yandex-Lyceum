import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Note(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'notes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    owner_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    title = sqlalchemy.Column(sqlalchemy.String)
    text = sqlalchemy.Column(sqlalchemy.String)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    background_image = sqlalchemy.Column(sqlalchemy.String, default='static/user_images/default.jpg')
    background_color = sqlalchemy.Column(sqlalchemy.String)
    border_color = sqlalchemy.Column(sqlalchemy.String)

# Для миграции БД выполнить:
# alembic revision --autogenerate -m "comment"
# alembic upgrade head