import os

from sqlalchemy import create_engine

class Config(object):
    SECRET_KEY = "ClaveSecreta"
    SESION_COOKIE_SECURE = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://LAPLANTA:LAPLANTA10s.@127.0.0.1/salon_belleza'
    SQLALCHEMY_TRACK_MODIFICATIONS = False