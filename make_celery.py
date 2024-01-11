from badger import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]

flask_app.app_context().push()

# celery -A make_celery worker --loglevel INFO --concurrency 4
# celery -A make_celery worker --loglevel INFO --pool=solo --concurrency 4

# celery -A make_celery worker --loglevel INFO -P threads
