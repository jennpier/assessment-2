from website import db, create_app
from website.models import Category, User
from flask_bcrypt import generate_password_hash

app = create_app()

with app.app_context():
    # Drop and recreate all tables
    db.drop_all()
    db.create_all()

    # I'm trying to add these categories by default
    categories = ["All", "Jazz", "Hip-Hop", "House", "Classical", "Rock", "Electronic", "Indie"]
    for name in categories:
        db.session.add(Category(category_name=name))

    # Creating a default admin user while database creation
    admin_user = User(
        name="admin",
        email="admin@admin.com",
        phone="0000",
        password_hash=generate_password_hash("123"),
        role="admin"
    )
    db.session.add(admin_user)

    db.session.commit()