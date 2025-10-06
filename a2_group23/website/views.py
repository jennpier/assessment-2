from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template("Index.html")

#change to it's own event.py file - include /update-event and /events?
@main_bp.route('/create-event', methods = ['GET', 'POST'])
def create_event():
  print('Method type: ', request.method)
  form = EventForm()
  if form.validate_on_submit():
    db_file_path = check_upload_file(form)    
    event = Event(title=form.title.data,
                  category=form.category.data,
                  description=form.description.data,
                  image=form.image.data,
                  date_time=form.date_time.data,
                  ticket_price=form.ticket_price.data
                  )
    db.session.add(event)
    db.session.commit()
    print('Successfully created new event')
    return redirect(url_for('event.create_event'))
  return render_template('/<id>/create_event.html', form=form)

@main_bp.route('/update-event')
def update_event():
    return render_template()


