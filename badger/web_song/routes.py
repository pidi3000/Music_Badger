

# from ..db_models import

import flask
from flask import render_template, request, url_for, redirect, jsonify
import json

from . import blueprint as song_pages
from ..data_handler.song_handler import Song, Artist
from ..help_functions import exception_to_dict, get_as_type_or_none, extract_yt_ID

import random
from pprint import pprint


@song_pages.route('/')
def index():
    return redirect(url_for('.list_songs'))

####################################################################################################
# Handle GET song
####################################################################################################

@song_pages.route('/get_song', methods=["GET", "POST"])
def get():
    if request.method == 'POST':
        id = get_as_type_or_none(request.values.get("id"), int)
        yt_id = extract_yt_ID(get_as_type_or_none(
            request.values.get("yt_id"), str))

        try:
            new_song = Song.get(id=id, yt_id=yt_id)
            response = new_song.to_json()
        except (TypeError, LookupError) as e:
            response = exception_to_dict(e)

        # new_song = Artist.get_by_ID(2)
        # response = (exception_to_dict(e))

        return jsonify(response)

    return render_template("song_get.html")


@song_pages.route('/get_song_info', methods=["GET", "POST"])
def get_info():
    if request.method == 'POST':
        yt_id = extract_yt_ID(get_as_type_or_none(
            request.values.get("yt_id"), str))

        try:
            song_info = Song.get_info(yt_id=yt_id)
            response = song_info
        except (TypeError) as e:
            response = exception_to_dict(e)
            raise

        return jsonify(response)

    return jsonify(exception_to_dict(NotImplementedError("")))


@song_pages.route('/list_songs', methods=["GET", ])
def list_songs():
    all_songs = Song.get_all()
    return render_template("song_list.html", songs=all_songs)


####################################################################################################
# Handle ADD song
####################################################################################################
@song_pages.route('/add_song', methods=["GET", "POST"])
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

        # yt_id = get_as_type_or_none(request.values.get("yt_id"), str)
        # artist_data = get_as_type_or_none(request.values.getlist("artists"), str)
        # song_title = get_as_type_or_none(request.values.get("song_title"), str)
        # song_extras = get_as_type_or_none(request.values.get("song_extras"), str)

        yt_id = request.values.get("yt_id")
        artist_data = request.values.getlist("artists")
        song_title = request.values.get("song_title")
        song_extras = request.values.get("song_extras")

        print("Debug Artist: ", artist_data)

        response = handle_add_song(yt_id, artist_data, song_title, song_extras)
        print("Response 2:\n", response, "\n")
        return jsonify(response)

        return redirect(url_for('.get', id=new_song.id))
        # return jsonify(new_song.to_json())

    return render_template("song_ingest.html")
    return jsonify("Response 3:\n", False, "\n")


def handle_add_song(yt_id: str, artist_data: int | str | list[str], song_title: str | None, song_extras: str | list[str] | None):
    response = None
    try:
        yt_id = extract_yt_ID(get_as_type_or_none(yt_id, str))
        artist_data = get_as_type_or_none(artist_data, str)
        song_title = get_as_type_or_none(song_title, str)
        song_extras = get_as_type_or_none(song_extras, str)

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

            # yt_id = get_as_type_or_none(song["yt_id"], str)
            # artist_data = get_as_type_or_none(song["artists"], str)
            # song_title = get_as_type_or_none(song["song_title"], str)
            # song_extras = get_as_type_or_none(song["song_extras"], str)

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
@song_pages.route('/edit_song', methods=["GET", "POST"])
def edit():
    if request.method == 'POST':

        print()

        # yt_id = get_as_type_or_none(request.values.get("yt_id"), str)
        # artist_data = get_as_type_or_none(request.values.getlist("artists"), str)
        # song_title = get_as_type_or_none(request.values.get("song_title"), str)
        # song_extras = get_as_type_or_none(request.values.get("song_extras"), str)

        yt_id = request.values.get("yt_id")
        artist_data = request.values.getlist("artists")
        song_title = request.values.get("song_title")
        song_extras = request.values.get("song_extras")

        response = handle_edit_song(
            yt_id, artist_data, song_title, song_extras)
        print("Response 2:\n", response, "\n")
        return jsonify(response)

        return redirect(url_for('.get', id=new_song.id))
        # return jsonify(new_song.to_json())

    return render_template("song_edit.html")


def handle_edit_song(yt_id: str, artist_data: int | str | list[str], song_title: str | None, song_extras: str | list[str] | None):

    response = None
    try:
        yt_id = extract_yt_ID(get_as_type_or_none(yt_id, str))
        artist_data = get_as_type_or_none(artist_data, str)
        song_title = get_as_type_or_none(song_title, str)
        song_extras = get_as_type_or_none(song_extras, str)

        print("Debug EDIT Artist: ", artist_data)
        new_song = Song.edit(yt_id, artist_data, song_title, song_extras)
        response = new_song.to_json()

    except (ValueError, LookupError) as e:
        # print("error")
        # print(e)
        response = (exception_to_dict(e))

    # response = (exception_to_dict(NotImplementedError("Not yet implemented")))

    return response

