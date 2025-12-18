import os
from flask import Flask, request, redirect, session, render_template
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# ------------------ MongoDB ------------------
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["event_system"]

users_col = db["users"]
events_col = db["events"]
resources_col = db["resources"]
allocations_col = db["allocations"]

# ------------------ Auth Decorator ------------------
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrap

# ------------------ Authentication ------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users_col.insert_one({
            "username": request.form["username"],
            "password": generate_password_hash(request.form["password"])
        })
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = users_col.find_one({"username": request.form["username"]})
        if user and check_password_hash(user["password"], request.form["password"]):
            session["user"] = user["username"]
            return redirect("/events")
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    if "user" in session:
        return redirect("/events")
    return render_template("index.html")

# ------------------ Events ------------------
@app.route("/events", methods=["GET", "POST"])
@login_required
def events():
    if request.method == "POST":
        start = datetime.fromisoformat(request.form["start"])
        end = datetime.fromisoformat(request.form["end"])
        if start >= end:
            return "Invalid time range"

        events_col.insert_one({
            "title": request.form["title"],
            "start": start,
            "end": end,
            "description": request.form["desc"]
        })

    events = list(events_col.find())
    return render_template("events.html", events=events)

# ------------------ Resources ------------------
@app.route("/resources", methods=["GET", "POST"])
@login_required
def resources():
    if request.method == "POST":
        resources_col.insert_one({
            "name": request.form["name"],
            "type": request.form["type"]
        })

    resources = list(resources_col.find())
    return render_template("resources.html", resources=resources)

# ------------------ Conflict Detection ------------------
def has_conflict(resource_id, start, end):
    for a in allocations_col.find({"resource_id": resource_id}):
        event = events_col.find_one({"_id": a["event_id"]})
        if not (end <= event["start"] or start >= event["end"]):
            return True
    return False

# ------------------ Allocate ------------------
@app.route("/allocate", methods=["GET", "POST"])
@login_required
def allocate():
    events = list(events_col.find())
    resources = list(resources_col.find())

    if request.method == "POST":
        event = events_col.find_one({"_id": ObjectId(request.form["event"])})
        resource_id = ObjectId(request.form["resource"])

        if has_conflict(resource_id, event["start"], event["end"]):
            return "Conflict: Resource already booked"

        allocations_col.insert_one({
            "event_id": event["_id"],
            "resource_id": resource_id
        })

    return render_template("allocate.html", events=events, resources=resources)

# ------------------ Report ------------------
@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    report_data = []

    if request.method == "POST":
        start = datetime.fromisoformat(request.form["start"])
        end = datetime.fromisoformat(request.form["end"])

        for r in resources_col.find():
            hours = 0
            upcoming = 0

            for a in allocations_col.find({"resource_id": r["_id"]}):
                event = events_col.find_one({"_id": a["event_id"]})
                if event["end"] > start and event["start"] < end:
                    hours += (event["end"] - event["start"]).seconds / 3600
                if event["start"] > datetime.now():
                    upcoming += 1

            report_data.append((r["name"], hours, upcoming))

    return render_template("report.html", report=report_data)

if __name__ == "__main__":
    app.run(debug=True)
