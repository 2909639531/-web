import math
from enum import unique

from flask import Flask, render_template, request, redirect, url_for,flash
import os

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '<KEY>'

IMAGE_FOLDER = os.path.join('static', 'images')
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['IMAGES_PER_PAGE'] = 6
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True,nullable=False)
    password = db.Column(db.String(100),nullable=False)
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        action = request.form['action']
        username = request.form['username']
        password = request.form['password']
        if action == '登录':
            user = Post.query.filter_by(username=username).first()
            if user and (username == user.username and password == user.password):
                return redirect(url_for('gallery'))
            else:
                flash('账号密码错误','danger')
                return redirect(url_for('login'))

        elif action == '注册':
            existing_user = Post.query.filter_by(username=username).first()

            if existing_user:
                flash('该用户名已被注册，请换一个', 'warning')
                return redirect(url_for('login'))

            new_user = Post(username=username, password=password)

            db.session.add(new_user)
            db.session.commit()

            flash('注册成功！现在可以登录了', 'success')
            return redirect(url_for('login'))

@app.route('/gallery')
def gallery():
    images_total = sorted(os.listdir(app.config['IMAGE_FOLDER']))
    images_total_numbers = len(images_total)
    total_pages = math.ceil(float(images_total_numbers) / app.config['IMAGES_PER_PAGE'])
    page = request.args.get('page',1,type=int)
    start_page = (page-1)*app.config['IMAGES_PER_PAGE']
    end_page = page*app.config['IMAGES_PER_PAGE']
    paginated_images = images_total[start_page:end_page]

    return render_template(
        'gallery.html',
        images=paginated_images,
        page=page,
        total_pages=total_pages
    )

@app.route('/upload',methods=['GET','POST'] )
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['image_file']

        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join(app.config['IMAGE_FOLDER'], uploaded_file.filename))
            return redirect(url_for('gallery'))
    else:
        return render_template('upload.html')

@app.route('/mange',methods=['GET','POST'] )
def mange():
    if request.method == 'GET':
        return render_template("mange.html",images=sorted(os.listdir(app.config['IMAGE_FOLDER'])))
    elif request.method == 'POST':
        delete_image = request.form['image_to_delete']

        deleted_file_path = os.path.join(app.config['IMAGE_FOLDER'], delete_image)
        os.remove(deleted_file_path)

        flash(f'{delete_image}已被删除','success')

        return redirect(url_for('mange'))

if __name__ == '__main__':
    app.run(debug=True)