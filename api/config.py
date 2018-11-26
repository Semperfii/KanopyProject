import os
from api.core import get_pg_url

class Config:
    SECRET_KEY = "testkey"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_FILE = "api.log"

class DockerDevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://testusr:password@postgres/testdb"
    DEBUG = True


config = {"docker": DockerDevConfig}