from flask import Blueprint, make_response, jsonify

blueprint = Blueprint(
    'errors_handler',
    __name__,
    template_folder='templates'
)


@blueprint.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@blueprint.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)
