#----------------------------------------------------------------------------#
# Imports.
#----------------------------------------------------------------------------#

from flask import * # do not use '*'; actually input the dependencies.
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user
import logging
from logging import Formatter, FileHandler



#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.needs_refresh_message = (
    u"You have to log in again to protect your account, sorry!")

from models import *
from forms import *
from views import *

# Automatically tear down SQLAlchemy.
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

# Get users for flask-login
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

# Let users refresh their authentication
@login_manager.needs_refresh_handler
def refresh():
    return redirect(url_for('login'))

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
