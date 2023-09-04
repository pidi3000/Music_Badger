
APP_VERSION = "0.1.0"


# TODO ?do I need to check before create on each table element?     - don't think so, check are done before song is added at all. So there shouldn't be duplicates
# TODO ?will I use user_id / multi user song data?                  - No for now


# TODO add Publisher pages
# TODO export test song entrys from my music playlist for unittest


if __name__ == '__main__':
    import badger

    from data.config import Config
    config = Config()

    # app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
    app = badger.create_app(config=config)

    print(app.url_map)

    print("-"*100)
    print(".\n"*2)
    print("Version: ", APP_VERSION)
    print("")
    print("MUSIC_BADGER: ", app.config["MUSIC_BADGER"])
    print("DB_path: ", app.config["SQLALCHEMY_DATABASE_URI"])
    print(".\n"*2)
    print("-"*100)

    app.run('localhost', 5000, debug=True)
