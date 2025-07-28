# app/__init__.py
import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- 配置区 ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['IMAGES_PER_PAGE'] = 15
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 使用绝对路径，让程序无论在哪里运行都能找到文件
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['IMAGE_FOLDER'] = os.path.join(app.static_folder, 'images')

# --- 初始化插件 ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import route, models
