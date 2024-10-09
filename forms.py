from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import EmailField, PasswordField
from wtforms.validators import DataRequired, URL, length, equal_to
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author =  StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class RegisterForm(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired(message="Enter Email")])
    firstname = StringField("First Name",validators=[DataRequired(message="Enter First Name")])
    password1 = PasswordField(label="Password",validators=[DataRequired(message="Please enter password"),length(min=8,max=15,message= "Password must be 8 characters long")])
    password2 = PasswordField(label="Confirm Password", validators=[DataRequired(message="Confirm assword"),length(min=8, max=15,message="Password must be 8 characters long"),equal_to('password1',message="Passwords Must Match")])
    submit = SubmitField(label="Submit")

class LoginForm(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired(message="Enter Email")])
    password = PasswordField(label="Password",validators=[DataRequired(message="Please enter password"),])
    submit = SubmitField(label="Submit")
