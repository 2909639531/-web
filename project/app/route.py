import math
import os
from functools import wraps

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
        if user and user.password == form.password.data:
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
            new_user = User(username=form.username.data, password=form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功！现在可以登录了。', 'success')
            return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/gallery')
@login_required_factory
def gallery():

    images_total = Image.query.order_by(Image.upload_data.desc()).all()

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
@login_required_factory
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['image_file']
        filename = request.form['image_name']

        if uploaded_file.filename != '' and filename:
            uploaded_file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))

            current_user_id = User.query.filter_by(username=session['username']).first()
            uploaded_file_name = Image(filename=filename, user=current_user_id)
            db.session.add(uploaded_file_name)
            db.session.commit()
            flash(f'上传完毕{filename}', 'success')


            return redirect(url_for('upload'))

        else:
            flash('输入文件和文件名', 'warning')
            return redirect(url_for('upload'))
    else:
        return render_template('upload.html')

@app.route('/mange',methods=['GET','POST'] )
@login_required_factory
@manger_required_factory
def mange():
    return render_template("mange.html",images=Image.query.order_by(Image.upload_data.desc()).all())


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


@app.route('/logout')
def logout():

    session.pop('username', None)

    flash('您已成功退出登录', 'success')

    return redirect(url_for('login'))