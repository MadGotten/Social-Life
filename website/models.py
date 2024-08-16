from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import event
from datetime import datetime, timezone, timedelta


# TODO: Do some cleanup with database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    profile_img = db.Column(db.String(), default="default.png")
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', cascade="all, delete-orphan")
    followed = db.relationship('Follow', foreign_keys='Follow.follower_id',
                               backref=db.backref('follower', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id',
                                backref=db.backref('followed', lazy='joined'), lazy='dynamic',
                                cascade='all, delete-orphan')
    notification = db.relationship('Notification', backref='user', lazy=True)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(followed=user, follower=self)
            db.session.add(follow)
            db.session.commit()
            return True
        return False

    def unfollow(self, user):
        follow = self.followed.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()
            return True
        return False

    def notify_followers(self):
        followers = self.followers.with_entities(Follow.followed_id, Follow.follower_id).all()
        if followers:
            for followed in followers:
                notification_object = Notification_object(entity_type=1, entity_id=self.id)
                notification = Notification(user_id=followed.follower_id, notification_object=[notification_object])
                db.session.add(notification)
                db.session.add(notification_object)


# TODO: Implement notification creating on insert in tables Post
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(255))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    url = db.Column(db.String(12), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post', cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='post', cascade="all, delete-orphan")
    

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(255))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    likes = db.relationship('Like', backref='comment', cascade="all, delete-orphan")


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete="CASCADE"))


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())


@event.listens_for(Follow, 'after_insert')
def create_notification_on_follow(mapper, connection, follow):
    notification_object = Notification_object(entity_type=3, entity_id=follow.follower_id)
    notification = Notification(user_id=follow.followed_id, notification_object=[notification_object])
    db.session.add(notification)
    db.session.add(notification_object)


# TODO: Implement built-in functions for adding new notifications
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    status = db.Column(db.BOOLEAN, default=True)
    notification_object = db.relationship('Notification_object', backref='notification', cascade='all, delete-orphan')

    @staticmethod
    def delete_expired_notifications():
        expiration_date = datetime.now(timezone.utc) - timedelta(days=3)
        expired_notifications = Notification.query.filter(Notification.date <= expiration_date).all()
        for notification in expired_notifications:
            db.session.delete(notification)
        db.session.commit()


class Notification_object(db.Model):
    notification_id = db.Column(db.Integer, db.ForeignKey('notification.id', ondelete="CASCADE"), primary_key=True)
    entity_type = db.Column(db.Integer, nullable=False)
    entity_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    entity = db.relationship('User', backref='notification_object', foreign_keys=entity_id)

# Entity type
# 1 User B created a Post // User madgotten has added a new post <gray>data<gray>
# 2 User B commented on your Post // User madgotten has commented on your post <gray>data<gray>
