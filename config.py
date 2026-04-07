import os
from pymongo import MongoClient
from sqlalchemy import create_engine

class Config:
    SECRET_KEY = os.urandom(24)
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = 'beauty_glam_salt_123'
    
    PERMANENT_SESSION_LIFETIME = 600 
    SECURITY_TOKEN_MAX_AGE = 600

    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Junior021205$$$@localhost/salon_belleza'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://LAPLANTA:LAPLANTA10s.@localhost/salon_belleza'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/salon_belleza'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Junior021205$$$@localhost/salon_belleza'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://LAPLANTA:LAPLANTA10s.@localhost/salon_belleza'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MONGO_URI = "mongodb://localhost:27017/salon_belleza"
    MONGO_DB_NAME = "salon_belleza"

client = MongoClient(Config.MONGO_URI)
mongo_db = client[Config.MONGO_DB_NAME]
bitacora_mongo = mongo_db['logs_seguridad']

class Config(object):
    SECRET_KEY = "ClaveSecreta"
    SESION_COOKIE_SECURE = False

class DevelopmentConfig(Config):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Junior021205$$$@127.0.0.1/salon_belleza'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://LAPLANTA:LAPLANTA10s.@localhost/salon_belleza'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1/salon_belleza'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Junior021205$$$@127.0.0.1/salon_belleza'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://LAPLANTA:LAPLANTA10s.@localhost/salon_belleza'
    SQLALCHEMY_TRACK_MODIFICATIONS = False