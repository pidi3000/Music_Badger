
import flask

from celery import Task, shared_task
from celery.result import AsyncResult

import yt_dlp as youtube_dl

from badger.data_handler.song_handler import Song
from badger.db_models._files import Download_Queue

from datetime import datetime
import time


class Download_Handler():

    @classmethod
    def start_download(cls, song: int | Song):
        print("DEBUG CELERY: start download", song)

        if isinstance(song, int):
            song = Song.get(id=song)

        if not isinstance(song, Song):
            raise ValueError("Not song given")  # TODO better message

        yt_id = song.meta_data.yt_id
        task: AsyncResult = _download_task.delay(
            yt_id=yt_id, song_id=song.id)

        print("DEBUG CELERY: new task ID", task.id)

        # download_queue.append(task.id)
        Download_Queue.create(song_id=song.id, task_id=task.id)

        return task.id

    @classmethod
    def pause_download(cls, yt_id):
        raise NotImplementedError()

    @classmethod
    def cancle_download(cls, yt_id):
        raise NotImplementedError()

    @classmethod
    def get_status(cls, song_id):
        # TODO make real

        status_obj = {
            "id": "asdasduiah",
            "song_id": song_id,
            "status": "pending",
            "progress": 0,
            "date_queued": datetime.now(),
            "date_started": None,
            "date_finished": None,
        }

        return status_obj

    @classmethod
    def get_status_all(cls):
        # TODO make real

        status_list = []
        for i in range(0, 5):
            status_obj = {
                "id": "asdasduiah",
                "song_id": i,
                "status": "pending",
                "progress": i*10,
                "date_queued": datetime.now(),
                "date_started": None,
                "date_finished": None,
            }

            status_list.append(status_obj)

        return status_list


@shared_task(bind=True, ignore_result=False)
def _download_task(self: Task, yt_id, song_id):
    def write_log_msg(msg):
        # print(msg)
        with open("E:/My-Data/Projects_HDD/Music_Badger/data/temp.log", "a") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} - {msg}\n")

    # with self.app.context:
    # update file status
    from badger import badger_app
    with badger_app.app_context():
        print(f"DEBUG DOWNLOAD: start \n{'#'*20}")
        db_task = Download_Queue.get(song_id=song_id)

    # write_log_msg(f"DEBUG CELERY: db_task: {str(db_task)}")
    if db_task is None:
        write_log_msg(f"ERROR task not found: {yt_id=}, {song_id=}")
        raise LookupError(f"ERROR task not found: {yt_id=}, {song_id=}")

    # self.update_state(state="downloading", meta={"foo": "bar"})
    # write_log_msg(f"DEBUG CELERY: state: running")

    # ! wrap all stuff in try catch block,
    # ! so that errors can be written to logger
    # + download queue is not left with garbage

    print(f"DEBUG DOWNLOAD: running...")
    _download_song(self, yt_id)

    # self.update_state(state="done", meta={})
    write_log_msg(f"DEBUG CELERY: state: done")

    # when done
    # ? copy files to permarnent storage

    # ? set files paths in DB
    # update files status in DB

    # remove from queue
    # if isinstance(task, Download_Queue):
    with badger_app.app_context():
        db_task.delete()

    print(f"DEBUG DOWNLOAD: done \n{'#'*20}")

    return  # ! on error return errors, or something like that


def _download_song(task: Task, yt_id):
    errors = []

    class _MyLogger(object):  # ! Better logging using logger lib
        def debug(self, msg):
            # print("DEBUG: ", msg)
            pass

        def warning(self, msg):
            print("WARNING: ", msg)

        def error(self, msg):
            print("ERROR: ", msg)

    def _progress_hook(d):
        # Task state data:
        # * 'state' -> ["downloading", "post_processing", "error", "finished"]

        task_state = ""
        task_meta = {}

        if d['status'] == 'finished':
            # * d['status'] is finnished when download done,
            # * but post processing is still going
            print('Done downloading, now converting ...')
            task_state = 'post_processing'

        if d['status'] == 'error':
            task_state = 'error'
            task_meta = d
            errors.append(d)

        if d['status'] == 'downloading':
            # done = d["downloaded_bytes"]
            # total = d["total_bytes"]
            # progress = "{:.1f}%".format(done/total * 100)
            progress = d["_percent_str"]

            task_state = 'downloading'
            task_meta = {
                "progress": progress,
                "eta": d.get("eta", -1),
                "speed": d["_speed_str"]
            }

        task.update_state(state=task_state, meta=task_meta)

    ydl_opts = {
        'outtmpl': 'data/downloads/%(id)s.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                # 'preferredquality': '320',
            },
            {
                'key': "EmbedThumbnail"
            }
        ],
        # 'writethumbnail': True,
        'logger': _MyLogger(),
        'progress_hooks': [_progress_hook],
    }

    ydl = youtube_dl.YoutubeDL(ydl_opts)
    with ydl:
        # ydl.download(['https://www.youtube.com/watch?v=KOUS0kTw0ew'])
        ydl.download([yt_id])
    # time.sleep(10)

    if len(errors) < 1:
        task.update_state(state="finished", meta={})
        return None

    task.update_state(state="error", meta={"errors:": errors})
    return errors
