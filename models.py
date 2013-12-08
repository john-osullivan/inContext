from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from app import db

engine = create_engine('sqlite:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# Set your classes here.


class User(Base):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    url = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    bond = db.relationship("Bond")
    context = db.relationship("Context")
    lens = db.relationship("Lens")
    card = db.relationship("Card")

    def __init__(self, name, password, url):
        self.name = name
        self.password = password
        self.url = url

    def is_authenticated():
        return True

    def is_active():
        return True

    def is_anonymous():
        return False

    def get_id():
        return self.user_id

class Lens(Base):
    __tablename__ = 'lenses'

    lens_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    title = db.Column(db.String(120))
    card = db.relationship("Card")    

    def __init__(self, user_id, title):
        self.user_id = user_id
        self.title = title

class Card(Base):
    __tablename__ = 'cards'

    card_id = db.Column(db.Integer, primary_key = True)
    lens_id = db.Column(db.Integer, db.ForeignKey('lenses.lens_id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    title = db.Column(db.String(120))
    text = db.Column(db.String(2000))
    image = db.relationship("Image")

    def __init__(self, lens_id, user_id, title):
        self.lens_id = lens_id
        self.user_id = user_id
        self.title = title

class  Context(Base):
    __tablename__ = 'contexts'

    context_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    name = db.Column(db.String(30), nullable = False)
    lens = db.relationship('lens')

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

class Bond(Base):
    __tablename__ = 'bonds'

    bond_id = db.Column(db.Integer, primary_key = True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    user1_context = db.Column(db.Integer, db.ForeignKey('contexts.context_id'), nullable = False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    user2_context = db.Column(db.Integer, db.ForeignKey('contexts.context_id'), nullable = False)
    accepted = db.Column(db.Boolean)

    def __init__(self, user1_id, user1_context, user2_id, user2_context):
        self.user1_id = user1_id
        self.user1_context = user1_context
        self.user2_id = user2_id
        self.user2_context = user2_context
        self.accepted = False

class Image(Base):
    __tablename__ = 'images'

    image_id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(30), nullable = False)

    def __init__(self, url):
        this.url = url

# Create tables.
Base.metadata.create_all(bind=engine)
