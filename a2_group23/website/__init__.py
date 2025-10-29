# import flask - from 'package' import 'Class'
from flask import Flask 
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from pathlib import Path


db = SQLAlchemy()

# create a function that creates a web application
# a web server will run this web application
def create_app():
  
    app = Flask(__name__)  # this is the name of the module/package that is calling this app
    # Should be set to false in a production environment
    app.debug = True
    app.secret_key = 'somesecretkey'
    # set the app configuration data 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'
    # initialise db with flask app
    db.init_app(app)

    Bootstrap5(app)
    
    # initialise the login manager
    login_manager = LoginManager()
    
    # set the name of the login function that lets user login
    # in our case it is auth.login (blueprintname.viewfunction name)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    #Set upload folder for images
    UPLOAD_FOLDER = '/static/image'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # create a user loader function takes userid and returns User
    # Importing inside the create_app function avoids circular references
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
       return db.session.scalar(db.select(User).where(User.id==user_id))

    from . import views
    app.register_blueprint(views.main_bp)

    from . import auth
    app.register_blueprint(auth.auth_bp)

   # Added one more events blueprint.
    from .events import events_bp
    app.register_blueprint(events_bp)



    #To Make sure Images are saved at correct path

    app.config["UPLOAD_FOLDER"] = str(Path(app.root_path) / "static" / "images")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
    app.config["ALLOWED_IMAGE_EXTS"] = {"png", "jpg", "jpeg", "gif"}

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    

    return app
