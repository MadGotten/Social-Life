from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from .forms import CSRFForm

db = SQLAlchemy()

login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.ProductionConfig')

    with app.app_context():
        migrate = Migrate(app, db)
        moment = Moment(app)
        
        db.init_app(app)
        moment.init_app(app)
        csrf.init_app(app)
        mail.init_app(app)

        from .models import User, Post, Comment, Like, Follow, Notification

        from app import main
        from .posts import posts
        from .profile import profile
        from .auth import auth
        from .errors import errors
        from .commands import create_admin

        app.register_blueprint(main, url_prefix='/')
        app.register_blueprint(posts, url_prefix='/')
        app.register_blueprint(profile, url_prefix='/')
        app.register_blueprint(auth, url_prefix='/')
        app.register_blueprint(errors, url_prefix='/')

        app.cli.add_command(create_admin)

        login_manager.login_view = 'login.html'
        login_manager.init_app(app)
        
        @app.context_processor
        def inject_csrf_token():
            return dict(csrf_form=CSRFForm())

        @login_manager.user_loader
        def load_user(id):
            return User.query.get(int(id))
        
        @login_manager.unauthorized_handler
        def unauthorized():
            return redirect(url_for('auth.login'))

        create_database(app)

        Notification.delete_expired_notifications()
        return app


def create_database(app):
    with app.app_context():
        db.create_all()
        print("Database created!")
