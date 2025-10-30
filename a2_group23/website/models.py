# website/models.py
from . import db
from datetime import datetime
from flask_login import UserMixin

# User Table Structure 
class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40))
    role = db.Column(db.String(20), nullable=False, default='user')



# Relationship of User with other Tables.
    events = db.relationship(
        "Event", back_populates="owner", cascade="all, delete-orphan"
    )
    bookings = db.relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )

# Adding these dunder methods for better visuals. Unsure, if it is imporatant, but they say it is beneficial while debugging
# I found them being used by people in stackoverflow, so i put them as well. We'll see use case in future.

    def __repr__(self):
        return f"<User {self.email}>"

class Venue(db.Model):
    __tablename__ = "venue"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    num_of_capacity = db.Column(db.Integer, nullable=False)


    events = db.relationship("Event", back_populates="venue")

    def __repr__(self):
        return f"<Venue {self.id}:{self.name}>"

class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="Open")
    duration_minutes = db.Column(db.Integer)

    ticket_price = db.Column(db.Integer, nullable=False)
    ticket_quantity = db.Column(db.Integer, nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)

    owner = db.relationship("User", back_populates="events")
    venue = db.relationship("Venue", back_populates="events")

    comments = db.relationship("Comment", back_populates="event", cascade="all, delete-orphan")
    bookings = db.relationship("Booking", back_populates="event", cascade="all, delete-orphan")
    tickets = db.relationship("Ticket", back_populates="event", cascade="all, delete-orphan")

    # This method returns how many tickets are left.
    def tickets_left(self):
        booked = sum(b.no_of_tickets for b in self.bookings if b.booking_status == "Confirmed")
        remaining = self.ticket_quantity - booked
        return max(remaining, 0)
    
    # This method updates the event status based on remaining tickets.
    def update_status(self):
        remaining = self.tickets_left()
        new_status = "Sold Out" if remaining == 0 else "Open"
        if self.status != new_status:
            self.status = new_status
            db.session.commit()


    def __repr__(self):
        return f"<Event {self.id}:{self.title}>"




class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)

    author = db.relationship("User", back_populates="comments")
    event = db.relationship("Event", back_populates="comments")

    def __repr__(self):
        return f"<Comment {self.id} by {self.user_id} on {self.event_id}>"

class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    no_of_tickets = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    booking_status = db.Column(db.String(20), nullable=False, default="Pending")

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)

    user = db.relationship("User", back_populates="bookings")
    event = db.relationship("Event", back_populates="bookings")
    tickets = db.relationship("Ticket", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Booking {self.id} user={self.user_id} event={self.event_id}>"


class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), nullable=True) 

    event = db.relationship("Event", back_populates="tickets")
    booking = db.relationship("Booking", back_populates="tickets")

    def __repr__(self):
        return f"<Ticket {self.id} price={self.price} qty={self.quantity}>"
