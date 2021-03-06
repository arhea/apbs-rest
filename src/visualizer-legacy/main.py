import sys, os
from os import environ
from logging.config import dictConfig
from flask import Flask
# from flask_cors import CORS
# from service.oldviz_service import viz_service
from service import oldviz_service

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__, static_url_path='/viz/static')
app.register_blueprint(oldviz_service.viz_service)

def main():
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5008'))
    except ValueError:
        PORT = 5009

    app.run(HOST, PORT)

if __name__ == "__main__":
    main()