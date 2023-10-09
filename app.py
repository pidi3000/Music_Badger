
APP_VERSION = "0.1.0"


# TODO ?do I need to check before create on each table element?     - don't think so, check are done before song is added at all. So there shouldn't be duplicates
# TODO ?will I use user_id / multi user song data?                  - No for now


# TODO add Publisher pages
# TODO export test song entrys from my music playlist for unittest


def _print_part(part, indent_level=1, indent=4, padding_length: int = 35, skip_indexes: list = None):
    from werkzeug.routing import Rule

    PRINT_TYPE = False

    count = 0
    if skip_indexes is None:
        skip_indexes = []

    skip_indexes = list(skip_indexes)  # create copy

    max_len = 0
    for key in part:
        count += 1
        key_len = 0

        is_last = False

        if count == len(part):
            is_last = True

        padding = " "*indent * (indent_level-1)
        padding += "└" if is_last else "│"
        padding += ("─"*(indent-1))

        ind = 0
        for i in range(len(padding)-indent):
            ind = i
            if i % indent == 0 and i not in skip_indexes:
                # padding[i] = "|"
                padding = padding[:i] + "│" + padding[i + 1:]
                pass

        if is_last:
            skip_indexes.append(len(padding)-indent)

        # padding += f" {ind}-{len(padding)}-{len(padding)-indent} "

        data = part[key]

        type_str = '' + str(type(data))
        type_str = f"{type_str}{' ' * max(padding_length - len(type_str), 0)} - " if PRINT_TYPE else ''

        key_str = '' + str(key)

        if len(key_str.strip()) < 1:
            key_str = "index"

        key_str = f"{key_str}{' ' * max(padding_length - len(key_str), 0)}"

        if isinstance(data, dict):
            print(f"{padding}{type_str}{key_str}")
            # print(f"{padding} {type(data)} - {key}: ")
            # print(padding, type(data), " - ", key, ": ")
            key_len = _print_part(
                part=data,
                indent_level=indent_level+1,
                indent=indent,
                padding_length=padding_length,
                skip_indexes=skip_indexes
            )

        elif isinstance(data, Rule):
            print(f"{padding}{data.endpoint} - {data.methods} ")

        else:
            print(f"{padding}{type_str}{key_str} -> {data}")
            key_len = len(key)
            # print(padding, type(data), " - ", key, ": ", data)

        max_len = key_len if key_len > max_len else max_len

    return max_len


def _add_rule_to_tree(tree, url_parts, rule_object):
    # print(tree, url_parts, rule_object)
    if not url_parts:
        return

    current_part = url_parts.pop(0)

    if current_part not in tree:
        tree[current_part] = {}

    if not url_parts:
        tree[current_part]['rule_object'] = rule_object
        # tree[current_part] = rule_object
        return

    _add_rule_to_tree(tree[current_part], url_parts, rule_object)


####################################################################################################
def create_app():
    import badger
    app = badger.create_app()

    return app


def run_app():
    app = create_app()

    from pathlib import Path

    print()

    url_rules = app.url_map
    url_tree = {}

    count = 0
    for rule_obj in url_rules.iter_rules():
        if count > 100:
            break
        count += 1
        url_parts = rule_obj.rule.split("/")
        _add_rule_to_tree(url_tree, url_parts[1:], rule_obj)

    print()
    _print_part(url_tree, indent=4, padding_length=10)

    print("-"*100)
    print(".\n"*2)
    print("Version: ", APP_VERSION)
    print("")
    print("DB_path: ", app.config["SQLALCHEMY_DATABASE_URI"])
    print(".\n"*2)
    print("-"*100)

    print("CONFIG: ")
    print("key_len: ", _print_part(app.config))
    # print(json.dumps(app.config, indent=2))
    print(".\n"*2)
    print("-"*100)

    print("SSL")
    print()

    cert_path = Path(app.config["SSL_CERT_PATH"]).absolute()
    key_path = Path(app.config["SSL_KEY_PATH"]).absolute()

    print("SSL_ENABLE:\t", app.config["SSL_ENABLE"])
    print("SSL_ENFORCE:\t", app.config["SSL_ENFORCE"])
    print("SSL_CERT_PATH:\t", cert_path, "\t", cert_path.exists())
    print("SSL_KEY_PATH:\t", key_path, "\t", key_path.exists())

    print()
    context = None
    if app.config["SSL_ENABLE"]:
        # check ssl key and cert file exist

        if cert_path.exists() and key_path.exists():
            context = (str(cert_path), str(key_path))
        else:
            print(
                f"ERROR: SSL files not found. Key: {key_path.exists()}, Cert: {cert_path.exists()}")
            if app.config["SSL_ENFORCE"]:
                raise FileNotFoundError(
                    f"SSL files not found. Key: {key_path.exists()}, Cert: {cert_path.exists()}")

    print(context)
    if context is None:
        print("WARNING: running without ssl enabled")

    print("-"*100)
    print()

    # app.run('localhost', 5000, debug=True)
    app.run(host="0.0.0.0", port=5100, ssl_context=context)


if __name__ == '__main__':
    run_app()
