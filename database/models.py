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
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

class Wordlewords(Model):
    id = Column(Integer, primary_key=True)
    word = Column(String(10), nullable=False)


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

class Wordleresult(Model):
    id = Column(Integer, primary_key=True)
    wordlegameid = Column(Integer, ForeignKey("wordlegame.id"))
    userid = Column(Integer, ForeignKey("user.id"))
    attempt1 = Column(String(5))
    attempt2 = Column(String(5))
    attempt3 = Column(String(5))
    attempt4 = Column(String(5))
    attempt5 = Column(String(5))
    attempt6 = Column(String(5))
    result = Column(String(20), default="incomplete")

class Wordlegame(Model):
    id = Column(Integer, primary_key=True)
    word = Column(String(10), nullable=False) #could also use wordid as a fk
    createduserid = Column(Integer, ForeignKey("user.id"))
