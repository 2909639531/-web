import math

from flask import Flask, render_template, request, redirect, url_for,flash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '<KEY>'

IMAGE_FOLDER = os.path.join('static', 'images')
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['IMAGES_PER_PAGE'] = 6

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '123456':
            return redirect(url_for('gallery'))
        else:
            flash('账号密码错误','danger')
            return redirect(url_for('gallery'))

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