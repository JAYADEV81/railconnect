from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from pathlib import Path
from datetime import date
from functools import wraps

app = Flask(__name__)
app.secret_key = "railconnect-demo-change-this"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "railconnect.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS trains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_number TEXT NOT NULL UNIQUE,
            train_name TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            departure TEXT NOT NULL,
            arrival TEXT NOT NULL,
            duration TEXT NOT NULL,
            fare REAL NOT NULL,
            seats INTEGER NOT NULL DEFAULT 60
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pnr TEXT NOT NULL UNIQUE,
            train_id INTEGER NOT NULL,
            journey_date TEXT NOT NULL,
            travel_class TEXT NOT NULL,
            passenger_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            seats INTEGER NOT NULL,
            total_fare REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Confirmed',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(train_id) REFERENCES trains(id)
        );
        """)
        count = db.execute("SELECT COUNT(*) FROM trains").fetchone()[0]
        if count == 0:
            sample = [
                ("12675","Kovai Express","Chennai Central","Coimbatore","06:10","13:50","7h 40m",475,120),
                ("12608","Lalbagh Express","Chennai Central","Bengaluru City","15:30","21:00","5h 30m",390,90),
                ("12671","Nilagiri Express","Chennai Central","Mettupalayam","21:05","06:15","9h 10m",620,75),
                ("12028","Shatabdi Express","Chennai Central","Bengaluru City","06:00","10:50","4h 50m",850,60),
                ("16127","Guruvayur Express","Chennai Egmore","Coimbatore","07:40","16:20","8h 40m",430,80),
                ("12640","Brindavan Express","Bengaluru City","Chennai Central","14:50","20:35","5h 45m",410,95),
                ("22637","West Coast Express","Chennai Central","Coimbatore","13:15","21:00","7h 45m",520,70),
                ("12609","Mysuru Express","Chennai Central","Mysuru","23:30","08:50","9h 20m",560,65),
            ]
            db.executemany("""INSERT INTO trains
                (train_number,train_name,source,destination,departure,arrival,duration,fare,seats)
                VALUES (?,?,?,?,?,?,?,?,?)""", sample)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please sign in to access the demo admin dashboard.", "error")
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    with get_db() as db:
        featured = db.execute("SELECT * FROM trains ORDER BY id LIMIT 3").fetchall()
    return render_template("index.html", featured=featured, today=date.today().isoformat())

@app.route("/trains")
def trains():
    source = request.args.get("from", "").strip()
    destination = request.args.get("to", "").strip()
    journey_date = request.args.get("date", "").strip()
    travel_class = request.args.get("class", "SL").strip()
    query = "SELECT * FROM trains WHERE 1=1"
    params = []
    if source:
        query += " AND source LIKE ?"
        params.append(f"%{source}%")
    if destination:
        query += " AND destination LIKE ?"
        params.append(f"%{destination}%")
    with get_db() as db:
        results = db.execute(query + " ORDER BY departure", params).fetchall()
    return render_template("trains.html", trains=results, source=source, destination=destination,
                           journey_date=journey_date, travel_class=travel_class)

@app.route("/booking/<int:train_id>", methods=["GET", "POST"])
def booking(train_id):
    with get_db() as db:
        train = db.execute("SELECT * FROM trains WHERE id=?", (train_id,)).fetchone()
    if not train:
        flash("That train could not be found.", "error")
        return redirect(url_for("trains"))
    journey_date = request.args.get("date", date.today().isoformat())
    travel_class = request.args.get("class", "SL")
    if request.method == "POST":
        name = request.form.get("passenger_name", "").strip()
        age_raw = request.form.get("age", "")
        gender = request.form.get("gender", "")
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        travel_date = request.form.get("journey_date", "")
        travel_class = request.form.get("travel_class", "SL")
        seats_raw = request.form.get("seats", "1")
        errors = []
        try:
            age = int(age_raw)
            seats = int(seats_raw)
            if not 1 <= age <= 120: errors.append("Enter an age between 1 and 120.")
            if not 1 <= seats <= 6: errors.append("You can book 1 to 6 passengers per demo booking.")
        except ValueError:
            age, seats = 0, 0
            errors.append("Enter a valid age and passenger count.")
        if not name or not email or not phone or not gender or not travel_date:
            errors.append("Please complete all required fields.")
        if travel_date < date.today().isoformat():
            errors.append("Journey date cannot be in the past.")
        if len(phone) != 10 or not phone.isdigit():
            errors.append("Enter a valid 10-digit Indian mobile number.")
        if errors:
            for error in errors: flash(error, "error")
            return render_template("booking.html", train=train, journey_date=travel_date,
                                   travel_class=travel_class, form=request.form, today=date.today().isoformat())
        fare_multiplier = {"SL": 1, "3A": 2.1, "2A": 3.0, "1A": 4.5, "CC": 1.6}.get(travel_class, 1)
        total_fare = round(train["fare"] * fare_multiplier * seats, 2)
        import secrets
        pnr = str(secrets.randbelow(9000000000) + 1000000000)
        with get_db() as db:
            db.execute("""INSERT INTO bookings
                (pnr,train_id,journey_date,travel_class,passenger_name,age,gender,email,phone,seats,total_fare)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (pnr, train_id, travel_date, travel_class, name, age, gender, email, phone, seats, total_fare))
        return redirect(url_for("confirmation", pnr=pnr))
    return render_template("booking.html", train=train, journey_date=journey_date,
                           travel_class=travel_class, form={}, today=date.today().isoformat())

