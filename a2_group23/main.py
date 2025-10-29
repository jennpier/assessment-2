from website import create_app, db
from website.models import User
from flask_bcrypt import generate_password_hash

# NEED TO GET RID OF THIS SOMEHOW - SO DON'T HAVE TO REBUILD DB EVERY TIME
# This method will create a web application database
def init_database(app):
    with app.app_context():
        # drop and recreate all tables. 
        # Guys, comment line 13/14 while pushing in pythonanywhere. We don't want to lose data everytime we run our application
        # I'm keeping this because I'm still unsure what to do. 
        db.drop_all()
        db.create_all()

        # I'm addming these categories by default
        #categories = ["All", "Jazz", "Hip-Hop", "House", "Classical", "Rock", "Electronic", "Indie"]
        #for name in categories:
        #    db.session.add(Category(category_name=name))

        # Creating a default admin user
        admin_user = User(
            name="admin",
            email="admin@admin.com",
            phone="0000",
            password_hash=generate_password_hash("123"),
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()


if __name__ == '__main__':
    app = create_app()

    # Running database first. 
    init_database(app)

    # running the app
    app.run()

    