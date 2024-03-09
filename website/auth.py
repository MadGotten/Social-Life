from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db, login_manager
from .models import User
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash('Already logged in!', category='info')
        return redirect(url_for('main'))
    else:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            if len(email) > 0 and len(password) > 0:
                user = User.query.filter_by(email=email).first()
                if user:
                    if check_password_hash(user.password, password):
                        flash('Logged successfully!', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('main'))
                    else:
                        flash("Incorrect password, try again.", "error")
                else:
                    flash("Email does not exist.", "error")
            else:
                flash("Email or password cannot be empty!", "error")
        return render_template("auth/login.html", user=current_user)


@auth.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]
        username = request.form["username"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]

        if len(email) < 4:
            flash("Email must be greater than 4 characters.", category="error")
        elif len(password) < 8:
            flash("Password must be greater than 8 characters.", category="error")
        elif password != password2:
            flash("Password don't match.", category="error")
        elif not re.search("[!@#$%^&*]", password):
            flash("Password must contain at least one special character.", category="error")
        elif not re.search(r"\d", password):
            flash("Password must contain at least one number.", category="error")
        elif len(username) < 1:
            flash("Username must be greater than 1 characters.", category="error")
        elif re.match("^[a-zA-Z0-9]*$", username) is None:
            flash("Username must use only a-Z characters and 0-9 numbers", category="error")
        elif len(firstname) < 2:
            flash("First must be greater than 2 characters.", category="error")
        elif len(lastname) < 2:
            flash("Last name must be greater than 2 characters.", category="error")
        else:
            user_email = User.query.filter_by(email=email.lower()).first()
            user_username = User.query.filter_by(username=username.lower()).first()
            if user_email:
                flash("Email already exist.", category='error')
            elif user_username:
                flash("Username already exist.", category='error')
            else:
                new_user = User(email=email, password=generate_password_hash(password, method='sha256'), username=username.lower(), first_name=firstname, last_name=lastname)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash("Account created!", category="success")
                return redirect(url_for('main'))

    return render_template("auth/sign_up.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', category='info')
    return redirect(url_for('auth.login'))
