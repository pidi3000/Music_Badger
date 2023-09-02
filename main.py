
APP_VERSION = "0.0.5"


# TODO ?do I need to check before create on each table element?     - don't think so, check are done before song is added at all. So there shouldn't be duplicates
# TODO ?will I use user_id / multi user song data?                  - No for now


# TODO DONE add artist pages
# TODO DONE get song meta data from youtube
# TODO add Publisher pages

# TODO export test song entrys from my music playlist for unittest

if __name__ == '__main__':
    import badger

    # app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
    app = badger.create_app()

    print(app.url_map)

    from badger._data.config import db_path

    print("-"*100)
    print(".\n"*2)
    print("Version: ", APP_VERSION)
    print("")
    print("DB_path: ", db_path)
    print(".\n"*2)
    print("-"*100)

    app.run('localhost', 5000, debug=True)