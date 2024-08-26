from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort
from .models import Post, Comment, Like
import uuid as uuid
from flask_login import login_required, current_user
from website.utils.decorators import verified_account
from website import db

posts = Blueprint('posts', __name__)


# TODO: refactor methods to use GET, POST, PUT, DELETE and consolidate them
# TODO: change response codes returned by server to be correct
@posts.route('/create_post', methods=["POST", "GET"])
@login_required
@verified_account
def create_post():
    if request.method == "POST":
        text = request.form['text']
        if 0 < len(text) <= 255:
            new_post = Post(data=text, user_id=current_user.id)
            db.session.add(new_post)
            current_user.notify_followers()
            db.session.commit()
            flash('Post has been published!', category='success')
            return redirect(url_for("main.index"))
        else:
            flash("Email or password cannot be empty!", "error")
    return render_template('post/create.html', user=current_user)


@posts.route('/create_comment/<post_id>', methods=["POST"])
@login_required
@verified_account
def create_comment(post_id):
    if request.method == "POST":
        comment = request.form["comment"]
        post_url = request.form["post_url"]
        if len(comment) > 0:
            new_comment = Comment(post_id=post_id, data=comment, user_id=current_user.id)
            db.session.add(new_comment)
            db.session.commit()
            flash("Comment published successfully!", category="success")
        return redirect(url_for('posts.open_post', post_url=post_url))
    return abort(405)


@posts.route('/p/<post_url>/', methods=["GET"])
@login_required
@verified_account
def open_post(post_url):
    post = Post.query.filter_by(id=post_url).first()
    if post:
        comments = Comment.query.filter_by(post_id=post.id).all()
        return render_template('post/detail.html', user=current_user, post=post, comments=comments)
    return abort(404)


@posts.route('/like_post/<post_id>/', methods=["POST"])
@login_required
@verified_account
def like_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if not post:
        flash('Post does not exist', category="error")
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, post_id=post_id, comment_id=None)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.user_id, post.likes)})


@posts.route('/like_comment/<comment_id>/', methods=["POST"])
@login_required
@verified_account
def like_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    like = Like.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()

    if not comment:
        flash('Comment does not exist', category="error")
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, post_id=comment.post_id, comment_id=comment_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(comment.likes), "liked": current_user.id in map(lambda x: x.user_id, comment.likes)})


# TODO: add function for deleting comments
@posts.route('/delete_post/<id>', methods=["POST"])
@login_required
@verified_account
def delete_post(id):
    post = Post.query.get(id)
    if post:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()
            flash("Post was deleted", category="success")

        return redirect(url_for("main.index"))
    return abort(405)

@posts.route('/delete_comment/<id>', methods=["POST"])
@login_required
@verified_account
def delete_comment(id):
    comment = Comment.query.get(id)
    if comment:
        if comment.user_id == current_user.id:
            db.session.delete(comment)
            db.session.commit()
            flash("Comment was deleted", category="success")

        return redirect(url_for('posts.open_post', post_url=request.form["post_url"]))
    return abort(405)