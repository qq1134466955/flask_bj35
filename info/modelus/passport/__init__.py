from flask import  Blueprint

passport_blu = Blueprint('passport',__name__,url_prefix='/passport')

from .views import *
# from info.modelus.passport import passport_blu