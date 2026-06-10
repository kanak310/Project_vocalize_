import datetime

from flask import Flask , render_template , request , url_for , redirect , session

from flask_sqlalchemy import SQLAlchemy

from gtts import gTTS

text = "Hello, welcome to Vocalize! This is a text-to-speech conversion."

tts = gTTS(text=text)

tts.save("static/audio/output.mp3")

app = Flask(__name__)

app.secret_key = "vocalize_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///users.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)

    username = db.Column(db.String(100),nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(100), nullable=False)

class History(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    text = db.Column(db.Text)

    history_type = db.Column(db.String(20))

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:
            session['user_id'] = user.id

            return redirect(url_for('home'))
        
        else:
            return "Invalid Email or Password"

    return render_template('login.html')


@app.route('/tts', methods=['GET', 'POST'])
def tts():
    if request.method == 'POST':

        text = request.form.get('text')

        print("TEXT RECEIVED:", text)

        try:
            new_history = History(
            text=text,
            history_type="TTS",
            user_id=session['user_id']
)

            db.session.add(new_history)

            db.session.commit()

            print("DATA SAVED")

        except Exception as e:

            print("ERROR:", e)

    return render_template('tts.html')

@app.route('/stt', methods=['GET', 'POST'])
def stt():

    if request.method == 'POST':

        text = request.form.get('text')

        new_history = History(
        text=text,
        history_type="STT",
        user_id=session['user_id']
)

        db.session.add(new_history)

        db.session.commit()

        return "Saved"

    return render_template('stt.html')

@app.route('/history')
def history_page():

    all_items = History.query.filter_by(
    user_id=session['user_id']
).all()


    print(all_items)

    return render_template(
        'history.html',
        items=all_items
    )

@app.route('/clear_history')
def clear_history():

    History.query.delete()

    db.session.commit()

    return redirect(url_for('history_page'))

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)


  
