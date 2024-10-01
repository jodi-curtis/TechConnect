from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.mapped_column(db.Integer, primary_key=True)
    username = db.mapped_column(db.String(50), unique=True, nullable=False)
    password = db.mapped_column(db.String(80), nullable=False)

    profile = db.relationship('Profile', back_populates='user', uselist=False, cascade="all, delete")
    sent_requests = db.relationship('FriendRequest', back_populates='sender', foreign_keys='FriendRequest.sender_id', cascade="all, delete")
    received_requests = db.relationship('FriendRequest', back_populates='receiver', foreign_keys='FriendRequest.receiver_id', cascade="all, delete")
    friends = db.relationship('Friend', back_populates='user1', foreign_keys='Friend.user1_id', cascade="all, delete")
    posts = db.relationship('Post', back_populates='user', cascade="all, delete")
    likes = db.relationship('Like', back_populates='user', cascade="all, delete")
    comments = db.relationship('Comment', back_populates='user', cascade="all, delete")



    def __str__(self):
        return self.username


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.mapped_column(db.Integer, primary_key=True)
    user_id = db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    first_name = db.mapped_column(db.String(50), nullable=False)
    surname = db.mapped_column(db.String(50), nullable=False)
    email = db.mapped_column(db.String(100), nullable=False)
    bio = db.mapped_column(db.Text, nullable=True)
    programming_languages = db.mapped_column(db.String(200), nullable=True)
    github = db.mapped_column(db.String(50), nullable=True)
    linkedin = db.mapped_column(db.String(50), nullable=True)

    user = db.relationship('User', back_populates='profile')

    def __str__(self):
        return f"Profile of {self.user.username}"



class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'
    id = db.mapped_column(db.Integer, primary_key=True)
    sender_id = db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    sender = db.relationship('User', back_populates='sent_requests', foreign_keys=[sender_id])
    receiver = db.relationship('User', back_populates='received_requests', foreign_keys=[receiver_id])

    def __str__(self):
        return f"Request from {self.sender.username} to {self.receiver.username}"


class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.mapped_column(db.Integer, primary_key=True)
    user1_id = db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user1 = db.relationship('User', foreign_keys=[user1_id], back_populates='friends')
    user2 = db.relationship('User', foreign_keys=[user2_id])

    def __str__(self):
        return f"Friendship between {self.user1.username} and {self.user2.username}"
    


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.mapped_column(db.Integer, primary_key=True)
    title = db.mapped_column(db.String(100), nullable=False)
    content = db.mapped_column(db.Text, nullable=False)
    timestamp = db.mapped_column(db.DateTime, nullable=False, default=db.func.now())
    user_id = db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='posts')
    likes = db.relationship('Like', back_populates='post', cascade="all, delete")
    comments = db.relationship('Comment', back_populates='post', cascade="all, delete")


    def __str__(self):
        return f"Post by {self.user.username} on {self.timestamp}"

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.mapped_column(db.Integer, primary_key=True)
    user_id = db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.mapped_column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='likes')

    def __str__(self):
        return f"Like by {self.user.username} on post {self.post.id}"
    

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.mapped_column(db.Integer, primary_key=True)
    comment = db.mapped_column(db.Text, nullable=False)
    timestamp = db.mapped_column(db.DateTime, default=db.func.now())
    user_id = db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.mapped_column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    user = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')

    def __str__(self):
        return f"Comment by {self.user.username} on post {self.post.id}"