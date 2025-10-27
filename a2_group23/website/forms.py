from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, RadioField, DateTimeField, IntegerField, FieldList, FormField
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
import datetime
# forms.py (near the top)
ALLOWED_FILE = {"png", "jpg", "jpeg", "gif", "PNG", "JPG", "JPEG", "GIF"}



# creates the login information
class LoginForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired('Enter user name')])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

 # this is the registration form
class RegisterForm(FlaskForm):
    user_name=StringField("Name", validators=[InputRequired()])
    email = StringField("Email Address", validators=[Email("Please enter a valid email")])
    phone = StringField("Phone Number")
    # linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")

    # submit button

    submit = SubmitField("Register")

class TicketForm(FlaskForm):
    type=StringField("Ticket type", validatiors=[InputRequired('Type of ticket')])
    price=IntegerField("Ticket Prices", validators=[InputRequired('Price must be set')])
    quantity=IntegerField("Number of available tickets per type", validators=[InputRequired('Must be at least 1 ticket available for booking'), NumberRange(min=1)])

class EventForm(FlaskForm):
    title=StringField("Event Title", validators=[InputRequired('Enter title')])
    category=RadioField("Category", 
                        choices=[('Category 1', 'Jazz'),
                                 ('Category 2', 'Rock'),
                                 ('Category 3', 'Hip Hop'),
                                 ('Category 4', 'Pop'),
                                 ('Category 5', 'Metal'),
                                ],   
                                 validators=[InputRequired('Choose category')])
    description=TextAreaField("Event Description", validators=[InputRequired('Enter description')])
    image = FileField('Destination Image', validators=[
        FileRequired(message = 'Image cannot be empty'),
        FileAllowed(ALLOWED_FILE, message='Only supports png, jpg, JPG, PNG')])
    date_time=DateTimeField("Event Date and Time", validators=[InputRequired('Date and Time required')], format='%D-%m-%Y %H:%M')
    duration_minutes=IntegerField("Duration in Minutes", validators=[InputRequired('Duration must be set')])
    tickets=FieldList(FormField(TicketForm), min_entries=1)
    submit = SubmitField("Post")

#event date cannot be in the past??
    def date_check(form, field):
        if field.date_time < datetime.date.today():
            raise ValidationError("Date cannot be in the past")
        
class BookingForm(FlaskForm):
    ticket_choice=RadioField("Ticket type", 
                           choices=[('type 1', 'General Admission'),
                                    ('type 2', 'VIP Pass'),
                                    ('type 3', 'Backstage Pass')
                           ],
                           validators=[InputRequired()])
    no_of_tickets=IntegerField("Number of tickets", validators=[InputRequired(), NumberRange(min=1)])
    submit=SubmitField("Buy")





