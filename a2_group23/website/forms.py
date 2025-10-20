from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, RadioField, DateTimeField, IntegerField
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired

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
    ticket_type=RadioField("Ticket type",
                           choices=[('type option 1', 'Ticket Type eg1'),
                                    ('type option 2', 'Ticket Type eg2'),
                                    ('type option 3', 'Ticket Type eg3')])
    ticket_price=IntegerField("Ticket Prices", validators=[InputRequired('Price must be set')])
    total_tickets=IntegerField("Number of tickets", validators=[InputRequired(), NumberRange(min=1)])    
    submit = SubmitField("Post")

class BookingForm(FlaskForm):
    ticket_type=RadioField("Ticket type", 
                           choices=[('ticket type 1', 'Ticket Type eg1'),
                                    ('ticket type 2', 'Ticket Type eg2'),
                                    ('ticket type 3', 'Ticket Type eg3')
                           ],
                           validators=[InputRequired()])
    no_tickets=IntegerField("Number of tickets", validators=[InputRequired(), NumberRange(min=1)])
    submit=SubmitField("Buy")


