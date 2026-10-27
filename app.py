import sqlite3
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Import our custom helper functions
from helpers import get_user_insights

# Configure application
app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# --- Database Connection ---
def get_db_connection():
    conn = sqlite3.connect('thrive.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Login Required Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# --- User Authentication Routes ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return render_template("error.html", message="Please fill out all fields.")
        if password != confirmation:
            return render_template("error.html", message="Passwords do not match.")

        conn = get_db_connection()
        db = conn.cursor()
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        if len(rows) > 0:
            conn.close()
            return render_template("error.html", message="Username already exists.")

        hash_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash_password))
        conn.commit()
        conn.close()
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username or not password:
            return render_template("error.html", message="Must provide username and password.")

        conn = get_db_connection()
        db = conn.cursor()
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            conn.close()
            return render_template("error.html", message="Invalid username and/or password.")

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        conn.close()
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- Main Application Routes ---
@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    insight_message = get_user_insights(user_id)
    
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ? AND status = 'todo' ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()

    return render_template("index.html", username=session["username"], insight=insight_message, tasks=tasks)

@app.route("/planner", methods=["GET", "POST"])
@login_required
def planner():
    user_id = session["user_id"]
    conn = get_db_connection()

    if request.method == "POST":
        task_content = request.form.get("task")
        if task_content:
            conn.execute("INSERT INTO tasks (user_id, content, status) VALUES (?, ?, 'todo')", (user_id, task_content))
            conn.commit()
    
    # Corrected query to only show today's completed tasks
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND (status = 'todo' OR (status = 'done' AND strftime('%Y-%m-%d', created_at, 'localtime') = strftime('%Y-%m-%d', 'now', 'localtime'))) ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    
    conn.close()
    return render_template("planner.html", tasks=tasks)

@app.route("/update_task/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    user_id = session["user_id"]
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET status = 'done' WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()
    return redirect("/planner")

@app.route("/mood", methods=["GET", "POST"])
@login_required
def mood():
    user_id = session["user_id"]
    conn = get_db_connection()

    if request.method == "POST":
        mood_value = request.form.get("mood")
        note = request.form.get("note")

        if mood_value:
            conn.execute("INSERT INTO moods (user_id, mood, note) VALUES (?, ?, ?)", (user_id, mood_value, note))
            conn.commit()
            conn.close()
            # Redirect to the mood page to see the new entry
            return redirect("/mood")
    
    # Fetch all journal entries for this user
    journal_entries = conn.execute(
        "SELECT id, mood, note, logged_at FROM moods WHERE user_id = ? AND note IS NOT NULL AND note != '' ORDER BY logged_at DESC",
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    return render_template("mood.html", entries=journal_entries)

@app.route("/calm")
@login_required
def calm():
    return render_template("calm.html")

@app.route("/delete_reflection/<int:entry_id>", methods=["POST"])
@login_required
def delete_reflection(entry_id):
    user_id = session["user_id"]
    conn = get_db_connection()
    
    conn.execute("DELETE FROM moods WHERE id = ? AND user_id = ?", (entry_id, user_id))
    conn.commit()
    conn.close()
    
    return redirect("/mood")