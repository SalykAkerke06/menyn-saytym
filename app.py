from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'kaznpu_secret_key'


# Деректер қорын дайындау
def init_db():
    conn = sqlite3.connect('student_system.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY,
                        fullname TEXT, email TEXT, age INTEGER,
                        phone TEXT, password TEXT, gender TEXT, course TEXT)''')
    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('student_system.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        sid = random.randint(100000, 999999)
        data = (sid, request.form['fullname'], request.form['email'],
                request.form['age'], request.form['phone'],
                request.form['password'], request.form['gender'], request.form['course'])

        conn = get_db_connection()
        conn.execute("INSERT INTO students VALUES (?,?,?,?,?,?,?,?)", data)
        conn.commit()
        conn.close()
        flash(f"Тіркелу сәтті! Сіздің ID: {sid}", "success")
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        sid = request.form['id']
        pwd = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM students WHERE id=? AND password=?", (sid, pwd)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        flash("ID немесе құпиясөз қате!", "danger")
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM students WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('dashboard.html', user=user, section='home')


@app.route('/dashboard/card')
def student_card():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM students WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('dashboard.html', user=user, section='card')


@app.route('/dashboard/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute("UPDATE students SET fullname=?, email=? WHERE id=?",
                     (request.form['fullname'], request.form['email'], session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('student_card'))
    user = conn.execute("SELECT * FROM students WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('dashboard.html', user=user, section='edit')


@app.route('/dashboard/password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute("UPDATE students SET password=? WHERE id=?", (request.form['new_pass'], session['user_id']))
        conn.commit()
        conn.close()
        flash("Құпиясөз өзгертілді!", "success")
        return redirect(url_for('dashboard'))
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM students WHERE id=?", (session['user_id'],)).fetchone()
    return render_template('dashboard.html', user=user, section='password')


@app.route('/dashboard/delete', methods=['POST'])
def delete_account():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id=?", (session['user_id'],))
    conn.commit()
    conn.close()
    session.clear()
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
