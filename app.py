from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_session import Session
from flask_socketio import SocketIO
from sqlalchemy import func, event
from werkzeug.security import generate_password_hash
from database.models import db, User, Score
from werkzeug.exceptions import Unauthorized
from database.models import db, Wordlewords
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
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
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    if current_user.is_authenticated:
        return render_template('home.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/wordleCreation')
@login_required
def wordleCreation():
    if current_user.is_authenticated:
        return render_template('wordleCreation.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/generate_word', methods=['GET'])
def generate_word():
    random_word = Wordlewords.query.order_by(func.random()).first()
    if random_word:
        return jsonify({'word': random_word.word})
    else:
        return jsonify({'error': 'No words found'})

# add_score, increment score to current user if existed, else create new score
# @param user_id which user to be updated
# @param score score to be incremented
@app.route('/add_score', methods=['POST'])
def add_score():
    _user_id = request.form["user_id"]
    _score = request.form["score"]

    # fetch current score of user
    score = db.session.execute(db.select(Score).filter_by(user_id=_user_id)).scalar_one_or_none()
    # create score if not existed
    if not score:    
        score = Score(user_id=_user_id, score=int(_score))
        db.session.add(score)
    else:
        score.score += int(_score)
    db.session.commit()

    flash('Score added!', 'success')
    return redirect(url_for('index'))

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
def get_scores():
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


# checking the word
@app.route('/check_word', methods=['POST'])
def get_worddb():
    Userword = request.form['word'].lower() #get the word from the form
    CWord = Wordlewords.query.filter_by(word=Userword) #compare word from wordlewords
    if CWord:
        return jsonify({'valid': True, 'message': 'Word is valid!'})
    else:
        return jsonify({'valid': False, 'message': 'Word is not valid!'})



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# This error is sent when a user tries to bypass routes requiring @login_required while being 'un-logged in'.
@app.errorhandler(Unauthorized)
def unauthorized(error):
    flash("You need to log in to access this page.", "error")
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
