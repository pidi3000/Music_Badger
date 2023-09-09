

import json
import os

import flask
from flask import current_app

import pyyoutube
from pyyoutube import Client, AccessToken


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
        return AccessToken.from_json(flask.session[cls.SESSION_NAME_ACCESSTOKEN])

    @classmethod
    def save_access_token(cls, access_token: AccessToken):
        flask.session[cls.SESSION_NAME_ACCESSTOKEN] = access_token.to_json()

    ####################################################################################################
    # Authorization functions
    ####################################################################################################

    @classmethod
    def check_yt_authorized(cls) -> bool:
        """
        Check if the users YT account has authorized the service
        """
        authorized = cls.SESSION_NAME_ACCESSTOKEN in flask.session and cls.check_secret_file_exists()
        return authorized

    @classmethod
    def get_authorized_client(cls) -> pyyoutube.Client:
        if not cls.check_yt_authorized():
            raise PermissionError("User must authorize service")

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
    def _get_default_auth_client(cls) -> pyyoutube.Client:
        client_secrets = cls.get_client_secret_data()
        client = Client(
            client_id=client_secrets["client_id"],
            client_secret=client_secrets["client_secret"]
        )

        # TODO set default values
        # override redirect URI
        # client.DEFAULT_REDIRECT_URI = flask.url_for('.oauth2callback', _external=True)

        # Scope
        # client.DEFAULT_SCOPE  = flask.url_for('.oauth2callback', _external=True)

        return client

    @classmethod
    def get_authorization_url(cls) -> str:
        """
        Returns
            url: Authorize url for user.
        """

        client = cls._get_default_auth_client()

        authorize_url, state = client.get_authorize_url(
            # access_type=`online` or `offline`
        )

        flask.session[cls.SESSION_NAME_YT_AUTH_STATE] = state

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

        access_token: AccessToken = client.generate_access_token(
            authorization_response=response_uri, scope=flask.session[cls.SESSION_NAME_YT_AUTH_STATE])

        cls.save_access_token(access_token=access_token)

    @classmethod
    def revoke_access_token(cls):
        # TODO IMPLEMENT token revoke
        raise NotImplementedError("soonTM")