@app.route("/confirmation/<pnr>")
def confirmation(pnr):
    with get_db() as db:
        booking = db.execute("""SELECT b.*, t.train_number, t.train_name, t.source, t.destination,
            t.departure, t.arrival FROM bookings b JOIN trains t ON b.train_id=t.id WHERE b.pnr=?""",
            (pnr,)).fetchone()
    if not booking:
        flash("Booking not found.", "error")
        return redirect(url_for("my_bookings"))
    return render_template("confirmation.html", booking=booking)

@app.route("/my-bookings", methods=["GET", "POST"])
def my_bookings():
    bookings = []
    searched = False
    if request.method == "POST":
        pnr = request.form.get("pnr", "").strip()
        phone = request.form.get("phone", "").strip()
        with get_db() as db:
            bookings = db.execute("""SELECT b.*, t.train_number, t.train_name, t.source, t.destination,
                t.departure, t.arrival FROM bookings b JOIN trains t ON b.train_id=t.id
                WHERE b.pnr=? AND b.phone=? ORDER BY b.created_at DESC""", (pnr, phone)).fetchall()
        searched = True
        if not bookings:
            flash("No booking matched that PNR and phone number.", "error")
    return render_template("my_bookings.html", bookings=bookings, searched=searched)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        if name and email and subject and message:
            flash("Thank you. This demo form has been validated; no email was sent.", "success")
            return redirect(url_for("contact"))
        flash("Please fill in all required fields.", "error")
    return render_template("contact.html")

@app.route("/admin", methods=["GET"])
@admin_required
def admin():
    with get_db() as db:
        total_trains = db.execute("SELECT COUNT(*) FROM trains").fetchone()[0]
        total_bookings = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        revenue = db.execute("SELECT COALESCE(SUM(total_fare),0) FROM bookings WHERE status='Confirmed'").fetchone()[0]
        bookings = db.execute("""SELECT b.*, t.train_number, t.train_name, t.source, t.destination
            FROM bookings b JOIN trains t ON b.train_id=t.id ORDER BY b.created_at DESC""").fetchall()
        trains_list = db.execute("SELECT * FROM trains ORDER BY train_number").fetchall()
    return render_template("admin.html", total_trains=total_trains, total_bookings=total_bookings,
                           revenue=revenue, bookings=bookings, trains=trains_list)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "admin" and password == "rail123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        flash("Incorrect demo username or password.", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin/cancel/<int:booking_id>", methods=["POST"])
@admin_required
def cancel_booking(booking_id):
    with get_db() as db:
        db.execute("UPDATE bookings SET status='Cancelled' WHERE id=?", (booking_id,))
    flash("Booking status updated.", "success")
    return redirect(url_for("admin"))

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

init_db()

if __name__ == "__main__":
    app.run(debug=True)
