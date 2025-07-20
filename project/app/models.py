from datetime import datetime

from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True,nullable=False)
    password = db.Column(db.String(100),nullable=False)

    images = db.relationship('Image', backref='user', lazy=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100),nullable=False)
    upload_data = db.Column(db.DateTime,nullable=False,default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)