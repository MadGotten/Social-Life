from website import create_app, login_manager, db
from flask import render_template, redirect, url_for, request, flash
from website.models import Post, User, Comment, Follow
from flask_login import login_required, current_user
from werkzeug.exceptions import RequestEntityTooLarge

ROWS_PER_PAGE = 5

app = create_app()

# TODO: refactor methods to have CRUD methodology
# TODO: add algorithm for displaying posts based on user followers, create date and others
@app.route('/')
@login_required
def main():
    page = request.args.get('page', type=int)
    posts = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    users = User.query.filter(User.id != current_user.id).limit(4).all()
    
    if request.headers.get('HX-Request'):
        return render_template("post.html", user=current_user, posts=posts, current_page=page)
    
    return render_template("main.html", user=current_user, posts=posts, users=users, current_page=page)


@app.route('/search', methods=["GET"])
@login_required
def search():
    searchText = request.args.get('search')
    users = User.query.filter(User.username.contains(searchText, autoescape=True)).limit(5).all()
    posts = Post.query.filter(Post.data.contains(searchText, autoescape=True)).limit(3).all()

    return render_template("search.html", user=current_user, posts=posts, users=users)


# TODO: add more error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html", user=current_user), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("errors/405.html", user=current_user), 405

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("File is too large. Maximum size allowed is 2MB.", category="error")
    return redirect(request.referrer)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.login'))