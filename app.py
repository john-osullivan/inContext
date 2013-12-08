#----------------------------------------------------------------------------#
# Imports.
#----------------------------------------------------------------------------#

from flask import * # do not use '*'; actually input the dependencies.
from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def home():
    return render_template('pages/home.html')

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form = form)


@app.route('/user/<profileURL>')
def getProfile(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    user_lenses = user.lens
    lenses = []
    for each in user_lenses:
        lens = {'title': each.title}
        lens[rows] = []
        lens_cards = each.card
        numRows = math.ceil(len(lens_cards) / 3)
        for i in range(numRows):
            row = []
            for j in range(3):
                try:
                    row.append(lens_cards[3 * i + j])
                except IndexError:
                    pass
            lens[rows].append(row)
    return render_template('pages/user_profile', user = user, lenses = lenses)
'''
METHODS TO ADD NEW OBJECTS
'''
@app.route('/user/<profileURL>/addCard', methods=['GET','POST'])
def addCard(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    if request.method == 'GET':
        form = CreateCardForm(request.form)
        form.lens.choices = [(lens.lens_id, lens.title) for lens in user.lens]
        # Populate select listing here
        return render_template('create_card.html', form=form)
    elif request.method == "POST":      
        lens = Lens.query.filter(Lens.user_id == user.user_id, Lens.lens_id == request.form['lensName']).one()
        newCard = Card(lens.lens_id, user.user_id, request.form['cardTitle'])
        if request.form['image'] != '':
            imageURL = request.form['image']
            newImage = Image(imageURL)
            newCard.image.append(newImage)
        newCard.text = request.form['text']
        user.card.append(newCard)
        lens.card.append(newCard)
        db_session.add(newCard)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))

@app.route('/user/<profileURL>/addLens', methods=['GET','POST'])
def addLens(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    if request.method == 'GET':
        form = CreateLensForm(request.form)
        form.context.choices = [(context.context_id, context.name) for context in user.context]
        return render_template('create_lens.html', form=form)
    elif request.method == 'POST':
        newLens = Lens(user.user_id, request.form['lensTitle'])
        if request.form['contexts'] != []:
            for contextID in request.form['contexts']:
                Context.get(int(contextID)).lens.append(newLens)
        user.lens.append(newLens)
        db_session.add(newLens)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))

@app.route('user/<profileURL>/addContext', methods=['GET','POST'])
def addContext(profileURL):
    if request.method == 'GET':
        form = CreateContextForm(request.form)
        return render_template('create_context.html', form=form)
    elif request.method == 'POST':
        user = User.query.filter(User.url == profileURL).one()
        newContext = Context(user.user_id, request.form['contextName'])
        user.context.append(newContext)
        db_session.add(newContext)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))

'''
METHODS TO REMOVE OBJECTS
'''
@app.route('/user/<profileURL>/removeCard', methods=['GET','POST'])
def removeCard(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    card = Card.query.filter(Card.card_id == int(request.form['cardID']))
    db_session.delete(card)
    db_session.commit()
    return redirect(url_for('getProfile', profileURL = profileURL))

@app.route('/user/<profileURL>/removeLens', methods=['GET','POST'])
def removeLens(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    lens = Lens.query.filter(Lens.lens_id == int(request.form['lensID']))
    db_session.delete(lens)
    db_session.commit()
    return redirect(url_for('getProfile', profileURL = profileURL))

@app.route('/user/<profileURL>/removeContext', methods=['GET','POST'])
def removeContext(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    context = Context.query.filter(Context.context_id == int(request.form['contextID']))
    db_session.delete(context)
    db_session.commit()
    return redirect(url_for('getProfile', profileURL = profileURL))

'''
METHODS TO CHANGE CONTENTS OF CONTEXT
'''
@app.route('user/<profileURL>/add_lens_to_context', methods=['GET','POST'])
def add_lens_to_context(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    if method == 'GET':
        form = AddLensContextForm(request.form)
        form.lens.choices = [(lens.lens_id, lens.title) for lens in user.lens]
        form.context.choices = [(context.context_id, context.name) for context in user.context]
        return render_template('add_lens_to_context.html', form=form)
    elif method == 'POST':
        context = Context.get(int(request.form['contextID']))
        lens = Lens.get(int(request.form['lensID']))
        context.lens.append(lens)
        db_session.add(context)
        db_session.add(lens)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))

@app.route('user/<profileURL>/remove_lens_from_context', methods=['GET','POST'])
def remove_lens_from_context(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    if method == 'GET':
        form = RemoveLensContextForm(request.form)
        form.lens.choices = [(lens.lens_id, lens.title) for lens in user.lens]
        form.context.choices = [(context.context_id, context.name) for context in user.context]
        return render_template('remove_lens_from_context.html', form=form)
    elif method == 'POST':
        context = Context.get(int(request.form['contextID']))
        lens = Lens.get(int(request.form['lensID']))
        context.lens.remove(lens)
        db_session.add(context)
        db_session.add(lens)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))

@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form = form)

@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form = form)

# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
