from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .models import Booking, Ticket, Event, Venue, Category, Comment
from .forms import BookingForm
from datetime import datetime
import os, uuid

events_bp = Blueprint("events", __name__)

@events_bp.route("/create-event", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        day = (request.form.get("day") or "").strip()
        hour = int(request.form.get("hour") or 0)
        minute = int(request.form.get("minute") or 0)
        duration_minutes = int(request.form.get("duration") or 0)
        status = (request.form.get("status") or "Open").strip()
        if not day:
            flash("Please pick a date.", "warning")
            return redirect(url_for("events.create"))
        date_time = datetime.strptime(day, "%Y-%m-%d").replace(hour=hour, minute=minute, second=0, microsecond=0)
        total_tickets = int(request.form.get("total_tickets") or request.form.get("number") or 100)

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

        category = db.session.scalar(db.select(Category).where(Category.category_name == "General"))
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
            date_time=date_time,
            image=image_filename,
            status=status,
            duration_minutes=duration_minutes or None,
            total_tickets=total_tickets,
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
        price_lookup = {'Phase I': 99, 'Phase II': 150, 'Phase III': 279}
        ticket_price = price_lookup.get(ticket_type, 0)
        total_price = ticket_price * quantity

        if quantity > event.tickets_left():
            flash(f"Only {event.tickets_left()} tickets left.", "warning")
            return render_template('book_event.html', event=event, form=form)

        booking = Booking(
            user_id=current_user.id,
            event_id=event.id,
            no_tickets=quantity,
            total_price=total_price,
            booking_status='Confirmed'
        )
        db.session.add(booking)
        db.session.flush()

        for _ in range(quantity):
            ticket = Ticket(price=ticket_price, type=ticket_type, booking_id=booking.id)
            db.session.add(ticket)

        db.session.commit()
        flash(f"Booking Successful! Your Order ID is {booking.id}", 'success')
        return redirect(url_for('main.my_bookings'))

    return render_template('book_event.html', event=event, form=form)

@events_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    comments = db.session.scalars(
        db.select(Comment).where(Comment.event_id == event.id).order_by(Comment.posted_date.desc())
    ).all()

    similar_events = db.session.scalars(
        db.select(Event).where(Event.category_id == event.category_id, Event.id != event.id).order_by(Event.date_time.asc()).limit(4)
    ).all()

    return render_template('event.html', event=event, comments=comments, similar_events=similar_events)

@events_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.events"))

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        day = (request.form.get("day") or "").strip()
        hour = int(request.form.get("hour") or 0)
        minute = int(request.form.get("minute") or 0)
        duration_minutes = int(request.form.get("duration") or 0)
        status = (request.form.get("status") or "Open").strip()
        venue_id = request.form.get("venue_id")

        if not day:
            flash("Please pick a date.", "warning")
            return redirect(url_for("events.edit", event_id=event.id))

        date_time = datetime.strptime(day, "%Y-%m-%d").replace(hour=hour, minute=minute, second=0, microsecond=0)

        venue = db.session.get(Venue, venue_id)
        if not venue:
            flash("Select a valid venue.", "warning")
            return redirect(url_for("events.edit", event_id=event.id))

        image_file = request.files.get("image")
        if image_file and image_file.filename:
            ext = image_file.filename.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "gif"}:
                flash("Unsupported image type.", "warning")
                return redirect(url_for("events.edit", event_id=event.id))
            safe_name = secure_filename(image_file.filename)
            new_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_name)
            image_file.save(save_path)

            if event.image:
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], event.image)
                try:
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except OSError:
                    pass
            event.image = new_name

        event.title = title
        event.description = description
        event.date_time = date_time
        event.status = status
        event.duration_minutes = duration_minutes or None
        event.venue_id = venue.id

        db.session.commit()
        flash("Event updated successfully!", "success")
        return redirect(url_for("main.events"))

    venues = db.session.scalars(db.select(Venue).order_by(Venue.name)).all()
    return render_template("edit-event.html", event=event, venues=venues)

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
