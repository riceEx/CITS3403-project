from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_session import Session
from flask_socketio import SocketIO
from sqlalchemy import func, event
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import Unauthorized
from database.models import db, User, Score, Post, Comment, Image
from datetime import datetime
import sqlite3
import random
import traceback
import base64
import os
import mimetypes
from io import BytesIO

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOADED_IMAGES_DEST'] = 'static/post_images'

Session(app)
socketio = SocketIO(app)
db.init_app(app)
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    # Query all posts from the database
    posts = Post.query.all()
    # Render the index.html template and pass the posts to it
    return render_template('index.html', user=current_user, posts=posts)



@app.route('/createpost')
def createpost():
    return render_template('createpost.html', user=current_user)
 
@app.route('/leaderboard')
def leaderboard():
    # Fetch top 10 scores in descending order
    top_scores = Score.query.order_by(Score.score.desc()).limit(10).all()
    
    # Fetch corresponding user details
    data = []
    rank = 1
    for score in top_scores:
        user = User.query.get(score.user_id)
        data.append({"rank": rank, "username": user.username, "score": score.score})
        rank += 1

    return render_template('leaderboard.html', data=data, current_user=current_user)


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

#specific for leaderboard so it doesnt take you to index if you logout
@app.route('/loginL', methods=['POST'])
def loginL():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for('leaderboard'))
    else:
        flash('Incorrect username or password', 'error')
        return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


#TODO for testing purposes, remove in production
@app.route('/test')
def test():
    return render_template('test.html', user=current_user)

# add_post, create a new post
# @param user_id which user created the post
# @param content post content
# @param hint hint to the guessing game
# @param language, source language of the hint, default is english
@app.route('/add_post', methods=['POST'])
@login_required
def add_post():
    _user_id = current_user.id
    _content = request.form["content"]
    _hint = request.form["hint"]
    #if user_id, content or hint is not provided, return error
    if not _user_id or not _content or not _hint:
        return jsonify({'message': 'Missing parameters'}), 400
    _language = request.form["language"] or 'en'
    _images = request.form.getlist("images[]")  # getlist to handle multiple files

    post = Post(user_id=_user_id, content=_content, hint=_hint, language=_language)
    db.session.add(post)
    db.session.flush()  # Flush to obtain the post ID for image foreign key
    for index, image_str in enumerate(_images):
        if image_str:
            header, encoded = image_str.split(',', 1)
            # Extract MIME type
            mime_type = header.split(';')[0].split(':')[1]
            # Use mimetypes to get the extension
            extension = mimetypes.guess_extension(mime_type)
            # Decode the image
            image_bytes = base64.b64decode(encoded)
            filename = secure_filename(f"{post.id}-{index}{extension}")
            file_path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)

            # Save the image to a file
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            # Save the image path to the database
            new_image = Image(post_id=post.id, url=filename)
            db.session.add(new_image)
    db.session.commit()

    flash('Post added!', 'success')
    return jsonify({ "result": post.to_dict() })

# get_posts, get post based on filters
# @param word_length, length of the word
# @param language, source language of the hint, default is english
# @param hint, hint to the guessing game
# @param status, status of the post
# @param page_no, page number
# @param page_size, number of posts per page
# @param order, order of the posts, default is descending order
@app.route('/get_posts', methods=['GET'])
@login_required
def get_posts():
    word_length = request.args.get('word_length', type=int)
    language = request.args.get('language', type=str)
    hint = request.args.get('hint', type=str)
    status = request.args.get('status') == 'true'
    page_no = request.args.get('page_no', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    order = request.args.get("order", 'desc')   
    order_method = getattr(Post.datetime, order)
    
    # Base query
    query = db.session.query(Post)

    # Filters
    if word_length:
        query = query.filter(func.length(Post.content) == word_length)
    if language:
        query = query.filter_by(language=language)
    if hint:
        query = query.filter(Post.hint.like(f"%{hint}%"))
    if status:
        query = query.filter_by(status=status)
    if order:
        query = query.order_by(order_method())

    # Pagination
    postQuerys = query.paginate(page=page_no, per_page=page_size, error_out=False)
    posts = [post.to_dict() for post in postQuerys.items]

    flash('Posts get!', 'success')
    # Return results
    return jsonify({
        'posts': posts,
        'total': postQuerys.total
    })

# update_post, update an existing post
# @param post_id the ID of the post to update
# @param content new content for the post
# @param hint new hint for the guessing game
# @param language new source language of the hint
@app.route('/update_post/<int:post_id>', methods=['POST'])
@login_required
def update_post(post_id):
    _post = Post.query.get(post_id)
    if not _post:
        return jsonify({'message': 'Post not found'}), 404
    
    _content = request.form.get("content")
    _hint = request.form.get("hint")
    _language = request.form.get("language")

    if _content:
        _post.content = _content
    if _hint:
        _post.hint = _hint
    if _language:
        _post.language = _language

    db.session.commit()

    flash('Post updated!', 'success')
    return jsonify({ "result": _post.to_dict() })

# delete_post, delete an existing post
# @param post_id the ID of the post to delete
@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    _post = Post.query.get(post_id)
    if not _post:
        return jsonify({'message': 'Post not found'}), 404

    db.session.delete(_post)
    db.session.commit()

    flash('Post deleted!', 'success')
    return jsonify({'message': 'Post successfully deleted'})
    
# add_comment, create a comment to a post
# @param post_id which post the comment belongs to
# @param content post content
@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    _user_id = current_user.id
    _post_id = request.form["post_id"]
    _content = request.form["content"]
    #if user_id, content or hint is not provided, return error
    if not _user_id or not _content or not _post_id:
        return jsonify({'message': 'Missing parameters'}), 400

    try:
        # Begin a transaction of multiple operations
        db.session.close()
        with db.session.begin():
            comment = Comment(user_id=_user_id, post_id=_post_id, content=_content)
            db.session.add(comment)
            check_game(_user_id, _post_id, _content)
            db.session.commit()
    except Exception as e:
        traceback.print_exc()
        # Roll back the transaction if any error occurs
        db.session.rollback()
        return jsonify({'message': 'An error has occurred, please submit again'}), 400

    flash('Comment added!', 'success')
    return jsonify({ "result": comment.to_dict() })

def check_game(user_id: int, post_id: int, content: str):
    post = db.session.execute(db.select(Post).filter_by(id=post_id)).scalar_one_or_none()
    _answer = post.content
    if (_answer == content):
        # 1. basic points based on the length of the word
        # 2. if the post has not been completed before, double the points
        score = len(post.content)
        if (post.status == False):
            score *= 2
        # update post status to completed
        post.status = True

        flash('Post status updated!', 'success')
        add_score(user_id, score)

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
