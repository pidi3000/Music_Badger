from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from badger.db_models import Artist

import re
import json

from badger.error import BadgerYTUserNotAuthorized

YT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class YouTube_Data_Handler:
    yt_id: str = None
    yt_data_raw: dict = None

    def __init__(self, yt_id: str) -> None:
        self.yt_id = yt_id
        self._load_yt_video_data_raw()

    def _load_yt_video_data_raw(self) -> dict:
        from badger.db_models import Song_Meta_Data
        meta_data = Song_Meta_Data.get_by_ytID(self.yt_id)

        print()
        print("DEBUG YT DATA: ", "Loading raw yt data")

        if meta_data is not None:
            print("DEBUG YT DATA: ", "loading from DB")
            self.yt_data_raw = json.loads(meta_data.yt_data_raw)
            # return

        print("DEBUG YT DATA: ", "loading from YT")
        from badger.web_youtube.routes import get_authorized_yt_obj
        youtube = get_authorized_yt_obj()

        # https://developers.google.com/youtube/v3/docs/videos#resource-representation
        request = youtube.videos().list(
            part="snippet,contentDetails,status,statistics",
            id=self.yt_id
        )
        response = request.execute()

        # print("-"*20)
        # print(response)
        # print("-"*20)

        # TODO catch problems
        # API errors -> quota exceeded
        # invalid yt ID given -> items is empty

        with open("temp/yt_data_raw.json", "w") as f:
            json.dump(response, f, indent=4)

        try:
            response["items"][0]["snippet"]["title"]
            response["items"][0]["snippet"]["description"]
        except IndexError:
            print(response)

            raise

        self.yt_data_raw = response

    ####################################################################################################
    # YT Video data
    ####################################################################################################

    def get_video_title(self) -> str:
        return self.yt_data_raw["items"][0]["snippet"]["title"].strip()

    def get_video_description(self) -> str:
        return self.yt_data_raw["items"][0]["snippet"]["description"]

    def get_video_published_date(self) -> str:
        from datetime import datetime
        date_string = self.yt_data_raw["items"][0]["snippet"]["publishedAt"]
        return datetime.strptime(date_string, YT_DATE_FORMAT)

    def get_video_thumbnail_url(self) -> str:
        return self.yt_data_raw["items"][0]["snippet"]["thumbnails"]["medium"]["url"]

    ####################################################################################################
    # YT Channel data
    ####################################################################################################

    def get_channel_Id(self) -> str:
        return self.yt_data_raw["items"][0]["snippet"]["channelId"]

    def get_channel_Title(self) -> str:
        return self.yt_data_raw["items"][0]["snippet"]["channelTitle"].strip()

    ####################################################################################################
    # Song data
    ####################################################################################################
    def _get_artist_part_from_title(self):
        parts = self.get_video_title().split("-")
        if len(parts) > 1:
            return parts[0]
        return None

    def get_song_title(self, user_song_title: str | None = None) -> str:
        # user_song_title has valid data
        if not (
            user_song_title is None or
            len(user_song_title) == 0 or
            user_song_title.isspace()
        ):
            return user_song_title

        parts = self.get_video_title().split("-", 1)

        if len(parts) >= 2:
            temp = parts[1]
        else:
            temp = parts[0]

        temp = temp.replace(self.get_song_extras(), "")

        return temp.strip() if temp else ""

    def get_song_extras(self, user_extras: str | None = None) -> str:
        # user_extras has valid data
        if not (
            user_extras is None or
            len(user_extras) == 0 or
            user_extras.isspace()
        ):
            return user_extras

        BRACKETS_OPEN = ['(', '[', '{']
        BRACKETS_CLOSE = [')', ']', '}']

        def lfind_bracket(s: str):
            idx = -1
            for bracket in BRACKETS_OPEN:
                x = s.find(bracket)
                idx = x if idx == -1 or (x < idx and x != -1) else idx
                # idx = min(x, idx) if x != -1 else idx
            return idx

        def rfind_bracket(s: str):
            idx = -1
            for bracket in BRACKETS_CLOSE:
                x = s.rfind(bracket)
                # idx = x if x > idx else idx
                idx = max(x, idx) if x != -1 else idx
            return idx

        temp = self.get_video_title()
        idx_l = lfind_bracket(temp)
        idx_r = rfind_bracket(temp)
        if min(idx_l, idx_r) < 0:
            temp = None
        else:
            temp = temp[idx_l:idx_r+1]
        return temp.strip() if temp else ""

    def get_song_artist_names(self) -> list[str]:
        artists = self._get_artist_part_from_title()

        if artists is None:
            artists = [self.get_channel_Title()]
        else:
            artists = re.split(" x |,|&", artists)

        return artists

    def get_song_artists(self, user_artist_data: Artist | list[Artist] = None) -> list[Artist]:
        if user_artist_data is not None and (isinstance(user_artist_data, list) and len(user_artist_data) > 0):
            return user_artist_data

        from badger.db_models import Artist
        artist_list = []
        artists = self.get_song_artist_names()

        for artist_name in artists:
            artist_list.append(Artist.get_or_create(artist_name))

        return artist_list
