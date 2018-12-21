import random
import re

from flask import request, abort, current_app, make_response, json, jsonify, session
from info import constants, db
from info import redis_store
from info.models import User
# from info.modules.passport import passport_blu
from info.modelus.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from info.libs.yuntongxun.sms import CCP
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@passport_blu.route("/logout")
def logout():
    """
    退出登录
    核心逻辑：清除session
    :return:
    """
    session.pop("user_id", None)
    session.pop("nick_name", None)
    session.pop("mobile", None)

    return jsonify(errno=RET.OK, errmsg="退出成功")


@passport_blu.route("/login", methods=["POST"])
def login():
    """
    登录逻辑
    1、接收参数 mobile passport
    2、校验参数的完整性
    3、校验手机号的格式
    4、去数据库通过手机号查询该用户是否存在
    5、如果存在，和数据库中的密码进行比对
    6、如果相等，返回响应
    :return:
    """
    # 1、接收参数 mobile passport
    params_dict = request.json
    mobile = params_dict.get("mobile")
    passport = params_dict.get("passport")

    # 2、校验参数的完整性
    if not all([mobile, passport]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 3、校验手机号的格式
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 4、去数据库通过手机号查询该用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    # 5、判断user是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户未注册")

    # 6、比较
    # if not check_password_hash(user.password_hash, passport):
    if not user.check_password(passport):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    # 7、设置用户最后一次登录的时间
    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    # 8、记录用户的状态
    session["user_id"] = user.id
    session["mobile"] = mobile
    session["nick_name"] = user.nick_name

    return jsonify(errno=RET.OK, errmsg="登录成功")


@passport_blu.route("/register", methods=["POST"])
def register():
    """
    注册功能
    1、接收参数 mobile smscode password
    2、校验参数的完整性
    3、校验手机号是否正确
    4、比对数据库中的短信验证码和用户输入的验证码是否一致
    5、保存用户信息到mysql数据库
    6、保持登录状态  session
    7、返回响应
    :return:
    """
    # 1、接收参数 mobile smscode password
    params_dict = request.json
    mobile = params_dict.get("mobile")
    smscode = params_dict.get("smscode")
    password = params_dict.get("password")

    # 2、校验参数的完整性
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 3、校验手机号是否正确
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 4、取到redis的手机验证码
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已经过期")

    # 5、和用户输入的手机验证码进行比较
    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 6、保存用户信息
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 将用户输入的密码进行hash加密
    # user.password_hash = generate_password_hash(password)
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    # 7、保持登录的状态
    session["user_id"] = user.id
    session["mobile"] = mobile
    session["nick_name"] = user.nick_name

    # 8、返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():
    """
    获取短信验证码
    1、接收参数 mobile image_code image_code_id
    2、校验参数的完整性
    3、校验手机号是否正确
    4、比对数据库中的图片验证码和用户输入的验证码是否一致
    5、生成短信验证码
    6、发送短信验证码
    7、保存短信验证码到redis数据库中
    8、返回响应
    :return:
    """
    # 1、接收参数 mobile image_code image_code_id
    # params_dict = json.loads(request.data)
    # 接收json数据，返回字典类型
    params_dict = request.json
    mobile = params_dict.get("mobile")
    image_code = params_dict.get("image_code")
    image_code_id = params_dict.get("image_code_id")

    # 2、校验参数的完整性
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 3、校验手机号是否正确
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式输入错误")

    # 4、先从数据库中获取图片验证码
    try:
        real_image_code = redis_store.get("ImageCode_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    # 5、判断取出来的code是否有值
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")

    # 6、和用户输入的去比较
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 7、生成短信验证码
    # 比如说我随机出来的是0000006
    sms_code = "%06d" % random.randint(0, 999999)
    current_app.logger.info("手机验证码是：%s" % sms_code)
    # 8、发送手机验证码
    # '18511551140', ['1234', 5], 1
    # result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="第三方发送短息出错")

    # 9、保存短信验证码到redis数据库中
    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="发送短信验证码成功")


@passport_blu.route("/image_code")
def get_image_code():
    """
    生成图片验证码
    1、接收uuid
    2、校验uuid是否存在
    3、生成验证码
    4、文本验证码保存到redis数据库中
    5、返回图片验证码
    :return:
    """
    # 1、接收uuid
    image_code = request.args.get("imageCodeId")

    # 2、校验uuid是否存在
    if not image_code:
        return abort(404)

    # 3、生成验证码
    _, text, image = captcha.generate_captcha()
    print(text)

    # 4、文本验证码保存到redis数据库中
    try:
        redis_store.setex("ImageCode_" + image_code, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return abort(500)

    # 5、修改返回的contentType
    response = make_response(image)
    response.headers["Content-Type"] = "image/png"

    # 6、返回图片验证码
    return response


