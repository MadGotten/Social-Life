from flask import Blueprint, flash, redirect, render_template, request
from flask_login import current_user
from werkzeug.exceptions import RequestEntityTooLarge

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html", user=current_user), 404


@errors.app_errorhandler(405)
def method_not_allowed(e):
    return render_template("errors/405.html", user=current_user), 405


@errors.app_errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("File is too large. Maximum size allowed is 2MB.", category="error")
    return redirect(request.referrer)
