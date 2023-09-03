# import os

# basedir = os.path.abspath(os.path.dirname(__file__))
# db_path = os.path.join(basedir, 'database.db')
import os
from pathlib import Path

data_dir = Path(__file__).parent.absolute()

# TODO make this json or something
class Config:
    # basedir = Path(__file__).parent.parent.parent.absolute()
    db_path = str(data_dir.joinpath("database.db").absolute())

    # SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = 'REPLACE ME - this value is here as a placeholder.'

    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + db_path

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    # MUSIC_BADGER = MUSIC_BADGER_CONFIG()
    MUSIC_BADGER = {
        "data_dir": str(data_dir),
        "DEFAULT_DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",

        # file that contains the OAuth 2.0 information, including its client_id and client_secret.
        "CLIENT_SECRETS_FILE": str(data_dir.joinpath("client_secret_youtube.json").absolute()),
    }
