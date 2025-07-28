from datetime import datetime

from app import db

likes_table = db.Table('likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True)
)

dislikes_table = db.Table('dislikes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True,nullable=False)
    password = db.Column(db.String(100),nullable=False)
    role = db.Column(db.String(10),nullable=False,default='user',server_default='user')
    images = db.relationship('Image', backref='user', lazy=True)

    liked_images = db.relationship('Image', secondary=likes_table, back_populates='likers')
    disliked_images = db.relationship('Image', secondary=dislikes_table, back_populates='dislikers')


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100),nullable=False)
    upload_date = db.Column(db.DateTime,nullable=False,default=datetime.now)
    likes = db.Column(db.Integer,default=0,nullable=False)
    dislikes = db.Column(db.Integer,default=0,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

    likers = db.relationship('User', secondary=likes_table, back_populates='liked_images')
    dislikers = db.relationship('User',secondary=dislikes_table, back_populates='disliked_images')
