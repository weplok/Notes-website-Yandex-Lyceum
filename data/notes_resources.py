from flask import jsonify
from flask_restful import abort, Resource, reqparse

from . import db_session
from .notes import Note


note_params = (
    'id',
    'owner_user',
    'user.name',
    'user.surname',
    'title',
    'text',
    'create_date',
    'is_active',
)


parser = reqparse.RequestParser()
parser.add_argument('owner_user', required=True)
parser.add_argument('title', required=True)
parser.add_argument('text', required=True)


def abort_if_note_not_found(note_id):
    session = db_session.create_session()
    note = session.query(Note).get(note_id)
    if not note:
        abort(404, message=f"Note {note_id} not found")


class NoteResource(Resource):
    def get(self, note_id):
        abort_if_note_not_found(note_id)
        session = db_session.create_session()
        note = session.query(Note).get(note_id)
        return jsonify({'note': note.to_dict(
            only=note_params)})

    def delete(self, note_id):
        abort_if_note_not_found(note_id)
        session = db_session.create_session()
        note = session.query(Note).get(note_id)
        session.delete(note)
        session.commit()
        return jsonify({'success': 'OK'})


class NoteListResource(Resource):
    def get(self):
        session = db_session.create_session()
        notes = session.query(Note).all()
        return jsonify({'notes': [item.to_dict(
            only=note_params) for item in notes]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        note = Note(
            owner_user=int(args['owner_user']),
            title=str(args['title']),
            text=str(args['text']),
        )
        session.add(note)
        session.commit()
        return jsonify({'id': note.id})
