
APP_VERSION = "0.1.0"


# TODO ?do I need to check before create on each table element?     - don't think so, check are done before song is added at all. So there shouldn't be duplicates
# TODO ?will I use user_id / multi user song data?                  - No for now


# TODO add Publisher pages
# TODO export test song entrys from my music playlist for unittest

def create_app():
    import badger

    from data.config import Config
    config = Config()

    # app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
    app = badger.create_app(config=config)

    return app


if __name__ == '__main__':
    app = create_app()

    import json
    from pprint import pprint

    print(app.url_map)

    print("-"*100)
    print(".\n"*2)
    print("Version: ", APP_VERSION)
    print("")
    print("MUSIC_BADGER: ", app.config["MUSIC_BADGER"])
    print("DB_path: ", app.config["SQLALCHEMY_DATABASE_URI"])
    print(".\n"*2)
    print("-"*100)

    def print_part(part, indent_level=1, indent=4):
        PRINT_TYPE = False

        max_len = 0
        for key in part:
            padding = " "*indent * indent_level
            data = part[key]

            type_str = '' + str(type(data))
            type_str = f"{type_str}{' ' * max(30 - len(type_str), 0)} - " if PRINT_TYPE else ''
            
            key_str = '' + str(key)
            key_str = f"{key_str}{' ' * max(30 - len(key_str), 0)} - "

            if isinstance(data, dict):
                print(f"{padding}{type_str}{key_str} ->")
                # print(f"{padding} {type(data)} - {key}: ")
                # print(padding, type(data), " - ", key, ": ")
                key_len = print_part(
                    part=data,
                    indent_level=indent_level+1,
                    indent=indent
                )

            else:
                print(f"{padding}{type_str}{key_str} -> {data}")
                key_len = len(key)
                # print(padding, type(data), " - ", key, ": ", data)

            max_len = key_len if key_len > max_len else max_len

        return max_len

    print(pprint(app.config))
    print("CONFIG: ")
    print("key_len: ", print_part(app.config))
    # print(json.dumps(app.config, indent=2))
    print(".\n"*2)
    print("-"*100)

    app.run('localhost', 5000, debug=True)
