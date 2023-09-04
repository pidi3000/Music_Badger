

from flask import request, jsonify

from . import blueprint as api_pages

from ....data_handler.song_handler import Song
from ....data_handler.user_input_handler import User_Input_Handler

from ....help_functions import exception_to_dict, obj_list_to_json


####################################################################################################
# Handle GET song
####################################################################################################


@api_pages.route('/get', methods=["POST", "GET"])
def get():
    if True:  # request.method == 'POST':
        id = User_Input_Handler.get_as_type_or_none(
            request.values.get("id"), int)
        yt_id = User_Input_Handler.get_as_type_or_none(
            request.values.get("yt_id"), str)

        # TODO make this better, maybe auto detect if yt_id is link or acutally and ID
        if yt_id is None:
            yt_id = User_Input_Handler.extract_yt_ID(User_Input_Handler.get_as_type_or_none(
                request.values.get("yt_link"), str))

        try:
            new_song = Song.get(id=id, yt_id=yt_id)
            response = new_song.to_json()
        except (TypeError, LookupError) as e:
            response = exception_to_dict(e)

        # new_song = Artist.get_by_ID(2)
        # response = (exception_to_dict(e))

        return jsonify(response)


@api_pages.route('/info', methods=["POST", "GET"])
def get_info():
    if True:  # request.method == 'POST':
        yt_id = User_Input_Handler.extract_yt_ID(User_Input_Handler.get_as_type_or_none(
            request.values.get("yt_id"), str))
        
        print("yt_id: ", yt_id)

        try:
            song_info = Song.get_info(yt_id=yt_id)
            response = song_info
        except (TypeError) as e:
            response = exception_to_dict(e)
            raise

        return jsonify(response)

    # return jsonify(exception_to_dict(NotImplementedError("")))


@api_pages.route('/list', methods=["POST", "GET"])
def list_songs():
    all_songs = Song.get_all()

    # return all_songs
    return obj_list_to_json(all_songs)
    # return render_template("song_list.html", songs=all_songs)


####################################################################################################
# Handle ADD song
####################################################################################################
@api_pages.route('/add', methods=["POST",])
def add():
    if request.method == 'POST':

        print()

        if request.is_json:
            song_data_list: dict = request.get_json()
            # print(song_data_list)
            # print(request.json)
            print(len(request.json))
            # print()
            # print()
            # pprint(request.json)
            # print()
            # print()

            response = add_song_list(song_data_list)
            print("Response 1:\n", response, "\n")
            return jsonify(response)

        # return jsonify(False)
        # print()
        # print()
        # pprint(request.values)
        # print()
        # print()

        # yt_id = User_Input_Handler.get_as_type_or_none(request.values.get("yt_id"), str)
        # artist_data = User_Input_Handler.get_as_type_or_none(request.values.getlist("artists"), str)
        # song_title = User_Input_Handler.get_as_type_or_none(request.values.get("song_title"), str)
        # song_extras = User_Input_Handler.get_as_type_or_none(request.values.get("song_extras"), str)

        yt_id = request.values.get("yt_id")
        artist_data = request.values.getlist("artists")
        song_title = request.values.get("song_title")
        song_extras = request.values.get("song_extras")

        print("Debug Artist: ", artist_data)

        response = handle_add_song(yt_id, artist_data, song_title, song_extras)
        print("Response 2:\n", response, "\n")
        return jsonify(response)


    # return render_template("song_ingest.html")
    # return jsonify("Response 3:\n", False, "\n")


def handle_add_song(yt_id: str, artist_data: int | str | list[str], song_title: str | None, song_extras: str | list[str] | None):
    response = None
    try:
        yt_id = User_Input_Handler.extract_yt_ID(
            User_Input_Handler.get_as_type_or_none(yt_id, str))
        artist_data = User_Input_Handler.get_as_type_or_none(artist_data, str)
        song_title = User_Input_Handler.get_as_type_or_none(song_title, str)
        song_extras = User_Input_Handler.get_as_type_or_none(song_extras, str)

        print("Debug Artist: ", artist_data)
        new_song = Song.create(yt_id, artist_data, song_title, song_extras)
        response = new_song.to_json()

    except (ValueError, LookupError) as e:
        # print("error")
        # print(e)
        response = (exception_to_dict(e))

    return response


def add_song_list(song_data_list: dict, include_succes_msg: bool = False):
    responses = {}

    if "songs" in song_data_list:
        for song in song_data_list["songs"]:
            song: dict
            # print(song)

            yt_id = song.get("yt_id")
            artist_data = song.get("artists")
            song_title = song.get("song_title")
            song_extras = song.get("song_extras")

            # yt_id = User_Input_Handler.get_as_type_or_none(song["yt_id"], str)
            # artist_data = User_Input_Handler.get_as_type_or_none(song["artists"], str)
            # song_title = User_Input_Handler.get_as_type_or_none(song["song_title"], str)
            # song_extras = User_Input_Handler.get_as_type_or_none(song["song_extras"], str)

            response = handle_add_song(
                yt_id, artist_data, song_title, song_extras)

            if isinstance(response, dict):
                responses[yt_id] = response

            elif response is True and include_succes_msg:
                responses[yt_id] = response

    else:
        responses = exception_to_dict(ValueError(" No key 'songs' in data"))

    return responses


####################################################################################################
# Handle EDIT song
####################################################################################################
@api_pages.route('/edit', methods=["POST",])
def edit():
    if request.method == 'POST':

        print()

        # yt_id = User_Input_Handler.get_as_type_or_none(request.values.get("yt_id"), str)
        # artist_data = User_Input_Handler.get_as_type_or_none(request.values.getlist("artists"), str)
        # song_title = User_Input_Handler.get_as_type_or_none(request.values.get("song_title"), str)
        # song_extras = User_Input_Handler.get_as_type_or_none(request.values.get("song_extras"), str)

        yt_id = request.values.get("yt_id")
        artist_data = request.values.getlist("artists")
        song_title = request.values.get("song_title")
        song_extras = request.values.get("song_extras")

        response = handle_edit_song(
            yt_id, artist_data, song_title, song_extras)
        print("Response 2:\n", response, "\n")
        return jsonify(response)


    # return render_template("song_edit.html")


def handle_edit_song(yt_id: str, artist_data: int | str | list[str], song_title: str | None, song_extras: str | list[str] | None):

    response = None
    try:
        yt_id = User_Input_Handler.extract_yt_ID(
            User_Input_Handler.get_as_type_or_none(yt_id, str))
        artist_data = User_Input_Handler.get_as_type_or_none(artist_data, str)
        song_title = User_Input_Handler.get_as_type_or_none(song_title, str)
        song_extras = User_Input_Handler.get_as_type_or_none(song_extras, str)

        print("Debug EDIT Artist: ", artist_data)
        new_song = Song.edit(yt_id, artist_data, song_title, song_extras)
        response = new_song.to_json()

    except (ValueError, LookupError) as e:
        # print("error")
        # print(e)
        response = (exception_to_dict(e))

    # response = (exception_to_dict(NotImplementedError("Not yet implemented")))

    return response
