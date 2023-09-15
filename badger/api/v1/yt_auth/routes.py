

from flask import request, url_for, session

from . import blueprint as api_pages

from badger.error import BadgerMisingParameter, BadgerUnsupportedMediaType
from badger.data_handler.api_response_handler import badger_Response
from badger.data_handler.youtube_auth_handler import YouTube_Auth_Handler


####################################################################################################
# Handle song routes
####################################################################################################


@api_pages.route('/yt/authorize', methods=["GET"])
@badger_Response()
def authorize():
    response = None
    status_code = None

    return {
        "oauth_url": YouTube_Auth_Handler.get_authorization_url(
            # redirect_uri=url_for(".oauth2callback", _external=True)
        )
    }


@api_pages.route('/yt/oauth2callback', methods=["POST", "GET"])
@badger_Response()
def oauth2callback():
    response = "OK"
    status_code = 204

    if request.method == "POST":

        if not request.is_json:
            raise BadgerUnsupportedMediaType(
                "Request body must be in json format")

        data: dict = request.get_json()
        print()
        print("DEBUG: YT AUTH")
        print(data)
        print()
        # print(request.json)
        # print()
        # print(len(request.json))
        # print()

        if "authorization_response" not in data:
            raise BadgerMisingParameter(
                "The key 'authorization_response' must be set")

        oauth_url = data["authorization_response"]

    else:
        oauth_url = request.url

    YouTube_Auth_Handler.handle_authorization_response(response_uri=oauth_url)

    return None, status_code


@api_pages.route('/yt/revoke', methods=["DELETE", "GET"])
@badger_Response()
def revoke():
    response = "OK"
    status_code = 204

    YouTube_Auth_Handler.revoke_access_token()

    return response, status_code


@api_pages.route('/yt/test', methods=["GET"])
@badger_Response()
def test():
    status_code = 200

    response = {
        "yt": YouTube_Auth_Handler.check_yt_authorized(),
        "session": session.get("YT_AccessToken")
    }

    return response, status_code
