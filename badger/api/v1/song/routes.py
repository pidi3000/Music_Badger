

from flask import request, jsonify
import traceback

from . import blueprint as api_pages

from ....data_handler.song_handler import Song
from ....data_handler.user_input_handler import User_Input_Handler

from ....help_functions import exception_to_dict, obj_list_to_json


####################################################################################################
# Handle song
####################################################################################################

@api_pages.route('/song', methods=["GET", "POST", "PUT"])
def index():
    response = None

    if request.method == 'GET':
        # response = handle_get_song_path()
        response = _handle_get_song()

    if request.method == 'POST':
        # response = handle_add_song_path()
        song_data = _get_song_data()
        response = _handle_add_song(song_data)

    if request.method == 'PUT':
        # response = handle_edit_song_path()
        song_data = _get_song_data()
        response = _handle_edit_song(song_data)

    return response
    # return jsonify(response)


@api_pages.route('/song/info', methods=["GET"])
def get_info():
    if request.method == 'GET':
        yt_id = User_Input_Handler.extract_yt_ID(request.values.get("yt_id"))

        print("yt_id: ", yt_id)
        # return str(yt_id), 200

        try:
            song_info = Song.get_info(yt_id=yt_id)
            response = song_info
        except (TypeError) as e:
            response = exception_to_dict(e)
            raise

        return jsonify(response)

    # return jsonify(exception_to_dict(NotImplementedError("")))


####################################################################################################
# Handle GET song
####################################################################################################
def _handle_get_song():
    def _print_debug(var_name):
        return
        print("DEBUG GET: ", var_name, "\t",request.values.get(var_name), "\t", type(request.values.get(var_name)))

    _print_debug("all")
    _print_debug("id")
    _print_debug("yt_id")

    all = User_Input_Handler.get_as_type_or_none(
        request.values.get("all"), bool)

    if all:
        all_songs = Song.get_all()
        return obj_list_to_json(all_songs)  # TODO use API response handler

    id = User_Input_Handler.get_as_type_or_none(request.values.get("id"), int)
    yt_id = User_Input_Handler.extract_yt_ID(request.values.get("yt_id")) if id is None else None

    try:
        new_song = Song.get(id=id, yt_id=yt_id)
        response = new_song.to_json()
    except (TypeError, LookupError) as e:
        response = exception_to_dict(e)
        traceback.print_exc()

    # new_song = Artist.get_by_ID(2)
    # response = (exception_to_dict(e))

    return response


####################################################################################################
# Handle ADD song
####################################################################################################
def _handle_add_song(song_data: dict):
    response = None
    try:
        print("Debug ADD: ", song_data)
        new_song = Song.create(
            yt_id=song_data["yt_id"],
            artist_data=song_data["artists"],
            song_title=song_data["title"],
            song_extras=song_data["extras"]
        )

        response = new_song.to_json()

    except (ValueError, LookupError) as e:
        # print("error")
        # print(e)
        response = (exception_to_dict(e))

    return response


####################################################################################################
# Handle EDIT song
####################################################################################################
def _handle_edit_song(song_data: dict):
    response = None
    try:
        print("Debug EDIT: ", song_data)
        new_song = Song.edit(
            yt_id=song_data["yt_id"],
            artist_data=song_data["artists"],
            song_title=song_data["title"],
            song_extras=song_data["extras"]
        )

        response = new_song.to_json()

    except (ValueError, LookupError) as e:
        # print("error")
        # print(e)
        response = (exception_to_dict(e))

    return response


####################################################################################################
# Get song data from request
####################################################################################################
def _get_song_data():
    """
    Get song data from request body (json)

    Returns
    -------
    dict
        dict containg all provided keys, but only the yt_id key is requiered\n
        ```
        {
            "yt_id": "string",
            "artists": [
                "string",
            ],
            "title": "string",
            "extras": "string",
        }
        ```
    """
    if request.is_json:
        song_data: dict = request.get_json()
        print()
        print("DEBUG: song data")
        print(song_data)
        print()
        # print(request.json)
        # print()
        # print(len(request.json))
        # print()

        if "yt_id" not in song_data:
            raise KeyError("The key yt_id must be set")

        yt_id = song_data["yt_id"]
        artist_data = song_data.get("artists")
        song_title = song_data.get("title")
        song_extras = song_data.get("extras")

        yt_id = User_Input_Handler.extract_yt_ID(yt_id)
        artist_data = User_Input_Handler.get_as_type_or_none(artist_data, str)
        song_title = User_Input_Handler.get_as_type_or_none(song_title, str)
        song_extras = User_Input_Handler.get_as_type_or_none(song_extras, str)

        data = {
            "yt_id": yt_id,
            "artists": artist_data,
            "title": song_title,
            "extras": song_extras,
        }

        return data

    raise TypeError("Request body must be in json format")
