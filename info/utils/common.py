from flask import current_app
from flask import g
from flask import session
import functools
from info.models import User


def do_index_class(index):
   '''
   如果index == 1 first， 2 second, 3 third
   :param index:  被过滤的参数
   :return:
   '''
   if index == 1:
       return 'first'

   elif index == 2:
       return 'second'

   elif index == 3:
       return 'third'

   else:
       return ''

def user_login_data(f):
    # TODO: 如果用装饰器装饰函数,那么装饰器会修改函数的名字为装饰器的内层函数的名字 将被装饰的试图函数的名字保持原有不变
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # TODO: g 变量 通过一个属性获取一个值
        g.user = user
        return f()
    return wrapper

