from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os, uuid, json

from website.forms import EventForm

from . import db
from .models import Event, Venue, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template("Index.html")

@main_bp.route("/events", methods=["GET"])
@login_required
def events():
    items = db.session.scalars(db.select(Event).order_by(Event.time.desc())).all()
    return render_template("all_events.html", events=items)   # or 'events.html' if that’s your file

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

@main_bp.route("/create-event", methods=["GET", "POST"])
@login_required
def create_event():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        day = request.form.get("day", "").strip()
        hour = int(request.form.get("hour") or 0)
        minute = int(request.form.get("minute") or 0)
        duration = int(request.form.get("duration") or 0)
        status = request.form.get("status") or "Open"
        seat_types = request.form.getlist("seat_types")

        try:
            date_obj = datetime.strptime(day, "%Y-%m-%d")
            event_dt = date_obj.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except Exception:
            flash("Invalid date/time format.", "danger")
            return redirect(url_for("main.create_event"))

        image_file = request.files.get("image")
        image_filename = None
        if image_file and image_file.filename:
            ext = image_file.filename.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "gif"}:
                flash("Unsupported image type.", "warning")
                return redirect(url_for("main.create_event"))
            safe_name = secure_filename(image_file.filename)
            new_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_name)
            image_file.save(save_path)
            image_filename = new_name

        category = db.session.scalar(
            db.select(Category).where(Category.category_name == "General")
        )
        if not category:
            category = Category(category_name="General", description="Default")
            db.session.add(category)
            db.session.flush()

        venue_id = request.form.get("venue_id")
        venue = db.session.get(Venue, venue_id)
        if not venue:
            flash("Select a valid venue.", "warning")
            return redirect(url_for("main.create_event"))

        event = Event(
            title=title,
            description=description,
            time=event_dt,
            image=image_filename,
            status=status,
            duration_minutes=duration or None,
            seat_types=json.dumps(seat_types) if seat_types else None,
            owner_id=current_user.id,
            category_id=category.id,
            venue_id=venue.id,
        )

        db.session.add(event)
        db.session.commit()
        flash("Event created successfully!", "success")
        return redirect(url_for("main.events"))

    venues = db.session.scalars(db.select(Venue).order_by(Venue.name)).all()
    return render_template("create-event.html", venues=venues)

#change to it's own event.py file - include /update-event and /events?
# @main_bp.route('/create-event', methods = ['GET', 'POST'])
# def create_event():
#   print('Method type: ', request.method)
#   form = EventForm()
#   if form.validate_on_submit():
#     db_file_path = check_upload_file(form)    
#     event = Event(title=form.title.data,
#                   category=form.category.data,
#                   description=form.description.data,
#                   image=form.image.data,
#                   date_time=form.date_time.data,
#                   ticket_price=form.ticket_price.data
#                   )
#     db.session.add(event)
#     db.session.commit()
#     print('Successfully created new event')
#     return redirect(url_for('event.create_event'))
#   return render_template('/<id>/create_event.html', form=form)

# @main_bp.route('/update-event')
# def update_event():
#     return render_template()


