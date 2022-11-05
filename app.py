from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

base_dir = os.path.dirname(os.path.realpath(__file__))
current_user= os.environ.get('USERNAME')

app = Flask(__name__, template_folder='templates')

app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///' + os.path.join(base_dir, 'users.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '923054541f636448117274bc' 

db = SQLAlchemy(app)
login_manager = LoginManager(app)

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

if __name__ == '__main__':
        app.run(debug=True)



