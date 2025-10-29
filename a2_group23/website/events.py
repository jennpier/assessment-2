from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os, uuid

from . import db
from .models import Event, Venue, Category, Comment, Booking, Ticket
from .forms import EventForm, TicketForm, BookingForm

events_bp = Blueprint("events", __name__)



# Route for Creating an Event
@events_bp.route("/create-event", methods=["GET", "POST"])
@login_required
def create():
    event_form = EventForm(request.form)
    ticket_form = TicketForm(request.form)

    if request.method == "POST" and event_form.validate_on_submit() and ticket_form.validate_on_submit():
        
        # Generatung a  unique string-based event ID
        title = event_form.title.data.strip()
        description = event_form.description.data.strip()
        day = event_form.day.data
        hour = event_form.hour.data
        minute = event_form.minute.data
        duration = event_form.duration.data
        status = "Open"

        event_dt = datetime.combine(day, datetime.min.time()).replace(hour=hour, minute=minute)

        # Checking that event is not created for a past date/time.
        now = datetime.now()
        if event_dt < now:
            flash("Event date and time cannot be in the past", "danger")
            return redirect(url_for("events.create"))

        # Handling image upload - it should be saved at correct path
        image_file = request.files.get("image")
        image_filename = None
        if image_file and image_file.filename:
            ext = image_file.filename.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "gif"}:
                flash("Unsupported image type.", "warning")
                return redirect(url_for("events.create"))
            safe_name = secure_filename(image_file.filename)
            new_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_name)
            image_file.save(save_path)
            image_filename = new_name

        # Validating venue - Hard for hacker to manipulate, but can be done with burpsuite. 
        venue_id = request.form.get("venue_id")
        venue = db.session.get(Venue, venue_id)
        if not venue:
            flash("Select a valid venue.", "warning")
            return redirect(url_for("events.create"))

        # Validating Category
        category_id = request.form.get("category_id")
        category = db.session.get(Category, category_id)
        if not category:
            flash("Select a valid category.", "warning")
            return redirect(url_for("events.create"))

        new_event = Event(
            title=title,
            description=description,
            date_time=event_dt,
            image=image_filename,
            status=status,
            duration_minutes=duration or None,
            owner_id=current_user.id,
            category_id=category.id,
            venue_id=venue.id,
            ticket_price=ticket_form.price.data,
            ticket_quantity=ticket_form.quantity.data,
        )

        db.session.add(new_event)
        db.session.flush()

        # Creating associated ticket
        ticket = Ticket(
            price=ticket_form.price.data,
            quantity=ticket_form.quantity.data,
            event_id=new_event.id
        )
        db.session.add(ticket)

        db.session.commit()
        flash("Event created successfully!", "success")
        return redirect(url_for("main.events"))

    # Load venues and categories for the form
    venues = db.session.scalars(db.select(Venue).order_by(Venue.name)).all()
    categories = db.session.scalars(db.select(Category).order_by(Category.category_name)).all()

    return render_template(
        "create-event.html",
        form=event_form,
        ticket_form=ticket_form,
        venues=venues,
        categories=categories
    )



# Route for editing an event
@events_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.events"))

    if request.method == "POST":
        event.title = request.form.get("title", event.title)
        event.description = request.form.get("description", event.description)
        event.duration_minutes = int(request.form.get("duration") or event.duration_minutes)
        event.ticket_price = int(request.form.get("ticket_price") or event.ticket_price)
        event.ticket_quantity = int(request.form.get("ticket_quantity") or event.ticket_quantity)
        event.status = request.form.get("status", event.status)
        event.venue_id = request.form.get("venue_id") or event.venue_id
        event.category_id = request.form.get("category_id") or event.category_id


        # Handle image replacement
        image_file = request.files.get("image")
        if image_file and image_file.filename:
            ext = image_file.filename.rsplit(".", 1)[-1].lower()
            if ext in {"jpg", "jpeg", "png", "gif"}:
                safe_name = secure_filename(image_file.filename)
                new_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
                save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_name)
                image_file.save(save_path)
                if event.image:
                    old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], event.image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                event.image = new_name

        db.session.commit()
        flash("Event updated successfully!", "success")
        return redirect(url_for("main.events"))

    venues = db.session.scalars(db.select(Venue).order_by(Venue.name)).all()
    categories = db.session.scalars(db.select(Category).order_by(Category.category_name)).all()
    return render_template("update-event.html", event=event, venues=venues, categories=categories, form=EventForm())


