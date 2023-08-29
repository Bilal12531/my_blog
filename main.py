from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
# Import your forms from the forms.py
from forms import CreatePostForm, reg_form,login_form,comments
import os
import smtplib
my_email = os.environ.get('MY_EMAIL')
my_pass = os.environ.get('MY_PASS')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)

gravatar = Gravatar(app, size=50,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", 'sqlite:///posts3.db')
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship('User', back_populates='post')
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comm = relationship('comment', back_populates='blog')



# TODO: Create a User table for all your registered users. 
class User(db.Model, UserMixin):
     __tablename__ = "users"
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(250), nullable=False)
     email =  db.Column(db.String(250), unique=True, nullable=False)
     password = db.Column(db.String(250), nullable=False)
     post = relationship('BlogPost', back_populates='author')
     comm = relationship('comment', back_populates='comment_auth')

class comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_auth = relationship('User', back_populates='comm')
    blog_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    blog = relationship('BlogPost', back_populates='comm')
    text = db.Column(db.Text, nullable = False)


with app.app_context():
    db.create_all()



# TODO: Use Werkzeug to hash the user's password when creating a new user.
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

@app.route('/register', methods = ['GET','POST'])
def register():
    reg = reg_form()
    if reg.validate_on_submit():
        name = reg.name.data
        email = reg.email.data
        password = reg.password.data
        res = db.session.execute(db.select(User).where(User.email == email))
        user = res.scalar() 
        if user:
            flash('login instead Register')
            return redirect(url_for('login'))   
        sec_pass = generate_password_hash(password, method="sha256", salt_length=8)
        entry = User(name = name, email = email,password = sec_pass)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html", form=reg, regis = True, c =current_user)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/',methods = ['GET','POST'])
def login():
    log = login_form()
    if log.validate_on_submit():
        email = log.email.data
        password = log.password.data
        res = db.session.execute(db.select(User).where(User.email == email))
        user = res.scalar()
        if not user:
            flash('Register Yourself')
            return redirect(url_for('login'))
        if not check_password_hash(user.password, password):
            flash('Wrong Password')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html", form = log, login = True, c =current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, login  = False,  c =current_user)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>",methods = ['POST','GET'])
@login_required
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    commenting = comments()
    if commenting.validate_on_submit():
        comm = commenting.com.data
        commen = comment( comment_auth= current_user,blog = requested_post, text = comm)
        db.session.add(commen)
        db.session.commit()
        return redirect(url_for('show_post', post_id = post_id))
    res = db.session.execute(db.select(comment))
    all_comm = res.scalars()
    return render_template("post.html",current_user = current_user, post=requested_post, comment =commenting, all_comm = all_comm)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
@login_required
def about():
    return render_template("about.html", c =current_user)


@app.route("/contact", methods = ['POST','GET'])
@login_required
def contact():
    if request.method == 'POST':
        data = request.form
        name = data['name']
        email = data['email']
        phone = data['phone']
        message = data['message']
        msg = "Successfully sent your message"
        send_msg(name, email, phone, message)
        return render_template("contact.html", msg_sent = msg)



    return render_template("contact.html", msg_sent = False, c =current_user)

def send_msg(name, email, phone, mseg):
    
    connection = smtplib.SMTP_SSL("smtp.gmail.com", 465)  
    connection.login(user=my_email, password=my_pass)   
    connection.sendmail(from_addr=my_email,
                        to_addrs=f"{email}", 
                        msg=f"Subject:Becon Jobs-job_finder\n\n Your Email:{email}\nYour Name:{name}\nYour Phone num:{phone}\nYour Message{mseg}")

    connection.quit()  

@app.route('/user_table', methods = ["POST","GET"])
def user_table():
    res = db.session.execute(db.select(User))
    users_data = res.scalars()
    return render_template('users_table.html', data = users_data, c =current_user)
    

if __name__ == "__main__":
    app.run(debug=False)
