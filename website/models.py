import uuid as uuid
from datetime import datetime, timedelta, timezone

from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType
from werkzeug.security import check_password_hash, generate_password_hash

from website import db


class TimestampMixin:
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime(), nullable=False, default=datetime.now, onupdate=datetime.now
    )


class User(db.Model, UserMixin, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    _password = db.Column(db.String(170), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)
    profile_img = db.Column(db.String(), default="default.png")
    is_confirmed = db.Column(db.Boolean(), nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime(), nullable=True)
    privacy_level = db.Column(db.String(10), default="public")
    posts = db.relationship("Post", backref="user", passive_deletes=True)
    comments = db.relationship("Comment", backref="user", cascade="all, delete-orphan")
    followed = db.relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        backref=db.backref("follower", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    followers = db.relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        backref=db.backref("followed", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    notification = db.relationship(
        "Notification", backref="user", foreign_keys="Notification.user_id", lazy=True
    )

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password, password)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(followed=user, follower=self)
            notification = Notification(user_id=user.id, notification_type=3, entity_id=self.id)
            db.session.add(follow)
            db.session.add(notification)
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
                notification = Notification(
                    user_id=followed.follower_id, notification_type=1, entity_id=self.id
                )
                db.session.add(notification)

    def can_view_profile(self, user):
        if not self.privacy_level == "private":
            return True
        return user == self or user.is_following(self)


# TODO: Implement notification creating on insert in tables Post
class Post(db.Model):
    id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    data = db.Column(db.String(255))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    comments = db.relationship("Comment", backref="post", cascade="all, delete-orphan")
    likes = db.relationship("Like", backref="post", cascade="all, delete-orphan")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(255))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    post_id = db.Column(UUIDType(), db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    likes = db.relationship("Like", backref="comment", cascade="all, delete-orphan")


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    post_id = db.Column(UUIDType(), db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id", ondelete="CASCADE"))


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())


# TODO: Implement built-in functions for adding new notifications
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    entity_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    notification_type = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    read = db.Column(db.Boolean, default=False)
    entity = db.relationship("User", backref="entity", foreign_keys=entity_id)

    @staticmethod
    def delete_expired_notifications():
        expiration_date = datetime.now(timezone.utc) - timedelta(days=3)
        expired_notifications = Notification.query.filter(
            Notification.timestamp <= expiration_date
        ).all()
        for notification in expired_notifications:
            db.session.delete(notification)
        db.session.commit()


# Entity type
# 1 User B created a Post // User madgotten has added a new post <gray>data<gray>
# 2 User B commented on your Post //
# User madgotten has commented on your post <gray>data<gray>
