from flask import Blueprint, render_template, request, flash, abort, current_app, redirect, jsonify
from flask_login import login_required, current_user
from . import db
from .models import User, Post, Follow, Notification
from werkzeug.utils import secure_filename
import uuid as uuid
import os

profile = Blueprint('profile', __name__)


# TODO: Paginate users posts
@profile.route('/<username>/', methods=["GET"])
@login_required
def open_profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        posts = Post.query.filter_by(user_id=user.id).all()
        return render_template('profile.html', user=current_user, profile=user, posts=posts)
    return abort(404)


@profile.route('/follow_user/<username>/', methods=["POST"])
@login_required
def follow_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        # follower = Follow.query.filter_by(followed_id=current_user.id, follower_id=user.id).first()
        if current_user.is_following(user):
            current_user.unfollow(user)
            db.session.commit()
            return jsonify({"followed": False})
        elif not current_user.is_following(user):
            current_user.follow(user)
            db.session.commit()
            return jsonify({"followed": True})
    flash('User does not exist', category="error")


# TODO: Create exception error
@profile.route('/UploadProfileImage', methods=["POST"])
@login_required
def UploadProfileImage():
    if request.method == "POST":
        image = request.files["profileimage"]
        if image:
            if current_user.profile_img != "default.png":
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_PROFILE_FOLDER'],
                                           current_user.profile_img))  # Removing image from disc
                except:
                    pass
            image_filename = secure_filename(image.filename)
            image_name = str(uuid.uuid1()) + "_" + image_filename  # Genereting uuid for image
            image.save(os.path.join(current_app.config['UPLOAD_PROFILE_FOLDER'], image_name))  # Saving image to disc
            user = User.query.filter_by(id=current_user.id).first()
            user.profile_img = image_name
            db.session.commit()
            flash("Profile picture changed!", category="success")
    return redirect('/' + current_user.username + '/', code=302, Response=None)


# TODO: Implement better way of unchecking notifications
@profile.route('/checkNotfications', methods=["POST"])
@login_required
def checkNotfications():
    if request.method == "POST":
        notifications = Notification.query.filter(Notification.user_id == current_user.id).all()
        for notification in notifications:
            notification.status = False
        db.session.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}
