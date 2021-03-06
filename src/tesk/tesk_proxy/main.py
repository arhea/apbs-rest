from os import environ
from logging.config import dictConfig
from flask import Flask
from service.tesk_proxy_service import tesk_proxy
from LOGGING_CONFIG import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)

app = Flask(__name__)
app.register_blueprint(tesk_proxy)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5007'))
    except ValueError:
        PORT = 5007

    app.run(HOST, PORT)