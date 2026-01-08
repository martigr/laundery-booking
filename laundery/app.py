from flask import Flask, render_template, request, redirect, abort, session
import sqlite3
from datetime import date, timedelta
from calendar import monthrange
from collections import defaultdict
from werkzeug.security import generate_password_hash, check_password_hash
import functools

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this"
DB = "reservations.db"

SLOTS = ["Vormittag", "Nachmittag", "Abend"]

def db():
    return sqlite3.connect(DB)

def init_db():
    with db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS apartments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            apartment_id INTEGER NOT NULL,
            FOREIGN KEY (apartment_id) REFERENCES apartments(id)
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            slot TEXT,
            apartment_id INTEGER NOT NULL,
            FOREIGN KEY (apartment_id) REFERENCES apartments(id)
        )
        """)
        con.commit()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('user_id'):
            return redirect('/login')
        return view(**kwargs)
    return wrapped_view

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    with db() as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            "SELECT u.*, a.name AS apartment_name FROM users u JOIN apartments a ON u.apartment_id = a.id WHERE u.id = ?",
            (user_id,)
        )
        return cur.fetchone()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        with db() as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cur.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        
        if not check_password_hash(user['password'], old_password):
            return render_template('profile.html', user=user, error='Old password incorrect')
        
        if len(new_password) < 6:
            return render_template('profile.html', user=user, error='Password must be at least 6 characters')
        
        hashed = generate_password_hash(new_password)
        with db() as con:
            con.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user['id']))
            con.commit()
        
        return render_template('profile.html', user=user, success='Password changed successfully')
    
    return render_template('profile.html', user=user)

def month_bounds(y, m):
    start = date(y, m, 1)
    end = date(y, m, monthrange(y, m)[1])
    return start, end

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    today = date.today()

    # --- Monat aus Query ---
    month_str = request.args.get("month")
    if month_str:
        y, m = map(int, month_str.split("-"))
        current = date(y, m, 1)
    else:
        current = date(today.year, today.month, 1)

    prev_month = (current.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1).strftime("%Y-%m")

    if request.method == "POST":
        day = request.form["day"]
        slots_str = request.form.get("slot", "")
        slots_selected = [s.strip() for s in slots_str.split(",") if s.strip()]

        if not slots_selected or not day:
            abort(400)

        with db() as con:
            cur = con.cursor()
            for slot in slots_selected:
                cur.execute("""
                    SELECT * FROM reservations
                    WHERE day=? AND slot=?
                """, (day, slot))
                if cur.fetchone() is None:
                    cur.execute("""
                        INSERT INTO reservations (day, slot, apartment_id)
                        VALUES (?, ?, ?)
                    """, (day, slot, user['apartment_id']))
            con.commit()

        return redirect(f"/?month={current.strftime('%Y-%m')}")

    # --- Daten für Monat ---
    start, end = month_bounds(current.year, current.month)
    days_in_month = monthrange(current.year, current.month)[1]
    first_weekday = start.weekday()  # Mo=0

    with db() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT r.id, r.day, r.slot, r.apartment_id, a.name
            FROM reservations r
            JOIN apartments a ON r.apartment_id = a.id
            WHERE r.day BETWEEN ? AND ?
        """, (start.isoformat(), end.isoformat()))

        grid = defaultdict(dict)
        for rid, day, slot, apt_id, apt_name in cur.fetchall():
            grid[day][slot] = {
                "id": rid,
                "apartment_id": apt_id,
                "apartment_name": apt_name
            }

    return render_template(
        "index.html",
        current=current,
        prev_month=prev_month,
        next_month=next_month,
        first_weekday=first_weekday,
        days_in_month=days_in_month,
        slots=SLOTS,
        grid=grid,
        today=today.isoformat(),
        user=user
    )

@app.route("/delete/<int:rid>", methods=["POST"])
@login_required
def delete(rid):
    user = get_current_user()
    if not user:
        return redirect('/login')

    with db() as con:
        con.execute("""
            DELETE FROM reservations
            WHERE id=? AND apartment_id=?
        """, (rid, user['apartment_id']))
        con.commit()

    return redirect(request.referrer or "/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
