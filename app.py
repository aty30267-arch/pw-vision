import os
import sqlite3
from functools import wraps
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-secret-in-production')
DB = os.path.join(os.path.dirname(__file__), 'pwvision.db')

COURSES = [
    {'id': 1, 'title': 'Complete Mathematics', 'teacher': 'PW Vision Faculty', 'tag': 'POPULAR', 'description': 'Concepts, practice and revision in one structured course.'},
    {'id': 2, 'title': 'Physics Foundation', 'teacher': 'PW Vision Faculty', 'tag': 'NEW', 'description': 'Build strong fundamentals with guided lessons.'},
    {'id': 3, 'title': 'Chemistry Masterclass', 'teacher': 'PW Vision Faculty', 'tag': 'TRENDING', 'description': 'Learn chemistry through concepts, examples and tests.'},
    {'id': 4, 'title': 'Biology Complete Course', 'teacher': 'PW Vision Faculty', 'tag': 'POPULAR', 'description': 'A complete biology learning path with revision.'}
]


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()
    con.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)')
    con.execute('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, progress INTEGER DEFAULT 0, UNIQUE(user_id, course_id))')
    con.execute('CREATE TABLE IF NOT EXISTS test_results (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, test_name TEXT NOT NULL, score INTEGER NOT NULL, total INTEGER NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    con.commit(); con.close()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'Login required'}), 401
        return fn(*args, **kwargs)
    return wrapper


@app.get('/')
def home():
    return render_template('index.html', user=session.get('user'))


@app.post('/api/register')
def register():
    data = request.get_json(silent=True) or request.form
    name, email, password = data.get('name','').strip(), data.get('email','').strip().lower(), data.get('password','')
    if not name or not email or len(password) < 6:
        return jsonify({'error': 'Name, valid email and 6+ character password are required'}), 400
    con = db()
    try:
        cur = con.execute('INSERT INTO users(name,email,password) VALUES(?,?,?)', (name,email,generate_password_hash(password)))
        con.commit(); uid = cur.lastrowid
    except sqlite3.IntegrityError:
        con.close(); return jsonify({'error': 'Email already registered'}), 409
    con.close(); session['user_id'] = uid; session['user'] = {'id': uid, 'name': name, 'email': email}
    return jsonify({'message':'Account created','user':session['user']}), 201


@app.post('/api/login')
def login():
    data = request.get_json(silent=True) or request.form
    email, password = data.get('email','').strip().lower(), data.get('password','')
    con = db(); user = con.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone(); con.close()
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error':'Invalid email or password'}), 401
    session['user_id'] = user['id']; session['user'] = {'id': user['id'], 'name': user['name'], 'email': user['email']}
    return jsonify({'message':'Login successful','user':session['user']})


@app.post('/api/logout')
def logout():
    session.clear(); return jsonify({'message':'Logged out'})


@app.get('/api/me')
def me():
    if not session.get('user_id'): return jsonify({'authenticated': False})
    return jsonify({'authenticated': True, 'user': session['user']})


@app.get('/api/courses')
def courses():
    return jsonify(COURSES)


@app.post('/api/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    if not any(c['id'] == course_id for c in COURSES): return jsonify({'error':'Course not found'}), 404
    con=db(); con.execute('INSERT OR IGNORE INTO enrollments(user_id,course_id) VALUES(?,?)',(session['user_id'],course_id)); con.commit(); con.close()
    return jsonify({'message':'Enrolled successfully'})


@app.get('/api/dashboard')
@login_required
def dashboard():
    con=db(); rows=con.execute('SELECT course_id, progress FROM enrollments WHERE user_id=?',(session['user_id'],)).fetchall(); results=con.execute('SELECT test_name,score,total,created_at FROM test_results WHERE user_id=? ORDER BY id DESC LIMIT 10',(session['user_id'],)).fetchall(); con.close()
    enrolled=[dict(next(c for c in COURSES if c['id']==r['course_id']), progress=r['progress']) for r in rows]
    return jsonify({'user':session['user'],'courses':enrolled,'tests':[dict(r) for r in results]})


@app.patch('/api/progress/<int:course_id>')
@login_required
def progress(course_id):
    value=int((request.get_json(silent=True) or {}).get('progress',0)); value=max(0,min(100,value)); con=db(); cur=con.execute('UPDATE enrollments SET progress=? WHERE user_id=? AND course_id=?',(value,session['user_id'],course_id)); con.commit(); con.close()
    if cur.rowcount == 0: return jsonify({'error':'Not enrolled'}), 404
    return jsonify({'course_id':course_id,'progress':value})


@app.post('/api/tests')
@login_required
def save_test():
    data=request.get_json(silent=True) or {}; name=data.get('test_name','Practice Test'); score=int(data.get('score',0)); total=max(1,int(data.get('total',10))); con=db(); con.execute('INSERT INTO test_results(user_id,test_name,score,total) VALUES(?,?,?,?)',(session['user_id'],name,score,total)); con.commit(); con.close(); return jsonify({'message':'Result saved'})


@app.get('/health')
def health(): return jsonify({'status':'ok','service':'PW Vision API'})


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_DEBUG') == '1')
