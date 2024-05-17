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
    gender = Column(String(10), nullable=False)
    dob = Column(DateTime, nullable=False)
    phone = Column(String(20))
    country = Column(String(50), nullable=False)
    avatar = Column(String(20), nullable=False)
    score = Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

class Score(Model):
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    score = Column(Integer, nullable=False, default=0)

    def __init__(self, user_id, score=0):
        self.user_id = user_id
        self.score = score

    def set_score(self, score):
        self.score = score

    def add_score(self, score):
        self.score += score

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class Post(Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    datetime = Column(DateTime(100), server_default=func.now())
    content = Column(String(128), nullable=False)
    hint = Column(String(128), nullable=False)
    language = Column(String(10), nullable=False, default='en')
    status = Column(Boolean, nullable=False, default=False) # false: active, true: completed
    comments = relationship('Comment', backref='post', lazy=True) # one to many, this will add a post attribute to the comment class
    images = relationship('Image', backref='post', lazy=True)

    def to_dict(self):
        post_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Handling relationships
        post_dict['comments'] = [comment.to_dict() for comment in self.comments]
        post_dict['images'] = [image.url for image in self.images]
        return post_dict

class Image(db.Model):
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id'))
    url = Column(String(255), nullable=False)

class Comment(Model):
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id'))
    user_id = Column(Integer, ForeignKey("user.id"))
    datetime = Column(DateTime(100), server_default=func.now())
    content = Column(String(128), nullable=False)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}