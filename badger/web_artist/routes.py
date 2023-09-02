

# from ..db_models import

import flask
from flask import render_template, request, url_for, redirect, jsonify
import json

from . import blueprint as ingest_pages
from ..data_handler.song_handler import Artist
from ..help_functions import exception_to_dict, get_as_type_or_none

import random
from pprint import pprint


@ingest_pages.route('/')
def index():
    return redirect(url_for('.list'))


@ingest_pages.route('/get', methods=["GET", "POST"])
def get():
    if request.method == 'POST':
        id = get_as_type_or_none(request.values.get("id"), int)

        try:
            artist = Artist.get_by_ID(id=id)
            response = artist.to_json()
        except (TypeError, LookupError) as e:
            response = exception_to_dict(e)

        return jsonify(response)
    
    return render_template("artist_get.html")


@ingest_pages.route('/list', methods=["GET", ])
def list():
    all_artists = Artist.get_all()
    return render_template("artist_list.html", artists=all_artists)

