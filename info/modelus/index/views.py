from flask import current_app
from flask import render_template

from info.modelus.index import index_blu
@index_blu.route('/')
def index():

    return render_template('news/index.html')

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

