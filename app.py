from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Veritabanı URI'yi MySQL için güncelledik
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/exam'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Question(db.Model):
    __tablename__ = 'questions'  
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

class User(db.Model):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    highest_score = db.Column(db.Integer, default=0)

class UserScore(db.Model):
    __tablename__ = 'user_scores'  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/', methods=['GET', 'POST'])
def exam():
    questions = Question.query.all()
    message = None
    highest_score = None

    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer == question.correct_answer:
                score += 20  

        if score > user.highest_score:
            user.highest_score = score
        
        db.session.add(UserScore(user_id=user.id, score=score))
        db.session.commit()

        highest_score = user.highest_score
        message = f"Tebrikler, {username}! Puanın: {score}. En yüksek puan: {user.highest_score}."

        return render_template('index.html', questions=questions, message=message, highest_score=highest_score)

    return render_template('index.html', questions=questions, message=message, highest_score=highest_score)

if __name__ == '__main__':
    app.run(debug=True)
