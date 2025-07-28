import math
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, render_template, request, redirect, url_for,session,flash,jsonify

from app import app,db
from app.forms import RegisterForm, LoginForm
from app.models import User,Image

def login_required_factory(original_function):
    @wraps(original_function)
    def wrapper_function(*a,**kw):
        if 'username' not in session:
            flash('登录才能访问此界面','warning')
            return redirect(url_for('login'))
        return original_function(*a,**kw)
    return wrapper_function

def manger_required_factory(original_function):
    @wraps(original_function)
    def wrapper_function(*a,**kw):
        if session.get('role') != 'admin':
            flash('管理员才能访问此页面','warning')
            return redirect(url_for('login'))
        return original_function(*a,**kw)
    return wrapper_function
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('gallery'))
        else:
            flash('账号或密码错误','warning')
    return render_template("login.html",form=form)

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('改用户名已经存在了', 'warning')
        else:
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功！现在可以登录了。', 'success')
            return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/gallery')
@login_required_factory
def gallery():
    page = request.args.get('page',1,type=int)
    per_page = app.config['IMAGES_PER_PAGE']
    pagination = Image.query.order_by(Image.upload_date.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    images = pagination.items

    return render_template('gallery.html',
                           images=images,
                           pagination=pagination)


@app.route('/upload',methods=['GET','POST'] )
@login_required_factory
def upload():
    if request.method == 'POST':
        uploaded_file = request.files.get('image_file')
        if not(uploaded_file):
            flash('请选择文件','warning')
            return redirect(url_for('upload'))
        enter_filename = request.form.get('image_name')
        filename = enter_filename if enter_filename else uploaded_file.filename
        existing_image = Image.query.filter_by(filename=filename).first()
        if existing_image:
            flash(f'文件名“{filename}”已经存在了，换个名字', 'warning')
            return redirect(url_for('upload'))
        uploaded_file.save(os.path.join(app.config['IMAGE_FOLDER'],filename))

        current_user = User.query.filter_by(username=session['username']).first()
        new_image = Image(filename=filename, user=current_user)
        db.session.add(new_image)
        db.session.commit()
        flash(f'上传完毕！图片 "{filename}" 已保存。', 'success')

        return redirect(url_for('upload'))
    else:
        return render_template('upload.html')

@app.route('/mange',methods=['GET','POST'] )
@login_required_factory
@manger_required_factory
def mange():
    return render_template("mange.html",images=Image.query.order_by(Image.upload_date.desc()).all())

@app.route('/sync_images',methods=['POST'] )
@login_required_factory
@manger_required_factory
def sync_images():
    image_folder = app.config['IMAGE_FOLDER']
    db_filenames = {img.filename for img in Image.query.all()}
    folder_filenames = os.listdir(image_folder)
    new_files_to_add = [f for f in folder_filenames if f not in db_filenames]
    if new_files_to_add:
        current_user = User.query.filter_by(username=session['username']).first()
        for filename in new_files_to_add:
            new_image = Image(filename=filename,user=current_user)
            db.session.add(new_image)
        db.session.commit()
        flash('同步完成', 'success')
    else:
        flash('没有新的图片需要同步','warning')
    return redirect(url_for('mange'))


@app.route('/delete-image',methods=['POST'] )
@login_required_factory
def delete_image():
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'status':'error','message':'请求者未包含文件名'})
    try:
        delete_file_path = os.path.join(app.config['IMAGE_FOLDER'], filename)
        if os.path.exists(delete_file_path):
            os.remove(delete_file_path)
        image_to_delete = Image.query.filter_by(filename=filename).first()
        if image_to_delete:
            db.session.delete(image_to_delete)
            db.session.commit()
        return jsonify({'status':'success'})
    except:
        db.session.rollback()
        return jsonify({'status':'error','message':'<UNK>'})


@app.route('/user',methods=['GET','POST'] )
@login_required_factory
def user():
    username_from_user = session['username']
    current_user_id = User.query.filter_by(username=username_from_user).first()
    return render_template('user.html',user=current_user_id)

@app.route('/like_image',methods=['POST'] )
@login_required_factory
def like_image():
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'status':'error','message':'？为啥没图片'})

    like_image = Image.query.filter_by(filename=filename).first()
    current_user = User.query.filter_by(username=session['username']).first()

    if current_user in like_image.likers:
        return jsonify({'status':'error','message':'你已经赞过了'})

    if like_image:
        like_image.likers.append(current_user)
        like_image.likes += 1
        db.session.add(like_image)
        db.session.commit()
        return jsonify({'status':'success',"new_count":like_image.likes})
    else:
        return jsonify({'status':'error','message':'???数据库里面没这个图片'})

@app.route('/dislike_image',methods=['POST'] )
@login_required_factory
def dislike_image():
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'status':'error','message':'？为啥没图片'})

    dislike_image = Image.query.filter_by(filename=filename).first()
    current_user = User.query.filter_by(username=session['username']).first()

    if current_user in dislike_image.dislikers:
        return jsonify({'status':'error','message':'你已经赞过了'})

    if dislike_image:
        dislike_image.dislikers.append(current_user)
        dislike_image.dislikes += 1
        db.session.add(dislike_image)
        db.session.commit()
        return jsonify({'status':'success',"new_count":dislike_image.dislikes})
    else:
        return jsonify({'status':'error','message':'???数据库里面没这个图片'})

@app.route('/logout')
def logout():

    session.pop('username', None)

    flash('您已成功退出登录', 'success')

    return redirect(url_for('login'))