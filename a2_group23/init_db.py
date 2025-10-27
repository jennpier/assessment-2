from website import db, create_app
from website.models import Category

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    categories = [
        "All", "Jazz", "Hip-Hop", "House", "Classical", "Rock", "Electronic", "Indie"
    ]

    for name in categories:
        if not Category.query.filter_by(category_name=name).first():
            db.session.add(Category(category_name=name))
    db.session.commit()
