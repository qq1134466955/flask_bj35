from flask import render_template, redirect, current_app, session, request, jsonify

from info.models import User, News, Category
# from info.modules.index import index_blu
from info.modelus.index import index_blu
from info.utils.response_code import RET


@index_blu.route("/news_list")
def get_news_list():
    """
    0、获取数据
    0.1 校验数据
    1、查询出所有新闻 (查询对应分类的新闻)
    2、排序 按照创建时间
    3、分页
    :return:
    """
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
        print(cid)
        print(page)
        print(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 1、查询出所有新闻
    # 2、排序 按照创建时间
    # 3、分页
    # *args  ()   []
    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)
    paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)

    # 对象列表
    news_list = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    # 转化成字典列表
    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_dict())

    data = {
        "news_dict_li": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }
    # js去控制html
    return jsonify(errno=RET.OK, errmsg="OK", data=data)


@index_blu.route("/")
def index():
    """
    一、显示用户登录状态
    核心逻辑：查询出来用户信息，然后通过模板进行渲染
    :return:
    """
    user_id = session.get("user_id")

    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 二、新闻点击排行功能实现
    # 1、查询出来所有的新闻数据
    # 2、进行排序？？？按点击量排序
    # 3、取出前六条新闻
    # 4、渲染
    news_list = News.query.order_by(News.clicks.desc()).limit(6).all()  # [obj, obj, obj]

    # 5、将对象列表转化为字典列表
    news_dict_li = []
    for news_obj in news_list:
        # 将新闻对象，变成字典
        news_dict_li.append(news_obj.to_basic_dict())

    # 三、查询分类
    categorys = Category.query.all()   # [obj, obj, obj]

    category_dict_li = []
    for category in categorys:
        category_dict_li.append(category.to_dict())

    # 列表推导式
    # category_dict_li = [category.to_dict() for category in categorys]

    data = {
        # 这是一个三元表达式
        "user_info": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "category_dict_li": category_dict_li
    }

    return render_template("news/index.html", data=data)


# 请求从哪里来？？？？
# 浏览器自动给我们发过来的：/favicon.ico
@index_blu.route("/favicon.ico")
def favicon():
    """
    # 返回我们的favicon.ico
    # redirect("/static/news/favicon.ico")实现
    :return:
    """
    return current_app.send_static_file("news/favicon.ico")