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

class Post(Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id"))
    datetime = Column(DateTime(100), server_default=func.now())
    content = Column(String(128), nullable=False)
    comments = relationship('Comment', backref='post', lazy=True) # one to many, this will add a post attribute to the comment class

    def set_content(self, content):
        self.content = content

class Comment(Model):
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('Post.id'))
    user_id = Column(Integer, ForeignKey("User.id"))
    datetime = Column(DateTime(100), server_default=func.now())
    content = Column(String(128), nullable=False)

    def set_content(self, content):
        self.content = content
    
'''
FORUM
 - POST
    -POST ID PK
    -USERID FK
    -DATETIME
    -CONTENT
    -COMMENT relationship 
 - COMMENTS
    - COMMENT ID PK
    - POST ID FK
    - USER ID FK
    - DATETIME
    - CONTENT
'''