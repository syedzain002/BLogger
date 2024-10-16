from functools import wraps
from os import abort
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from datetime import date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import email
from forms import CreatePostForm,RegisterForm,LoginForm
from flask_login import login_user, login_required, logout_user, current_user, UserMixin, LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor()
ckeditor.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CONFIGURING TABLES FOR BLOGPOST AND USER
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class User(db.Model,UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250),unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    firstname: Mapped[str] = mapped_column(String(250), nullable=False)

#CREATES THE DATABASE
with app.app_context():
    db.create_all()

#CONFIGURING THE LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(id):
   return User.query.get(int(id))

#THIS IS THE ADMIN DECORATOR , USED FOR ADMIN RIGHTS
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

#THE FOLLOWING ROUTES ARE FOR VIEWS
@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts,current_user=current_user)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost,post_id)
    return render_template("post.html", post=requested_post,current_user=current_user)

@app.route('/add',methods=["GET","POST"])
@admin_only
def add():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body= form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d,%Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html",form=form,heading="New Post",current_user=current_user)

@app.route('/edit-post/<post_id>',methods=["GET","POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost,post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle=edit_form.subtitle.data
        post.body=edit_form.body.data
        post.img_url=edit_form.img_url.data
        post.author=edit_form.author.data
        db.session.commit()
        return redirect(url_for("show_post",post_id=post_id))
    return render_template("make-post.html",form=edit_form,heading="Edit Post",current_user=current_user)

@app.route('/delete-post/<post_id>')
def delete_post(post_id):
    post = db.get_or_404(BlogPost,post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

#THE FOLLOWING ROUTES ARE FOR AUTHENTICATIONS

@app.route("/register",methods=["GET","POST"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                email=form.email.data,
                firstname=form.firstname.data,
                password=generate_password_hash(form.password1.data, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash("Account Created!", category="success")
        except :
            flash("User Already Exists,Please Log-In", category="success")
        return redirect(url_for("login"))
    return render_template("register.html",form=form)

@app.route("/login/",methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        user=db.session.query(User).filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                print("Login Successful")
                login_user(user)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Wrong Password,Re-enter", category="error")

        else:
            flash("User does not exist,please register first.", category="error")

    return render_template("login.html",form=form,current_user=current_user)

@app.route("/logout")
@login_required
def logout():
    # db.session.query(User).delete()
    # db.session.commit()
    logout_user()
    return redirect(url_for("get_all_posts"))

#THE FOLLLOWING ROUTES ARE FOR ABOUT AND CONTACT PAGES
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
