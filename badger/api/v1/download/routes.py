
from celery.result import AsyncResult
from flask import request

from . import blueprint as api_pages

from badger.error import BadgerMisingParameter
from badger.data_handler.api_response_handler import badger_Response
from badger.data_handler.user_input_handler import User_Input_Handler
from badger.data_handler.song_handler import Song
from badger.data_handler.download_handler import Download_Handler


####################################################################################################
# Handle download routes
####################################################################################################

# ! TODO REMOVE just testing
@api_pages.route('/download/result', methods=["GET"])
@badger_Response
def get_download_result():
    task_id = request.values.get("task_id", None, type=str)
    
    result = AsyncResult(task_id)
    # result.state
    ready = result.ready()
    response = {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "result": result.result,
        "value": result.get() if ready else result.result,
        "state": result.state,
        "info": result.info,
    }

    print(response)

    return response

@api_pages.route('/downloads', methods=["GET"])
@badger_Response
def get_downloads():
    response = None

    response = Download_Handler.get_status_all()

    return response


@api_pages.route('/download', methods=["GET"])
@badger_Response
def get_download():
    response = None

    song_id = request.values.get("song_id", None, type=int)

    if song_id is None or not isinstance(song_id, int):
        raise BadgerMisingParameter(
            f"Invalid or missing parameter: '{song_id=}'")

    response = Download_Handler.get_status(song_id=song_id)

    return response


@api_pages.route('/download/start', methods=["post"])
@badger_Response
def start_download():
    response = None
    status_code = 201
    page_info = None

    song_id = request.values.get("song_id", None, type=int)

    if song_id is None or not isinstance(song_id, int):
        raise BadgerMisingParameter(
            f"Invalid or missing parameter: '{song_id=}'")

    response = Download_Handler.start_download(song=song_id)

    return response, status_code
