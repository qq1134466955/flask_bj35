from flask import Blueprint

news_blu = Blueprint('news',__name__,url_prefix="/news")

from info.modelus.news.views import *