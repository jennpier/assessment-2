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

# Added _repr_ method of debugging purposes.
    def __repr__(self):
        return f"<User {self.email}>"

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

    events = db.relationship("Event", back_populates="category")

    def __repr__(self):
        return f"<Category {self.category_name}>"

class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.String(50), primary_key=True) 
    name = db.Column(db.String(200), nullable=False)
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
    total_tickets = db.Column(db.Integer, nullable=False)
    no_sold_tickets = db.Column(db.Integer, default=0)

    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    venue_id = db.Column(db.String(50), db.ForeignKey("venue.id"), nullable=False)

    owner = db.relationship("User", back_populates="events")
    category = db.relationship("Category", back_populates="events")
    venue = db.relationship("Venue", back_populates="events")

    comments = db.relationship(
        "Comment", back_populates="event", cascade="all, delete-orphan"
    )
    bookings = db.relationship(
        "Booking", back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Event {self.id}:{self.title}>"
    
    def tickets_sold(self):
        return Ticket.query.filter_by(booking_id=self.id).count()

    def tickets_left(self):
        return self.total_tickets - self.tickets_sold()
    
    #def sold_out(self):
        #return self.no_sold_tickets >= self.total_tickets
   
    def status(self):
        if self.status == 'cancelled':
            return
        elif self.time < datetime.utcnow():
            self.status = 'inactive'
        elif self.tickets_left() <= 0:
            self.status = 'sold_out'
        else:
            self.status = 'active'

#class Status(db.Model):
#    __tablename___ = "status"

#    id = db.Column(db.Integer, primary_key=True)    
#    open = db.Column(db.String(10), nullable=False)
#    cancelled = db.Column(db.String(10), nullable=False)
#    inactive = db.Column(db.String(10), nullable=False)
#    sold_out = db.Column(db.String(10), nullable=False)

#    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
#    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), nullable=False)

#    event = db.relationship(
#        "Event", back_populates="status", cascade="all, delete-orphan"
#    )

#    bookings = db.relationship(
#        "Booking", back_populates="event", cascade="all, delete-orphan"
#    )


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

# Booking 1..* Tickets, belongs to 1 User and 1 Event
class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    no_tickets = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    booking_status = db.Column(db.String(20), nullable=False, default="Pending")

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)

    user = db.relationship("User", back_populates="bookings")
    event = db.relationship("Event", back_populates="bookings")

    tickets = db.relationship(
        "Ticket", back_populates="booking", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Booking {self.id} user={self.user_id} event={self.event_id}>"

# Ticket belongs to 1 Booking
class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)

    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), nullable=False)
    booking = db.relationship("Booking", back_populates="tickets")
    event = db.relationship("Event", back_populates="tickets" )

    def __repr__(self):
        return f"<Ticket {self.id} booking={self.booking_id}>"
