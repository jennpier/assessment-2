from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Booking, Ticket, Event
from .forms import BookingForm
from datetime import datetime
from datetime import datetime
import os, uuid, json

from website.forms import EventForm

from . import db
from .models import Event, Venue, Category

events_bp = Blueprint("events", __name__)  # no url_prefix so paths stay the same if you want

@events_bp.route("/create-event", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        hour = int(request.form.get("hour") or 0)
        minute = int(request.form.get("minute") or 0)
        duration = int(request.form.get("duration") or 0)
        status = request.form.get("status") or "Open"
        seat_types = request.form.getlist("seat_types")

        day = (request.form.get("day") or "").strip()
        if not day:
            flash("Please pick a date.", "warning")
            return redirect(url_for("events.create"))
        event_dt = datetime.strptime(day, "%Y-%m-%d").replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

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
            return redirect(url_for("events.create"))

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



@events_bp.route('/events/<int:event_id>/book', methods=['GET', 'POST'])
@login_required
def book_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    form = BookingForm()

    if form.validate_on_submit():
        ticket_type = form.ticket_type.data
        quantity = form.no_of_tickets.data

        # example pricing
        price_lookup = {
            'Phase I': 99,
            'Phase II': 150,
            'Phase III': 279,
        }
        ticket_price = price_lookup.get(ticket_type, 0)
        total_price = ticket_price * quantity

        # create booking
        booking = Booking(
            user_id=current_user.id,
            event_id=event.id,
            no_of_tickets=quantity,
            total_price=total_price,
            booking_status='Confirmed'
        )
        db.session.add(booking)
        db.session.flush()  # get booking.id before commit

        # create ticket
        for _ in range(quantity):
            ticket = Ticket(
                price=ticket_price,
                ticket_type=ticket_type,
                booking_id=booking.id
            )
            db.session.add(ticket)

        db.session.commit()
        flash(f"Booking Successful! Your Order ID is {booking.id}", 'success')

        # redirect back to event page o bookings page
        return redirect(url_for('main.my_bookings'))

    # if GET request or form not valid show booking form
    return render_template('book_event.html', event=event, form=form)


@events_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)
    return render_template('event.html', event=event)
