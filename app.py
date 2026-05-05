from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DB CONNECTION =================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",   
    database="assignment_tracker"
)

cursor = conn.cursor(dictionary=True)

# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()

        return redirect('/login')

    return render_template('register.html')

# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            return redirect('/')
        else:
            return "Invalid Credentials"

    return render_template('login.html')

# ================= HOME =================
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor.execute("SELECT * FROM tasks WHERE user_id=%s", (user_id,))
    tasks = cursor.fetchall()

    return render_template('index.html', tasks=tasks)

# ================= FILTER =================
@app.route('/filter/<status>')
def filter_tasks(status):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor.execute("SELECT * FROM tasks WHERE user_id=%s AND status=%s", (user_id, status))
    tasks = cursor.fetchall()

    return render_template('index.html', tasks=tasks)

# ================= ADD =================
@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    title = request.form['title']
    description = request.form['description']
    deadline = request.form['deadline']
    status = request.form['status']

    cursor.execute("""
        INSERT INTO tasks (user_id, title, description, deadline, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, title, description, deadline, status))

    conn.commit()

    return redirect('/')

# ================= DELETE =================
@app.route('/delete/<int:id>')
def delete_task(id):
    cursor.execute("DELETE FROM tasks WHERE id=%s", (id,))
    conn.commit()
    return redirect('/')

# ================= UPDATE =================
@app.route('/update/<int:id>', methods=['POST'])
def update_task(id):
    title = request.form['title']
    description = request.form['description']
    deadline = request.form['deadline']
    status = request.form['status']

    cursor.execute("""
        UPDATE tasks
        SET title=%s, description=%s, deadline=%s, status=%s
        WHERE id=%s
    """, (title, description, deadline, status, id))

    conn.commit()

    return redirect('/')

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)