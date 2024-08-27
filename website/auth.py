from flask import Blueprint, render_template, request, flash, redirect, url_for
from website import db, mail
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from .forms import LoginForm, RegisterForm
from .token import generate_token, confirm_token
from flask_mail import Message
from datetime import datetime

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        flash("You are already logged in!", category="info")
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.verify_password(form.password.data):
            remember_me = request.form.get("remember_me", default=False, type=bool)
            login_user(user, remember=remember_me)
            flash("Logged successfully!", category="success")
            return redirect(url_for("main.index"))
        else:
            flash("Incorrect email or password, try again.", "error")

    return render_template("auth/login.html", user=current_user, form=form)


@auth.route("/signup", methods=["POST", "GET"])
def signup():
    form = RegisterForm()
    if current_user.is_authenticated:
        flash("You are already logged in!", category="info")
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        user_email = User.query.filter_by(email=form.email.data.lower().lower()).first()
        user_username = User.query.filter_by(username=form.username.data.lower()).first()

        if user_email:
            flash("Email already exist.", category="error")
        elif user_username:
            flash("Username already exist.", category="error")
        else:
            user = User(
                email=form.email.data.lower(),
                password=form.password.data,
                username=form.username.data.lower(),
                first_name=form.firstname.data.capitalize(),
                last_name=form.lastname.data.capitalize(),
            )
            db.session.add(user)
            db.session.commit()
            token = generate_token(user.email)
            confirm_url = url_for("auth.confirm_email", token=token, _external=True)
            msg = Message(
                subject="Social Life - Confirm your account",
                html=render_template(
                    "auth/confirm_email.html", username=user.username, confirm_url=confirm_url
                ),
                recipients=[user.email],
            )
            mail.send(msg)
            login_user(user, remember=True)
            flash("Account created successfully!", category="success")
            return redirect(url_for("auth.inactive"))

    return render_template("auth/sign_up.html", user=current_user, form=form)


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", category="info")
    return redirect(url_for("auth.login"))


@auth.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        flash("Account already confirmed.", "success")
        return redirect(url_for("main.index"))
    email = confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.is_confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
    return redirect(url_for("main.index"))


@auth.route("/resend")
@login_required
def resend_confirmation():
    if current_user.is_confirmed:
        flash("Your account has already been confirmed.", "success")
        return redirect(url_for("main.index"))
    token = generate_token(current_user.email)
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    msg = Message(
        subject="Social Life - Confirm your account",
        html=render_template(
            "auth/confirm_email.html", username=current_user.username, confirm_url=confirm_url
        ),
        recipients=[current_user.email],
    )
    mail.send(msg)
    flash("A new confirmation email has been sent.", "success")
    return redirect(url_for("auth.inactive"))


@auth.route("/inactive")
@login_required
def inactive():
    if current_user.is_confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/inactive.html")
