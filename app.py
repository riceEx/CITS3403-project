from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_session import Session
from flask_socketio import SocketIO
from sqlalchemy import func, event
from werkzeug.security import generate_password_hash
from database.models import db, User, Score, Post, Comment
from werkzeug.exceptions import Unauthorized
from datetime import datetime
import sqlite3
import random

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        dob_str = request.form['dob']
        phone = request.form['phone']
        country = request.form['country']
        avatar = request.form['avatar']  # Selected avatar filename

        dob = datetime.strptime(dob_str, '%Y-%m-%d')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            email=email,
            gender=gender,
            dob=dob,
            phone=phone,
            country=country,
            avatar=avatar)

        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. You can now login.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for('index'))
    else:
        flash('Incorrect username or password', 'error')
        return redirect(url_for('index'))


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

# add_post, create a new post
# @param user_id which user created the post
# @param content post content
# @param hint hint to the guessing game
# @param language, source language of the hint, default is english
@app.route('/add_post', methods=['POST'])
#! @login_required
def add_post():
    _user_id = request.form["user_id"]
    _content = request.form["content"]
    _hint = request.form["hint"]
    #if user_id, content or hint is not provided, return error
    if not _user_id or not _content or not _hint:
        return jsonify({'message': 'Missing parameters'}), 400
    _language = request.form["language"] or 'en'

    score = Post(user_id=_user_id, content=_content, hint=_hint, language=_language)
    db.session.add(score)
    db.session.commit()

    flash('Post added!', 'success')
    return jsonify({ "result": score.to_dict() })

# add_comment, create a comment to a post
# @param user_id which user created the post
# @param content post content
@app.route('/add_comment', methods=['POST'])
#! @login_required
def add_comment():
    _user_id = request.form["user_id"]
    _post_id = request.form["post_id"]
    _content = request.form["content"]
    #if user_id, content or hint is not provided, return error
    if not _user_id or not _content or not _post_id:
        return jsonify({'message': 'Missing parameters'}), 400

    try:
        # Begin a transaction of multiple operations
        with db.session.begin():
            comment = Comment(user_id=_user_id, post_id=_post_id, content=_content)
            db.session.add(comment)
            check_game(_user_id, _post_id, _content)
            db.session.commit()

    except Exception as e:
        print("add_comment error:", e)
        # Roll back the transaction if any error occurs
        db.session.rollback()
        return jsonify({'message': 'An error has occurred, please submit again'}), 400

    flash('Comment added!', 'success')
    return jsonify({ "result": comment.to_dict() })

def check_game(user_id: int, post_id: int, content: str):
    post = db.session.execute(db.select(Post).filter_by(id=post_id)).scalar_one_or_none()
    _answer = post.content
    if (_answer == content):
        # update post status to completed
        post.status = True
        flash('Post status updated!', 'success')

        #TODO add_score to user, currently just add 1
        add_score(user_id, score = 1)

# TODO add_like
# @app.route('/add_like', methods=['POST'])

# add_score, increment score to current user if existed, else create new score
# @param user_id which user to be updated
# @param score score to be incremented
# return {Score} object
def add_score(user_id: int, score: int):
    _user_id = user_id
    _score = score

    # fetch current score of user
    score = db.session.execute(db.select(Score).filter_by(user_id=_user_id)).scalar_one_or_none()
    # create score if not existed
    if not score:    
        score = Score(user_id=_user_id, score=int(_score))
        db.session.add(score)
    else:
        score.score += int(_score)

    flash('Score added!', 'success')
    return score

# event listener for score update
# send top10 result to frontend when score has an update
def after_update_listener(mapper, connection, target):
    # state.get_history() can be used to get the history of attributes
    # It returns a History object with three lists: added, unchanged, and deleted
    state = db.inspect(target)
    if state.attrs.score.history.has_changes():
        scores = db.session.query(Score.user_id.label('user_id'), Score.score.label('score'), User.username.label('username')).join(User, Score.user_id == User.id).order_by(Score.score.desc()).paginate(page=1, per_page=10, error_out=False)
        
        result = [{'user_id': score.user_id, 'score': score.score, 'user_name': score.username} for score in scores.items]
        # Emit the top 10 scores
        socketio.emit('score_update', result)
# Attach the listener to the Score class, listening to 'after_update'
event.listen(Score, 'after_update', after_update_listener)

# get_scores, get scores of all users
# @param page_no page number
# @param page_size page size
# @param order: asc or desc
@app.route('/get_scores', methods=['GET'])
@login_required
def get_scores():
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'error': 'Unauthorized'}), 403
    page_no = request.args.get("page_no", 1)
    page_size = request.args.get("page_size", 10)
    order = request.args.get("order", 'desc')   
    order_method = getattr(Score.score, order)

    scores = db.session.query(Score.user_id.label('user_id'), Score.score.label('score'), User.username.label('username')).join(User, Score.user_id == User.id).order_by(order_method()).paginate(page=int(page_no), per_page=int(page_size), error_out=False)

    # transform score models to list of dicts
    # result = [score.to_dict() for score in scores.items]
    result = [{'user_id': score.user_id, 'score': score.score, 'user_name': score.username} for score in scores.items]

    flash('Score fetched!', 'success')
    # return result as JSON
    return jsonify({"result": result, "total": scores.total})

# This error is sent when a user tries to bypass routes requiring @login_required while being 'un-logged in'.
@app.errorhandler(Unauthorized)
def unauthorized(error):
    flash("You need to log in to access this page.", "error")
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
