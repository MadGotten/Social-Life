from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment

db = SQLAlchemy()

login_manager = LoginManager()


# TODO: Delete unused functions
# TODO: Implement more functionality for running dev or production
# TODO: move variables to a separate config file
def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config.py")

    with app.app_context():
        migrate = Migrate(app, db)
        moment = Moment(app)

        db.init_app(app)
        moment.init_app(app)

        from .models import User, Post, Comment, Like, Follow, Notification, Notification_object

        from .posts import posts
        from .profile import profile
        from .auth import auth

        app.register_blueprint(posts, url_prefix='/')
        app.register_blueprint(profile, url_prefix='/')
        app.register_blueprint(auth, url_prefix='/')

        login_manager.login_view = 'login.html'
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(id):
            return User.query.get(int(id))

        create_database(app)

        Notification.delete_expired_notifications()
        #Follow.query.delete()
        #db.session.commit()
        return app


def create_database(app):
    with app.app_context():
        db.create_all()
        print("Database created!")
