from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

# Create a blueprint - make sure all BPs have unique names
auth_bp = Blueprint('auth', __name__)

# this is a hint for a login function
@auth_bp.route('/login', methods=['GET', 'POST'])
# view function
def login():
    login_form = LoginForm()
    error = None
    if login_form.validate_on_submit():
        user_name = login_form.user_name.data
        password = login_form.password.data
        user = db.session.scalar(db.select(User).where(User.name==user_name))
        if user is None:
            error = 'Incorrect user name'
        elif not check_password_hash(user.password_hash, password): # takes the hash and cleartext password
            error = 'Incorrect password'
        if error is None:
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            nextp = request.args.get('next')
            if not nextp or not nextp.startswith('/'):
                # if user.role == "admin":
                #     return redirect(url_for('admin.dashboard'))
                return redirect(url_for('main.index'))
            return redirect(nextp)
        else:
            flash(error, "danger")
    return render_template('user.html', form=login_form, heading='Login')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit(): 
        # Check if email or username already exists
        existing_email = db.session.scalar(db.select(User).where(User.email == form.email.data))
        existing_user = db.session.scalar(db.select(User).where(User.name == form.user_name.data))

        if existing_email:
            flash("That email is already registered. Please log in instead.", "warning")
            return redirect(url_for('auth.login'))

        if existing_user:
            flash("That username is already taken. Please choose a different one.", "warning")
            return redirect(url_for('auth.register'))

        # Password hashing for security
        hashed_password = generate_password_hash(form.password.data)

        # Creating new user record
        new_user = User(
            name=form.user_name.data,
            email=form.email.data,
            phone=form.phone.data,
            password_hash=hashed_password,
            role='user'  # Default role of user is given
        )

        db.session.add(new_user)
        db.session.commit()

        # Confirmation message after successful registration
        flash("Registration successful! You can now log in.", "success")  
        return redirect(url_for('auth.login'))

    # Show the registration form again if invalid
    return render_template('user.html', form=form, heading='Register')


            
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()  # Clears the user session
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))



