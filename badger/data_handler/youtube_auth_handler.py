

import json
import os
from datetime import datetime

import flask
from flask import current_app

import pyyoutube
from pyyoutube import Client, AccessToken, PyYouTubeException

from badger.error import BadgerYTUserNotAuthorized

# CACHING DATA, dict with 'client_id' and 'client_secret'
_client_secret_data: dict = None


class YouTube_Auth_Handler:
    SESSION_NAME_CREDENTIALS = "YT_TOKENS"  # Key name used to store YT credentials
    # Key name used to store YT AccessToken
    SESSION_NAME_ACCESSTOKEN = "YT_AccessToken"
    SESSION_NAME_YT_AUTH_STATE = "Python-YouTube-State"

    ####################################################################################################
    # Secrets file functions
    ####################################################################################################

    @classmethod
    def get_client_secrets_file_path(cls) -> str:
        return current_app.config["MUSIC_BADGER"]["CLIENT_SECRETS_FILE"]

    @classmethod
    def check_secret_file_exists(cls):
        return os.path.isfile(cls.get_client_secrets_file_path())

    @classmethod
    def get_client_secret_data(cls):
        global _client_secret_data

        if _client_secret_data is not None:
            return _client_secret_data

        _client_secret_data = {}

        CLIENT_SECRETS_FILE = cls.get_client_secrets_file_path()

        # extract data

        with open(CLIENT_SECRETS_FILE, "r") as f:
            data = json.load(f)

        _client_secret_data["client_id"] = data["web"]["client_id"]
        _client_secret_data["client_secret"] = data["web"]["client_secret"]

        return _client_secret_data

    ##################################################
    # Credential functions
    ##################################################

    @classmethod
    def get_access_token(cls) -> AccessToken:
        # can raise KeyError, must firts run check_yt_authorized to verify
        # cls.assert_yt_authorized()
        return AccessToken.from_json(flask.session.get(cls.SESSION_NAME_ACCESSTOKEN))

    @classmethod
    def save_access_token(cls, access_token: AccessToken):
        # TODO split and use a string for access and refresh token,
        # using AccessToken class is too confusing
        flask.session[cls.SESSION_NAME_ACCESSTOKEN] = access_token.to_json()

    @classmethod
    def delete_access_token(cls):
        # flask.session[cls.SESSION_NAME_ACCESSTOKEN] = None
        flask.session.pop(cls.SESSION_NAME_ACCESSTOKEN)
        # del flask.session[cls.SESSION_NAME_ACCESSTOKEN]

    @classmethod
    def check_access_token_expired(cls):
        access_token = cls.get_access_token()
        expire_date = datetime.fromtimestamp(access_token.expires_at)
        time_now = datetime.now()

        return expire_date < time_now

    ####################################################################################################
    # Authorization functions
    ####################################################################################################

    @classmethod
    def assert_yt_authorized(cls) -> bool:
        """ Assert YT credentials exist

        Check if the users YT account has authorized the service and client secret file exist
        Otherwise rasie exceptions

        Raises
        ------
        BadgerYTUserNotAuthorized
            when the youtube has not authorized the service

        FileNotFoundError
            when the client secret file was not found        

        """

        # FileNotFoundError
        if cls.SESSION_NAME_ACCESSTOKEN not in flask.session or cls.check_access_token_expired():
            raise BadgerYTUserNotAuthorized()

        if not cls.check_secret_file_exists():
            raise FileNotFoundError("Client secret file not found")

    @classmethod
    def check_yt_authorized(cls) -> bool:
        """
        Check if the users YT account has authorized the service
        """
        authorized = cls.SESSION_NAME_ACCESSTOKEN in flask.session and cls.check_secret_file_exists() and not cls.check_access_token_expired()
        return authorized

    @classmethod
    def get_authorized_client(cls) -> pyyoutube.Client:
        cls.assert_yt_authorized()

        access_token = cls.get_access_token()
        client_secrets = cls.get_client_secret_data()

        client = Client(
            access_token=access_token.access_token,
            refresh_token=access_token.refresh_token,
            client_id=client_secrets["client_id"],
            client_secret=client_secrets["client_secret"]
        )

        return client

    ####################################################################################################
    # Authorization flow functions
    ####################################################################################################
    # auth flow:
    # get auth url -> redirect user to url
    # user autherizes service -> google redirects to service callback URL
    # on callback URL get source url (has info stuff) -> generate acces tokens
    # store access and refresh token (in SESSION or DB or FILE)

    @classmethod
    def _get_default_auth_client(cls, redirect_uri: str = None) -> pyyoutube.Client:
        client_secrets = cls.get_client_secret_data()
        client = Client(
            client_id=client_secrets["client_id"],
            client_secret=client_secrets["client_secret"]
        )

        # TODO set default values
        # override redirect URI
        # client.DEFAULT_REDIRECT_URI = flask.url_for('.oauth2callback', _external=True)
        # default_redirect = "http://localhost:5000/api/v1/yt/oauth2callback"
        default_redirect = "http://localhost:5000/yt/oauth2callback"
        client.DEFAULT_REDIRECT_URI = default_redirect if redirect_uri is None else redirect_uri

        # Scope
        client.DEFAULT_SCOPE = [
            'https://www.googleapis.com/auth/youtube.readonly'
        ]

        client.DEFAULT_STATE = None

        return client

    @classmethod
    def get_authorization_url(cls, redirect_uri: str = None) -> str:
        """
        Returns
            url: Authorize url for user.
        """

        client = cls._get_default_auth_client(redirect_uri=redirect_uri)

        authorize_url, state = client.get_authorize_url(
            # access_type=`online` or `offline`
            access_type="offline"
        )

        flask.session[cls.SESSION_NAME_YT_AUTH_STATE] = state

        print()
        print("DEBUG STATE: ", state)
        print()

        return authorize_url

    @classmethod
    def handle_authorization_response(cls, response_uri: str):
        """

        Parameters
        ----------
        authorization_response
            str: url of where google redirected to after user authorized service

        """

        client = cls._get_default_auth_client()

        state = flask.session[cls.SESSION_NAME_YT_AUTH_STATE]

        access_token: AccessToken = client.generate_access_token(
            authorization_response=response_uri,
            state=state
        )

        cls.save_access_token(access_token=access_token)

    @classmethod
    def revoke_access_token(cls) -> bool:
        if cls.check_yt_authorized():
            client = cls._get_default_auth_client()
            token = cls.get_access_token()

            print()
            print("DEBUG OAuth token: ", token, type(token))
            print("DEBUG OAuth token: ", token.access_token,
                  type(token.access_token))
            print()
            print()

            cls.delete_access_token()

            try:
                status = client.revoke_access_token(token=token.access_token)
            except PyYouTubeException as e:
                print(e)
                status = False

            return status

        raise BadgerYTUserNotAuthorized(
            message="No credentials exist for user to revoke", status_code=404)
