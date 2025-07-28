from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):

    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=4, max=20, message='用户名长度必须在4到20个字符之间')])

    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, message='密码长度不能少于6个字符')])
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=4, max=20, message='用户名长度必须在4到20个字符之间')])

    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, message='密码长度不能少于6个字符')])

    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请输入密码'),
        EqualTo('password', message='两次输入密码不一样')
    ])

    submit = SubmitField('注册')

