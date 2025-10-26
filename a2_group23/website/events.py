from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Booking, Ticket, Event
from .forms import BookingForm, EventForm, TicketForm
from datetime import datetime
from datetime import datetime
import os, uuid, json

from website.forms import EventForm, TicketForm

from . import db
from .models import Event, Venue, Category, Comment, Ticket, Booking

events_bp = Blueprint("events", __name__)  # no url_prefix so paths stay the same if you want

@events_bp.route("/create-event", methods=["GET", "POST"])
@login_required
def create():
    event_form = EventForm()
    ticket_form = TicketForm()
    
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        hour = int(request.form.get("hour") or 0)
        minute = int(request.form.get("minute") or 0)
        duration = int(request.form.get("duration") or 0)
        status = request.form.get("status") or "Open"

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

        type = (request.form.get("type") or "").strip()
        price = int(request.form.get("price") or 0)
        quantity = int(request.form.get("quantity") or 0)



        if event_form.validate_on_submit():
            new_event = Event(
                id=f"V-{uuid.uuid4().hex[:8]}",
                title=title,
                description=description,
                time=event_dt,
                image=image_filename,
                status=status,
                duration_minutes=duration or None,
                owner_id=current_user.id,
                category_id=category.id,
                venue_id=venue.id,
                ticket_type=type,
                ticket_price=price,
                ticket_quantity=quantity,                
            )

        db.session.add(new_event)
        db.session.flush()

        for ticket_form in event_form.tickets:
            a_ticket = Ticket(
                id=f"V-{uuid.uuid4().hex[:8]}",
                type=ticket_form.type.data,
                price=ticket_form.price.data,
                quantity=ticket_form.quantity.data,
                event_id=new_event.id
            )
            db.session.add(a_ticket)       
        db.session.commit(new_event, a_ticket)

        flash("Event with tickets created successfully!", "success")
        return redirect(url_for("main.events", event_id=new_event.id))


    venues = db.session.scalars(db.select(Venue).order_by(Venue.name)).all()
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    return render_template("create-event.html", venues=venues, categories=categories)


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

    comments = db.session.scalars(
        db.select(Comment)
          .where(Comment.event_id == event.id)
          .order_by(Comment.posted_date.desc())
    ).all()

    return render_template('event.html', event=event, comments=comments)




@events_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.events"))

    # Optional: only owner can edit
    # if event.owner_id != current_user.id:
    #     flash("You don't have permission to edit this event.", "danger")
    #     return redirect(url_for("main.events"))

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        hour = int(request.form.get("hour") or 0)
        minute = int(request.form.get("minute") or 0)
        duration = int(request.form.get("duration") or 0)
        status = request.form.get("status") or "Open"
        if event.status == "Inactive":
            flash("Cannot change the status of a past event", "warning")
            return redirect(url_for("main.events"))
        venue_id = request.form.get("venue_id")

        category = db.session.scalar(
            db.select(Category).where(Category.category_name == "General")
        )
        if not category:
            category = Category(category_name="General", description="Default")
            db.session.add(category)
            db.session.flush()

        # date (required)
        day = (request.form.get("day") or "").strip()
        event_dt = datetime.strptime(day, "%Y-%m-%d").replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

        # venue (required)
        venue = db.session.get(Venue, venue_id)
        if not venue:
            flash("Select a valid venue.", "warning")
            return redirect(url_for("events.edit", event_id=event.id))

        # optional image replacement
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

            # delete old file if existed
            if event.image:
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], event.image)
                try:
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except OSError:
                    pass

            event.image = new_name  # set new filename

        ticket_type = db.session.scalar(
            db.select(Event).where(Event.ticket_type == "General Admission")
        )
        if not ticket_type:
            flash("Select a valid type.", "warning")
            return redirect(url_for("events.create"))
        ticket_price = request.form.get("ticket_price")
        ticket_quantity = request.form.get("ticket_quanitty")

        # update fields
        event.title = title
        event.description = description
        event.time = event_dt
        event.status = status
        event.category_id = category
        event.duration_minutes = duration or None
        event.venue_id = venue.id
        event.ticket_type = ticket_type
        event.ticket_price = ticket_price
        event.ticket_quantity = ticket_quantity
        

        db.session.commit()
        flash("Event updated successfully!", "success")
        return redirect(url_for("main.events"))

    # GET: render form with current values
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
        return redirect(url_for("events.event_detail", event_id=0))  # harmless fallback

    # allow deletion by comment author or event owner
    is_author = c.user_id == current_user.id
    is_event_owner = (c.event and c.event.owner_id == current_user.id)
    if not (is_author or is_event_owner):
        flash("You don't have permission to delete this comment.", "danger")
        return redirect(url_for("events.event_detail", event_id=c.event_id) + "#comments")

    db.session.delete(c)
    db.session.commit()
    flash("Comment deleted.", "success")
    return redirect(url_for("events.event_detail", event_id=c.event_id) + "#comments")
