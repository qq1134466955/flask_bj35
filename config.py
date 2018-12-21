import logging
from redis import StrictRedis


class Config(object):

    SECRET_KEY = "VJqxvU1Sih5OcaX+3TVuLXYfW/s+ESJj6v3CPoaS/B4RuQ/nd4cHw2zAgkU3ii77uooWs9a+Nqar7BpKTFQW1w=="

    # 链接数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/flask_bj35'
    # 数据库设置是否追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 默认为空 需要手动设置 session-type = redis
    SESSION_TYPE = 'redis'
    # 设置session——redis 链接
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置加密
    SESSION_USE_SIGNER = True
    # 如果为TRUE的话 ，浏览器关闭他也会消失
    SESSION_PERMANENT = False
    # 设置存活时间
    PERMANENT_SESSION_LIFETIM = 86400 * 2
    # TODO:
    # 如果为True，当我们对一个已经查询出来的对象进行修改操作的话,不需要去使用db.session.conmmit
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

class Development_Config(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

class Production_Config(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING

class Testing_Config(Config):
    DEBUG = True

config = {
    'development':Development_Config,
    'production':Production_Config,
    'testing' : Testing_Config
}