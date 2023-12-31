from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post") 



class reg_form(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')



class login_form(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class comments(FlaskForm):
    com = CKEditorField('Comment Feild')
    submit = SubmitField('Submit')

class forgot_passw(FlaskForm):
    email = StringField('Enter your Email', validators=[DataRequired()])
    submit = SubmitField('Submit')

class verify_password(FlaskForm):
    Password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class reset_password(FlaskForm):
    Password = StringField('Enter Your New Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')