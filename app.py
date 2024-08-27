from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from website.models import Post, User
from website.utils.decorators import verified_account

main = Blueprint("main", __name__)

ROWS_PER_PAGE = 5


# TODO: refactor methods to have CRUD methodology
# TODO: add algorithm for displaying posts based on user followers, create date and others
@main.route("/")
@login_required
@verified_account
def index():
    page = request.args.get("page", type=int)
    posts = Post.query.order_by(Post.date.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    users = User.query.filter(User.id != current_user.id).limit(4).all()

    if request.headers.get("HX-Request"):
        return render_template("post/index.html", user=current_user, posts=posts, current_page=page)

    return render_template(
        "main.html", user=current_user, posts=posts, users=users, current_page=page
    )


@main.route("/search", methods=["GET"])
@login_required
@verified_account
def search():
    searchText = request.args.get("search")
    users = User.query.filter(User.username.contains(searchText, autoescape=True)).limit(5).all()
    posts = Post.query.filter(Post.data.contains(searchText, autoescape=True)).limit(3).all()

    return render_template("search.html", user=current_user, posts=posts, users=users)
