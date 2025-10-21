from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Booking, Ticket, Event, User, Category, Venue, Comment
from .forms import BookingForm
from datetime import datetime
from datetime import datetime
import os, uuid, json

from website.forms import EventForm

from . import db
from .models import Event, Venue, Category, Ticket, Booking, Comment, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    events = db.session.scalars(
        db.select(Event).order_by(Event.date_time.asc())
    ).all()
    return render_template("Index.html", events=events)

@main_bp.route('/search')
def search():
    term = (request.args.get('search') or "").strip()
    if term:
        query = f"%{term}%"
        events = db.session.scalars(
            db.select(Event).where(Event.description.like(query))
        ).all()
        return render_template('index.html', events=events)
    return redirect(url_for('main.index'))

@main_bp.route('/my-bookings')
@login_required
def my_bookings():
    bookings = db.session.scalars(
        db.select(Booking).where(Booking.user_id == current_user.id).order_by(Booking.id.desc())
    ).all()
    return render_template('bookings.html', bookings=bookings)

@main_bp.route("/events", methods=["GET"])
@login_required
def events():
    items = db.session.scalars(
        db.select(Event).order_by(Event.date_time.desc())
    ).all()
    return render_template("all_events.html", events=items)

@main_bp.route("/venues", methods=["GET", "POST"])
@login_required
def venues():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        location = (request.form.get("location") or "").strip()
        capacity = int(request.form.get("capacity") or 0)
        if not name or not location or capacity <= 0:
            flash("Please fill all fields correctly.", "warning")
            return redirect(url_for("main.venues"))
        existing = db.session.scalar(
            db.select(Venue).where(Venue.name == name, Venue.location == location)
        )
        if existing:
            flash("That venue already exists.", "info")
            return redirect(url_for("main.venues"))
        venue = Venue(
            id=f"V-{uuid.uuid4().hex[:8]}",
            name=name,
            location=location,
            num_of_capacity=capacity,
        )
        db.session.add(venue)
        db.session.commit()
        flash("Venue added.", "success")
        return redirect(url_for("main.venues"))

    venues = db.session.scalars(db.select(Venue).order_by(Venue.name)).all()
    return render_template("add-venue.html", venues=venues)
