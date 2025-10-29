from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, RadioField, IntegerField, DateField
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange, ValidationError, DataRequired, Optional
from flask_wtf.file import FileField, FileAllowed, FileRequired
import datetime

ALLOWED_FILE = {"png", "jpg", "jpeg", "gif", "PNG", "JPG", "JPEG", "GIF"}



# creates the login information
class LoginForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired('Enter user name')])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    user_name=StringField("Name", validators=[InputRequired()])
    email = StringField("Email Address", validators=[Email("Please enter a valid email")])
    phone = StringField("Phone Number")
    # linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")
    submit = SubmitField("Register")


class EditProfileForm(FlaskForm):
    user_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    password = PasswordField("New Password (optional)", validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[Optional(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField("Update Profile")


class TicketForm(FlaskForm):
    price = IntegerField('Ticket Price ($)', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Available Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Set Ticket Details')


class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    day = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    hour = IntegerField('Time (Hour)', validators=[DataRequired(), NumberRange(min=0, max=23)])
    minute = IntegerField('Time (Minute)', validators=[DataRequired(), NumberRange(min=0, max=59)])
    duration = IntegerField('Event Duration (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    image = FileField('Event Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Create Event')


    def date_check(form, field):
        if field.date_time < datetime.date.today():
            raise ValidationError("Date cannot be in the past")
        
        
class BookingForm(FlaskForm):
    no_of_tickets = IntegerField("Number of Tickets", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Confirm Booking")




