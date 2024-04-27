from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# Unpack SQLAlchemy classes into local variables
Column, Integer, String, Boolean, DateTime, ForeignKey, Model, func, relationship = (
    db.Column, db.Integer, db.String, db.Boolean, db.DateTime, db.ForeignKey, db.Model, db.func, db.relationship
)
class User(UserMixin, Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        # Used by Flask-Login to manage user sessions
        return str(self.id)

    def is_authenticated(self):
        # Assuming all users are authenticated once they are registered
        return True

    def is_active(self):
        # Assuming all users are active by default
        return True

    def is_anonymous(self):
        # We don't have anonymous users, so always return False
        return False

class WordleWords(Model):
    id = Column(Integer, primary_key=True)
    word = Column(String(10), nullable=False)

class Post(Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    datetime = Column(DateTime(100), server_default=func.now())
    content = Column(String(128), nullable=False)
    comments = relationship('Comment', backref='post', lazy=True) # one to many, this will add a post attribute to the comment class

    def set_content(self, content):
        self.content = content

class Comment(Model):
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id'))
    user_id = Column(Integer, ForeignKey("user.id"))
    datetime = Column(DateTime(100), server_default=func.now())
    content = Column(String(128), nullable=False)

    def set_content(self, content):
        self.content = content

class Score(Model):
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    score = Column(Integer, nullable=False, default=0)

    def __init__(self, user_id, score=0):
        self.user_id = user_id
        self.score = score

    # def to_dict(self):
    #     return {
    #         'user_id': self.user_id,
    #         'score': self.score
    #     }

    def set_score(self, score):
        self.score = score

    def add_score(self, score):
        self.score += score