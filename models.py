from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean

engine = create_engine('sqlite:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# Set your classes here.


class User(Base):
    __tablename__ = 'users'

    user_id =  Column( Integer, primary_key=True)
    name =  Column( String(120), unique=True)
    email =  Column( String(120), unique=True)
    url =  Column( String(30), unique=True)
    password =  Column( String(30))
    connection =  relationship("connections")
    context =  relationship("contexts")
    aspect =  relationship("aspects")
    detail =  relationship("details")

    def __init__(self, name, email, password, url):
        self.name = name
        self.email = email
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

class Aspect(Base):
    __tablename__ = 'aspects'

    aspect_id =  Column( Integer, primary_key = True)
    user_id =  Column( Integer,  ForeignKey('users.user_id'), nullable = False)
    title =  Column( String(120))
    detail =  relationship("details")    

    def __init__(self, user_id, title):
        self.user_id = user_id
        self.title = title

class Detail(Base):
    __tablename__ = 'details'

    detail_id =  Column( Integer, primary_key = True)
    aspect_id =  Column( Integer,  ForeignKey('aspects.aspect_id'), nullable = False)
    user_id =  Column( Integer,  ForeignKey('users.user_id'), nullable = False)
    title =  Column( String(120))
    text =  Column( String(2000))
    image =  relationship("images")

    def __init__(self, aspect_id, user_id, title):
        self.aspect_id = aspect_id
        self.user_id = user_id
        self.title = title

class  Context(Base):
    __tablename__ = 'contexts'

    context_id =  Column( Integer, primary_key = True)
    user_id =  Column( Integer,  ForeignKey('users.user_id'), nullable = False)
    name =  Column( String(30), nullable = False)
    aspect =  relationship('aspects')

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

class Connection(Base):
    __tablename__ = 'connections'

    connection_id =  Column( Integer, primary_key = True)
    user1_id =  Column( Integer,  ForeignKey('users.user_id'), nullable = False)
    user1_context =  Column( Integer,  ForeignKey('contexts.context_id'), nullable = False)
    user2_id =  Column( Integer,  ForeignKey('users.user_id'), nullable = False)
    user2_context =  Column( Integer,  ForeignKey('contexts.context_id'), nullable = False)
    accepted =  Column( Boolean)

    def __init__(self, user1_id, user1_context, user2_id, user2_context):
        self.user1_id = user1_id
        self.user1_context = user1_context
        self.user2_id = user2_id
        self.user2_context = user2_context
        self.accepted = False

class Image(Base):
    __tablename__ = 'images'

    image_id =  Column( Integer, primary_key = True)
    detail_id = Column(Integer, ForeignKey('details.detail_id'))
    url =  Column( String(30), nullable = False)

    def __init__(self, url):
        this.url = url

# Create tables.
Base.metadata.create_all(bind=engine)
