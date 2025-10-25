from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, current_app
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

# Listing out all the events list that is to be displayed in thee index page.
@main_bp.route('/')
def index():
    events = db.session.scalars(
        db.select(Event).order_by(Event.date_time.asc())
    ).all()
    return render_template("index.html", events=events)

## === Fetching Individual Event Details
#Search Bar
@main_bp.route('/search')
def search():
    if request.args['search'] and request.args['search'] != "":
        print(request.args['search'])
        query = "%" + request.args['search'] + "%"
        events = db.session.scalars(db.select(Event).where(Event.description.like(query))).all()
        return render_template('index.html', events=events)
    else:
        return redirect(url_for('main.index'))

# Backend Filter (working on - Still need to do front end)
@main_bp.route('/filter-event/<category>')
def filter_event(category):
    filtered = db.session.scalars(
        db.select(Event).join(Category).where(Category.category_name.ilike(category)).order_by(Event.date_time.asc())
        ).all()
    return render_template('index.html', events=filtered)    
    
@main_bp.route('/events/<int:event_id>')
def event_detail(event_id):
     event = db.session.get(Event, event_id)
     if not event:
         abort(404)
     return render_template('event.html', event=event)

@main_bp.route('/my-bookings')
@login_required
def my_bookings():
    # Get all bookings for the current user
    bookings = db.session.scalars(
        db.select(Booking).where(Booking.user_id == current_user.id).order_by(Booking.id.desc())
    ).all()
    return render_template('bookings.html', bookings=bookings)

# @main_bp.route('/events/<int:event_id>/book', methods=['GET', 'POST'])
# @login_required
# def book_event(event_id):
#     event = db.session.get(Event, event_id)
#     if not event:
#         abort(404)

#     form = BookingForm()

#     if form.validate_on_submit():
#         ticket_type = form.ticket_type.data
#         quantity = form.no_of_tickets.data

#         # example pricing
#         price_lookup = {
#             'Phase I': 99,
#             'Phase II': 150,
#             'Phase III': 279,
#         }
#         ticket_price = price_lookup.get(ticket_type, 0)
#         total_price = ticket_price * quantity

#         # create booking
#         booking = Booking(
#             user_id=current_user.id,
#             event_id=event.id,
#             no_of_tickets=quantity,
#             total_price=total_price,
#             booking_status='Confirmed'
#         )
#         db.session.add(booking)
#         db.session.flush()  # get booking.id before commit

#         # create ticket
#         for _ in range(quantity):
#             ticket = Ticket(
#                 price=ticket_price,
#                 ticket_type=ticket_type,
#                 booking_id=booking.id
#             )
#             db.session.add(ticket)

#         db.session.commit()
#         flash(f"Booking Successful! Your Order ID is {booking.id}", 'success')

#         # redirect back to event page o bookings page
#         return redirect(url_for('main.my_bookings'))

#     # if GET request or form not valid show booking form
#     return render_template('book_event.html', event=event, form=form)

@main_bp.route("/events", methods=["GET"])
@login_required
def events():
    items = db.session.scalars(db.select(Event).order_by(Event.date_time.desc())).all()
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

# @main_bp.route("/create-event", methods=["GET", "POST"])
# @login_required
# def create_event():
#     if request.method == "POST":
#         title = request.form.get("title", "").strip()
#         description = request.form.get("description", "").strip()
#         hour = int(request.form.get("hour") or 0)
#         minute = int(request.form.get("minute") or 0)
#         duration = int(request.form.get("duration") or 0)
#         status = request.form.get("status") or "Open"
#         total_tickets = int(request.form.get("number") or 1)



#         day = request.form.get("day", "").strip()
#         event_dt = datetime.strptime(day, "%Y-%m-%d")
#         event_dt = event_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
#         image_file = request.files.get("image")
#         image_filename = None
#         if image_file and image_file.filename:
#             ext = image_file.filename.rsplit(".", 1)[-1].lower()
#             if ext not in {"jpg", "jpeg", "png", "gif"}:
#                 flash("Unsupported image type.", "warning")
#                 return redirect(url_for("main.create_event"))
#             safe_name = secure_filename(image_file.filename)
#             new_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"

#             # Saving to the static folder. 
#             save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_name)
#             image_file.save(save_path)
#             image_filename = new_name

#         category = db.session.scalar(
#             db.select(Category).where(Category.category_name == "General")
#         )
#         if not category:
#             category = Category(category_name="General", description="Default")
#             db.session.add(category)
#             db.session.flush()

#         venue_id = request.form.get("venue_id")
#         venue = db.session.get(Venue, venue_id)
#         if not venue:
#             flash("Select a valid venue.", "warning")
#             return redirect(url_for("main.create_event"))

#    if form.validate_on_submit():
#         event = Event(
#             title=title,
#             description=description,
#             time=event_dt,
#             image=image_filename,
#             status=status,
#             total_tickets=total_tickets,
#             duration_minutes=duration or None,
#             seat_types=json.dumps(seat_types) if seat_types else None,
#             owner_id=current_user.id,
#             category_id=category.id,
#             venue_id=venue.id,
#         )

#         db.session.add(event)
#         db.session.commit()
#         flash("Event created successfully!", "success")
#         return redirect(url_for("main.events"))

#     venues = db.session.scalars(db.select(Venue).order_by(Venue.name)).all()
#     return render_template("create-event.html", venues=venues)

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




