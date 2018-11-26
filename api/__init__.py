import os
import logging

from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy_utils import create_database, database_exists

# why we use application factories http://flask.pocoo.org/docs/1.0/patterns/appfactories/#app-factories
def create_app(test_config=None):
    """
    The flask application factory. To run the app somewhere else you can:
    ```
    from api import create_app
    app = create_app()
    if __main__ == "__name__":
        app.run()
    """
    app = Flask(__name__)

    CORS(app)  # add CORS

    # decide whether to create database
    db_url = app.config["SQLALCHEMY_DATABASE_URI"]
    if not database_exists(db_url):
        create_database(db_url)

    # register sqlalchemy to this app
    from api.models import db

    db.init_app(app)  # initialize Flask SQLALchemy with this flask app
    Migrate(app, db)

    return app