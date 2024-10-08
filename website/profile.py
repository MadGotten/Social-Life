import os
import uuid as uuid
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from website import db
from website.utils.decorators import verified_account
from .forms import UpdateSettingsForm
from .models import Notification, Post, User

profile = Blueprint("profile", __name__)

POST_PER_PAGE = 9


# TODO: Paginate users posts
@profile.route("/<username>/", methods=["GET"])
@login_required
@verified_account
def open_profile(username):
    page = request.args.get("page", type=int)
    user = User.query.filter_by(username=username).first()
    if user:
        if user.can_view_profile(current_user):
            posts = Post.query.filter_by(user_id=user.id).paginate(
                page=page, per_page=POST_PER_PAGE
            )
        else:
            posts = None
        if request.headers.get("HX-Request"):
            return render_template(
                "profile/posts.html", profile=user, posts=posts, current_page=page
            )
        return render_template(
            "profile/index.html", user=current_user, profile=user, posts=posts, current_page=page
        )
    return abort(404)


@profile.route("/settings", methods=["GET", "POST"])
@login_required
@verified_account
def settings():
    form = UpdateSettingsForm(obj=current_user)
    if form.validate_on_submit():
        if form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash("Email already in use.", category="error")
            else:
                current_user.email = form.email.data
                flash("Email updated successfully!", category="success")

        if form.password.data:
            current_user.password = form.password.data
            flash("Password updated successfully!", category="success")

        if form.privacy_level.data != current_user.privacy_level:
            current_user.privacy_level = form.privacy_level.data
            flash("Privacy level updated successfully!", category="success")
        db.session.commit()
        return redirect(url_for("profile.settings"))

    return render_template("profile/settings.html", user=current_user, form=form)


@profile.route("/follow_user/<username>/", methods=["POST"])
@login_required
@verified_account
def follow_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if current_user.is_following(user):
            current_user.unfollow(user)
            return jsonify({"followed": False})
        elif not current_user.is_following(user):
            current_user.follow(user)
            return jsonify({"followed": True})
    flash("User does not exist", category="error")


@profile.route("/UploadProfileImage", methods=["POST"])
@login_required
@verified_account
def UploadProfileImage():
    if request.method == "POST":
        image = request.files["profileimage"]
        if not image:
            flash("No image uploaded!", category="error")
            return redirect(url_for("profile.open_profile", username=current_user.username))

        image_filename = secure_filename(image.filename)
        file_ext = os.path.splitext(image_filename)[1].lower()

        if file_ext not in current_app.config["UPLOAD_EXTENSIONS"]:
            flash("Invalid image format!", category="error")
            return redirect(url_for("profile.open_profile", username=current_user.username))

        if current_user.profile_img != "default.png":
            old_path = os.path.join(
                current_app.config["UPLOAD_PROFILE_FOLDER"], current_user.profile_img
            )
            if os.path.exists(old_path):
                os.remove(old_path)

        image_name = f"{uuid.uuid1()}_{image_filename}"
        image_path = os.path.join(current_app.config["UPLOAD_PROFILE_FOLDER"], image_name)

        image.save(image_path)

        current_user.profile_img = image_name
        db.session.commit()
        flash("Profile picture changed successfully!", category="success")
    return redirect(url_for("profile.open_profile", username=current_user.username))


# TODO: Implement better way of unchecking notifications
@profile.route("/checkNotfications", methods=["POST"])
@login_required
@verified_account
def checkNotfications():
    if request.method == "POST":
        notifications = Notification.query.filter(Notification.user_id == current_user.id).all()
        for notification in notifications:
            notification.read = True
        db.session.commit()
    return jsonify({"success": True}), 200, {"ContentType": "application/json"}
