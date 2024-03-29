
from pathlib import Path

from badger_config_handler import Badger_Config_Base, Badger_Config_Section


class Flask_Config(Badger_Config_Section):
    _exclude_vars_ = ["db_schema", "SQLALCHEMY_DATABASE_URI"]

    PORT: int
    DEBUG: bool

    SECRET_KEY: str

    sqlite_db_path: Path
    db_schema: str

    SQLALCHEMY_DATABASE_URI: str
    SQLALCHEMY_TRACK_MODIFICATIONS: bool

    SESSION_TYPE: str

    SSL_ENABLE: bool
    SSL_ENFORCE: bool
    SSL_CERT_PATH: Path
    SSL_KEY_PATH: Path

    def setup(self):
        # self.PORT = 5000
        self.DEBUG = True
        self.SECRET_KEY = 'REPLACE ME - this value is here as a placeholder.'

        self.sqlite_db_path = Path("database.db")
        self.db_schema = 'sqlite:///'
        self.SQLALCHEMY_DATABASE_URI = self.db_schema + \
            str(self.sqlite_db_path)
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        self.SESSION_TYPE = 'filesystem'

        self.SSL_ENABLE = True
        self.SSL_ENFORCE: bool = False
        self.SSL_CERT_PATH: Path = Path("ssl/cert.pem")  # relative to data dir
        self.SSL_KEY_PATH: Path = Path("ssl/key.pem")  # relative to data dir

    def post_process(self):
        # TODO make sure these are safe
        self.SSL_CERT_PATH = self.root_path.joinpath(self.SSL_CERT_PATH)
        self.SSL_KEY_PATH = self.root_path.joinpath(self.SSL_KEY_PATH)

        # make sure relative path is within root_path not outside
        # could be done with something like `../../secrets.json`
        temp_sqlite_db_path = self.root_path.joinpath(self.sqlite_db_path)
        temp = temp_sqlite_db_path.resolve()
        if temp.is_relative_to(self.root_path):
            self.sqlite_db_path = temp_sqlite_db_path
            self.SQLALCHEMY_DATABASE_URI = self.db_schema + \
                str(self.sqlite_db_path)
        else:
            raise ValueError("sqlite_db_path is outside root_path")

    def pre_process(self):

        if self.SSL_CERT_PATH.is_relative_to(self.root_path):
            self.SSL_CERT_PATH = self.SSL_CERT_PATH.relative_to(self.root_path)

        if self.SSL_KEY_PATH.is_relative_to(self.root_path):
            self.SSL_KEY_PATH = self.SSL_KEY_PATH.relative_to(self.root_path)

        if self.sqlite_db_path.is_relative_to(self.root_path):
            self.sqlite_db_path = self.sqlite_db_path.relative_to(
                self.root_path)


class Badger_Config(Badger_Config_Section):

    YT_API_KEY: str
    CLIENT_SECRETS_FILE: Path
    
    ENTRYS_PER_PAGE: int

    def setup(self):
        self.YT_API_KEY = ""
        self.CLIENT_SECRETS_FILE: Path = Path("client_secret_youtube.json")  # relative to data dir
        
        self.ENTRYS_PER_PAGE = 5

    def post_process(self):
        # TODO make sure these are safe
        self.CLIENT_SECRETS_FILE = self.root_path.joinpath(self.CLIENT_SECRETS_FILE)

    def pre_process(self):
        if self.CLIENT_SECRETS_FILE.is_relative_to(self.root_path):
            self.CLIENT_SECRETS_FILE = self.CLIENT_SECRETS_FILE.relative_to(self.root_path)


class Celery_Config(Badger_Config_Section):

    broker_url: str
    result_backend: Path
    
    task_ignore_result: bool

    def setup(self):
        self.broker_url = "redis://localhost"
        self.result_backend = "redis://localhost"
        
        self.task_ignore_result = False

    def post_process(self):
        pass

    def pre_process(self):
        pass

class Config(Badger_Config_Base):
    _exclude_vars_ = ["project_root", "data_dir", "config_file_path"]

    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root.joinpath("data").absolute()
    config_file_path = data_dir.joinpath("config.json")

    flask: Flask_Config
    badger: Badger_Config
    celery: Celery_Config

    def __init__(self) -> None:
        self.flask = Flask_Config(section_name="flask")
        self.badger = Badger_Config(section_name="badger")
        self.celery = Celery_Config(section_name="celery")

        super().__init__(
            config_file_path=self.config_file_path,
            root_path=self.data_dir
        )
