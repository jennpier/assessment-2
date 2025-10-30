from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Booking, Ticket, Event, User, Venue, Comment
from .forms import BookingForm
from datetime import datetime
from datetime import datetime
import os, uuid, json

from website.forms import EventForm

from . import db
from .models import Event, Venue, Ticket, Booking, Comment, User

main_bp = Blueprint('main', __name__)

# Listing out all the events list that is to be displayed in thee index page.
@main_bp.route('/')
def index():
    events = db.session.scalars(
        db.select(Event).order_by(Event.date_time.asc())
    ).all()
    return render_template("index.html", events=events)

# Search Bar
@main_bp.route('/search')
def search():
    if request.args['search'] and request.args['search'] != "":
        print(request.args['search'])
        query = "%" + request.args['search'] + "%"
        events = db.session.scalars(db.select(Event).where((Event.title.like(query)) | (Event.description.like(query)))).all()
        return render_template('index.html', events=events)
    else:
        return redirect(url_for('main.index'))


# Filter Events based on genre
@main_bp.route('/filter-event/<category>')
def filter_event(category):
    if category == "All":
        filtered = db.session.scalars(
            db.select(Event).order_by(Event.date_time.asc())
        ).all()
    else:
        filtered = db.session.scalars(
            db.select(Event)
            .where(Event.category.ilike(category))
            .order_by(Event.date_time.asc())
        ).all()
    return render_template('index.html', events=filtered)


@main_bp.route('/my-bookings')
@login_required
def my_bookings():
    # Admin Users can see all the bookings made by every users
    if current_user.role == "admin":
        bookings = db.session.scalars(
            db.select(Booking).order_by(Booking.id.desc())
        ).all()
    else:
        # Normal users can see onlty their own bookings.
        bookings = db.session.scalars(
            db.select(Booking)
            .where(Booking.user_id == current_user.id)
            .order_by(Booking.id.desc())
        ).all()

    return render_template('bookings.html', bookings=bookings)

@main_bp.route("/events", methods=["GET"])
@login_required
def events():
    # Admin can see all the events. 
    if current_user.role == "admin":
        items = db.session.scalars(
            db.select(Event).order_by(Event.date_time.desc())
        ).all()
    else:
        # Individual users can only see events created by them
        items = db.session.scalars(
            db.select(Event)
            .where(Event.owner_id == current_user.id)
            .order_by(Event.date_time.desc())
        ).all()

    return render_template("all_events.html", events=items)

@main_bp.route("/venues", methods=["GET", "POST"])
@login_required
def venues():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        location = (request.form.get("location") or "").strip()
        capacity = int(request.form.get("capacity") or 0)
 
        # Validating input - if filled up or not. Aslo checking the capacity.
        if not name or not location or capacity <= 0:
            flash("Please fill all fields correctly.", "warning")
            return redirect(url_for("main.venues"))

        # Check for duplicate entry.
        existing = db.session.scalar(
            db.select(Venue).where(
                Venue.name == name,
                Venue.location == location
            )
        )
        if existing:
            flash("That venue already exists.", "info")
            return redirect(url_for("main.venues"))

        venue = Venue(
            name=name,
            location=location,
            num_of_capacity=capacity,
        )
        db.session.add(venue)
        db.session.commit()

        flash("Venue added.", "success")
        return redirect(url_for("main.venues"))

    # GET: show existing venues
    venues = db.session.scalars(db.select(Venue).order_by(Venue.name)).all()
    return render_template("add-venue.html", venues=venues)



#error handling
@main_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template ('500.html'), 500



