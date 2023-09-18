

from flask import request, jsonify

from . import blueprint as api_pages

from badger.data_handler.api_response_handler import badger_Response
from badger.data_handler.user_input_handler import User_Input_Handler
from badger.db_models import Artist


@api_pages.route('/artist', methods=["GET"])
@badger_Response(debug=False)
def index():
    if request.method == 'GET':
        id = User_Input_Handler.get_as_type_or_none(
            request.values.get("id"), int)

        artist = Artist.get_by_ID(id=id)
        return artist


@api_pages.route('/artist/list', methods=["GET"])
@badger_Response
def list():
    if request.method == 'GET':
        # all_artists = Artist.get_all()
        page_id = request.values.get("page_id", type=int)
        all_artists = Artist.get_page(page_num=page_id)

        return all_artists
