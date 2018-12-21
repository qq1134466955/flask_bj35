
# 配置类
import logging
from logging.handlers import RotatingFileHandler
# from urllib import response

from flask import Flask
from flask import make_response
from flask.ext.wtf import CSRFProtect
from flask.ext.wtf.csrf import generate_csrf
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
# def create_app(config_name):
#     app = Flask(__name__)
#     app.config.from_object(config[config_name])
#     # 集成flask_sqlalchemy SQLAlchemy
#     db.init_app(app)
#     global redis_store
#     # 集成redis StrictRedis
#     redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT, decode_responses=True)
#     # CSRFProtect只帮我们做校验工作
#     # 往表单添加一个隐藏字段csrf_tocken()并且往cookie中添加csrf_tocken
#     # 用到时ajax请求，我们可以往请求头中去设置一个X-CSRFToken
#     CSRFProtect(app)
#
#     @app.after_request
#     def set_cookie(response):
#         # 当我们使用CSRFProtect进行保护的时候，那么这个csrf_tocken只必须用CSRFProtect提供的
#         csrf_tocken = generate_csrf()
#         response.set_cookie('csrf_tocken',csrf_tocken)
#         return response
#
#      # 五、 集成flask-session
#     # 1、由于session默认制定session的储存是null,所以我们需要通过SESSION_TYPE = ‘redis’来制定session的储存位置
#     Session(app)
#     # 注册蓝图
#     # from info.modelus.index import index_blu
#     # app.register_blueprint(index_blu)
#     #
#     # from info.modelus.passport import passport_blu
#     # app.register_blueprint(passport_blu)
#     # from info.modules.index import index_blu
#     from info.modelus.index import index_blu
#     app.register_blueprint(index_blu)
#
#     # from info.modules.passport import passport_blu
#     from info.modelus.passport import passport_blu
#     app.register_blueprint(passport_blu)
#     # 数据库迁移
#     from info.utils.common import do_index_class
#     app.add_template_filter(do_index_class,'indexClass')
#
#     return app

def create_app(config_name):
    # 在创建app前去调用set_log
    set_log(config_name)
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    # # 二、集成flask-sqlalchemy
    # db = SQLAlchemy(app)
    db.init_app(app)

    # 三、集成redis
    # 如果我连接的是unbuntu的ip
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT, decode_responses=True)
    # 四、集成CSRFProtect
    # 他只起到保护作用，具体的往表单中设置csrf_token和往cookie中设置csrf_token需要我们自己来做
    # 只针对post，put，delete请求进行保护  get本身就不需要包旭

    # 1、CSRFProtect只帮我们做校验工作
    # 2、往表单中添加一个隐藏字段csrf_token()并且往cookie中去添加csrf_token
    # 3、用到时ajax请求，我们可以往请求头中去设置一个X-CSRFToken
    CSRFProtect(app)

    # 设置csrf_token的cookie
    @app.after_request
    def set_cookie_csrf(response):
        # 当我们使用CSRFProtect进行保护的时候，那么这个csrf_token值必须用CSRFProtect提供的
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token", csrf_token)
        return response

    # 五、集成flask-session
    # 1、由于Session默认指定session的存储方式是null，所以我们需要通过SESSION_TYPE = "redis"来指定session存储位置
    Session(app)

    # 注册蓝图
    # 当我们去调用蓝图对象的时候，什么时候用什么时候导入
    # from info.modules.index import index_blu
    from info.modelus.index import index_blu
    app.register_blueprint(index_blu)

    # from info.modules.passport import passport_blu
    from info.modelus.passport import passport_blu
    app.register_blueprint(passport_blu)

    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class, "indexClass")

    return app