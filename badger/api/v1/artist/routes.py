

from flask import request, jsonify

from . import blueprint as api_pages

from ....data_handler.song_handler import Artist
from ....data_handler.user_input_handler import User_Input_Handler

from ....help_functions import exception_to_dict, obj_list_to_json



@api_pages.route('/get', methods=["POST", "GET"])
def get():
    if True: #request.method == 'POST':
        id = User_Input_Handler.get_as_type_or_none(request.values.get("id"), int)

        try:
            artist = Artist.get_by_ID(id=id)
            response = artist.to_json()
        except (TypeError, LookupError) as e:
            response = exception_to_dict(e)

        return jsonify(response)
    
    # return render_template("artist_get.html")


@api_pages.route('/list', methods=["GET", "POST" ])
def list():
    all_artists = Artist.get_all()

    # return all_artists
    return obj_list_to_json(all_artists)
    # return render_template("artist_list.html", artists=all_artists)

