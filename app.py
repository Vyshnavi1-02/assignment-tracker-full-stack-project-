from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Database (works locally + Render)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------- MODELS --------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    status = db.Column(db.String(50), default='Pending')
    priority = db.Column(db.String(20))
    due_date = db.Column(db.String(20))
    user_id = db.Column(db.Integer)

with app.app_context():
    db.create_all()

# -------- AUTH --------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            session['user_id'] = user.id
            return redirect('/')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')


# -------- TASKS --------

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    tasks = Task.query.filter_by(user_id=session['user_id']).all()

    total = len(tasks)
    completed = len([t for t in tasks if t.status == 'Completed'])
    pending = total - completed

    return render_template(
        'index.html',
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending
    )


@app.route('/add', methods=['POST'])
def add():
    task = Task(
        name=request.form['task'],
        priority=request.form['priority'],
        due_date=request.form['due_date'],
        user_id=session['user_id']
    )
    db.session.add(task)
    db.session.commit()
    return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')


@app.route('/complete/<int:id>')
def complete(id):
    task = Task.query.get_or_404(id)
    task.status = 'Completed'
    db.session.commit()
    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)

    if request.method == 'POST':
        task.name = request.form['task']
        task.priority = request.form['priority']
        task.due_date = request.form['due_date']
        db.session.commit()
        return redirect('/')

    return render_template('edit.html', task=task)


if __name__ == '__main__':
    app.run(debug=True)