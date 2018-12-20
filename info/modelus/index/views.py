from flask import current_app
from flask import render_template
from flask import session

from info.models import User
from info.modelus.index import index_blu
@index_blu.route('/')
def index():
    '''
    一、显示用户登录状态
    核心逻辑：查询出来用户信息，然后通过模板进行渲染

    :return:
    '''
    user_id = session.get('user_id')

    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    data = {
        # 三元表达式
        "user_info":  user.to_dict() if user else None
    }




    return render_template('news/index.html',data=data)

# 请求从哪里来？？
# 浏览器自动给我们发过来的： favicon.ico
@index_blu.route('/favicon.ico')
def favicon():
    '''
    # 返回我们的favicon.ico
    # redirect('/static/news/favicon.ico')实现
    :return:
    '''
    return current_app.send_static_file('news/favicon.ico')

