from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, RadioField, DateTimeField, IntegerField
from wtforms.validators import InputRequired, Length, Email, EqualTo
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
                        choices=[('Category 1', 'Category 1'),
                                 ('Category 2', 'Category 2'),
                                 ('Category 3', 'Category 3')],   
                                 validators=[InputRequired('Choose category')])
    description=TextAreaField("Event Description", validators=[InputRequired('Enter description')])
    image = FileField('Destination Image', validators=[
        FileRequired(message = 'Image cannot be empty'),
        FileAllowed(ALLOWED_FILE, message='Only supports png, jpg, JPG, PNG')])
    date_time=DateTimeField("Event Date and Time", validators=[InputRequired('Date and Time required')], format='%D-%m-%Y %H:%M')
    ticket_price=IntegerField("Ticket Prices", validators=[InputRequired('Price must be set')])
    submit = SubmitField("Post", validators=[InputRequired()])

