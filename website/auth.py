from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db, login_manager
from .models import User
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .forms import LoginForm, RegisterForm

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        flash('You are already logged in!', category='info')
        return redirect(url_for('main'))
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password, form.password.data):
            remember_me = request.form.get('remember_me', default=False, type=bool)
            login_user(user, remember=remember_me)
            flash('Logged successfully!', category='success')
            return redirect(url_for('main'))
        else:
            flash("Incorrect email or password, try again.", "error")

    return render_template("auth/login.html", user=current_user, form=form)


@auth.route('/signup', methods=["POST", "GET"])
def signup():
    form = RegisterForm()
    if current_user.is_authenticated:
        flash('You are already logged in!', category='info')
        return redirect(url_for('main'))
    
    if form.validate_on_submit():
        user_email = User.query.filter_by(email=form.email.data.lower().lower()).first()
        user_username = User.query.filter_by(username=form.username.data.lower()).first()
        
        if user_email:
            flash("Email already exist.", category='error')
        elif user_username:
            flash("Username already exist.", category='error')
        else:
            new_user = User(
                email=form.email.data.lower(), 
                password=generate_password_hash(form.password.data), 
                username=form.username.data.lower(),
                first_name=form.firstname.data.capitalize(),
                last_name=form.lastname.data.capitalize()
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created successfully!", category="success")
            return redirect(url_for('main'))

    return render_template("auth/sign_up.html", user=current_user, form=form)


@auth.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', category='info')
    return redirect(url_for('auth.login'))
