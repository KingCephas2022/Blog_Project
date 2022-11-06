from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

base_dir = os.path.dirname(os.path.realpath(__file__))
current_user= os.environ.get('USERNAME')

app = Flask(__name__, template_folder='templates')

app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///' + os.path.join(base_dir, 'blog.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '923054541f636448117274bc' 

db = SQLAlchemy(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.Text(), nullable = False)
    first_name = db.Column(db.Text(), nullable = True)
    last_name = db.Column(db.Text(), nullable = True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f"User {self.username}"

class Blog(db.Model):
    __tablename__ = "blog"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable = False)
    content = db.Column(db.String(150), nullable = True)
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f"Blog {self.title}"


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method=="POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        
        if user:
                if check_password_hash(user.password, password):
                    flash("Logged in!", category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Password is incorrect.', category='error')
        else:
                flash('Email does not exist.', category='error')

    return render_template('login.html')

@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))

@app.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(
                email=email, username=username, 
                password_hash=generate_password_hash(
                    password1, method='sha256'
                )
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for("login"))
    return render_template('signup.html')

# To post

@app.route("/post", methods=['POST'])
def post():
    if request.method =='POST':
        title = request.form.get('title')
        content = request.form.get('content')
        date_posted = datetime.utcnow()

        title = post.query.filter_by(title=title).first()
        if title:
            return redirect(url_for('post'))

        content = post.query.filter_by(content=content).first()
        if content:
            return redirect(url_for('blog'))

        new_post = post(title=title, content=content, date_posted=date_posted) 

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('post.html')

### To edit 

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    edit = post.query.get_or_404(id)

    if current_user.username == post.author:
        if request.method == 'POST':
            post.title = request.form['title']
            post.content = request.form['content']

            db.session.commit()
            flash("Heads up! Post created")
            return redirect(url_for('home', id=post.id))
        
        context = {'post': post}
        return redirect(url_for('edit'))

    return render_template('edit.html', post=post)

### To delete

@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete(id):
    deleteblog= post.query.get_or_404(id)

    if current_user.username == post.author:
        if request.method == 'POST':
            db.session.delete(deleteblog)
            db.session.commit()
            flash("Post deleted")
            return redirect(url_for('home'))

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
        app.run(debug=True)