# Delete Event
@events_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
def delete(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.events"))

    if event.image:
        img_path = os.path.join(current_app.config["UPLOAD_FOLDER"], event.image)
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except OSError:
            pass

    db.session.delete(event)
    db.session.commit()
    flash("Event deleted.", "success")
    return redirect(url_for("main.events"))


# Booking an Event
@events_bp.route('/events/<int:event_id>/book', methods=['GET', 'POST'])
@login_required
def book_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    form = BookingForm()

    if form.validate_on_submit():
        quantity = form.no_of_tickets.data

        # Checking if user is trying to buy more tickets than available for the show
        if quantity > event.tickets_left():
            flash("Not enough tickets available.", "warning")
            return redirect(url_for('events.book_event', event_id=event.id))

        total_price = event.ticket_price * quantity

        # Actual Adding Booking details to db is done at line 201.
        booking = Booking(
            user_id=current_user.id,
            event_id=event.id,
            no_of_tickets=quantity,
            total_price=total_price,
            booking_status='Confirmed'
        )

        db.session.add(booking)

        # Decreasing the event tickets after booking is done.
        if event.tickets_left() <= 0:
            event.status = "Sold Out"


        db.session.commit()

        # Redirecting user to the Order COnfirmation pagee.
        return redirect(url_for('events.order_confirmation', booking_id=booking.id))

    return render_template('book_event.html', event=event, form=form)


# Booking Confirmation Route
@events_bp.route('/booking/<int:booking_id>/confirmation')
@login_required
def order_confirmation(booking_id):
    # Making sure booking exist for the user.
    booking = db.session.get(Booking, booking_id)
    if not booking or booking.user_id != current_user.id:
        abort(404)

    event = booking.event
    return render_template('order-confirmation.html', booking=booking, event=event)

# Listing all Events Booked by the user
@events_bp.route("/my-bookings")
@login_required
def my_bookings():
    bookings = (
        db.session.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return render_template("my-bookings.html", bookings=bookings)


# Event Details Page
@events_bp.route('/events/<event_id>')
def event_detail(event_id):
    event = db.session.get(Event, int(event_id))
    if not event:
        abort(404)

    comments = event.comments
    comments.sort(key=lambda c: c.posted_date, reverse=True)
    return render_template('event.html', event=event, comments=comments)


# To Add the comment
@events_bp.route("/events/<int:event_id>/comments", methods=["POST"])
@login_required
def add_comment(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    text = (request.form.get("comment") or "").strip()
    if not text:
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for("events.event_detail", event_id=event.id) + "#comments")

    c = Comment(comment=text, user_id=current_user.id, event_id=event.id)
    db.session.add(c)
    db.session.commit()
    flash("Comment posted.", "success")
    return redirect(url_for("events.event_detail", event_id=event.id) + "#comments")


# To Delete the commment
@events_bp.route("/comments/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    c = db.session.get(Comment, comment_id)
    if not c:
        flash("Comment not found.", "warning")
        return redirect(url_for("main.events"))

    is_author = c.user_id == current_user.id
    is_event_owner = (c.event and c.event.owner_id == current_user.id)
    if not (is_author or is_event_owner):
        flash("You don't have permission to delete this comment.", "danger")
        return redirect(url_for("events.event_detail", event_id=c.event_id) + "#comments")

    db.session.delete(c)
    db.session.commit()
    flash("Comment deleted.", "success")
    return redirect(url_for("events.event_detail", event_id=c.event_id) + "#comments")
