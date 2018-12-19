
# 配置类
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.ext.wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from config import config



def set_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL) # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

db = SQLAlchemy()
redis_store = None # type: StrictRedis
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # 集成flask_sqlalchemy SQLAlchemy
    db.init_app(app)
    global redis_store
    # 集成redis StrictRedis
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT, decode_responses=True)
    # CSRF 保护    需要自己手动设置form表单csrf_tokch 和sessioncsrf_tokch
  #  CSRFProtect(app)
    # 这个Session是储存位置 需要手动设置
    Session(app)
    # 注册蓝图
    from info.modelus.index import index_blu
    app.register_blueprint(index_blu)
    from info.modelus.passport import passport_blu
    app.register_blueprint(passport_blu)
    # 数据库迁移
    return app