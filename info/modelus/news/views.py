from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from sqlalchemy.sql.functions import user

from info.models import News, Comment
from info.modelus.news import news_blu
from info.utils.common import user_login_data



@news_blu.route('/news_collect',methods=['POST'])
@user_login_data
def new_collect():
    '''
    新闻收藏
    1、接收参数
    2、校验参数
    3、查询出该条新闻
    4、往用户收藏那该新闻的列表中添加新闻
    5、返回响应
        :return:
    '''
    user =g.user
    if not user

@news_blu.route('/<int:news_id>')
@user_login_data
def detail(news_id):
    '''
    新闻详情
    :param news_id:  需要查看详情的新闻id
    :return:
           1 、从新闻表中查询浏览量以降序排序只显示六条数据
    '''
    user = g.user
    news_list = News.query.order_by(News.clicks.desc().limit(6)).all()
    news_dict_li = []
    # 将列表对象以for循环的方式遍历出列表
    for news_obj in news_list:
        # 将新闻对象，变成字典
        news_dict_li.append(news_obj.to_dict())
    # 一、查询新闻的信息
    news = None
    try:
        news = News.query.get('news_id')
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    if not news:
        abort(404)

    news.clicks += 1

    # try:
    #       db.session.commit()
    # except Exception as e:
    #   current_app.logger.error(e)
    is_collected = False
    # 什么时候这个is_collected是收藏的？？
    # 该条新闻在用户收藏的新闻列表当中
    if user:
        if news in user.collection_news:
            is_collected = True
    # 二、查询评论
    # TODO:
    commit_list = Comment.query.filter(Comment.news_id == news_id == news_id).order_by(
        Comment.create_time.desc()).all()
    print(commit_list)
    comment_dict_li = [comment.to_dict() for comment in commit_list]

    data = {
        "user_info": user.to_dict() if user else None,
        "news_dict_li":news_dict_li,
        "news":news.to_dict(),
        "is_collected": is_collected,
        "comments": comment_dict_li

    }
    return render_template('news/detail.html',data=data)

