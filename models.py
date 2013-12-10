from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table

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
    connection =  relationship("Connection")
    perspective = relationship("Perspective")
    context =  relationship("Context")
    aspect =  relationship("Aspect")
    detail =  relationship("Detail")

    def __init__(self, name, email, password, url):
        self.name = name
        self.email = email
        self.password = password
        self.url = url

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id

class Detail(Base):
    __tablename__ = 'details'

    detail_id =  Column( Integer, primary_key = True)
    aspect_id =  Column( Integer,  ForeignKey('aspects.aspect_id'), nullable = False)
    user_id =  Column( Integer,  ForeignKey('users.user_id'), nullable = False)
    title =  Column( String(120))
    text =  Column( String(2000))
    image =  relationship("Image")

    def __init__(self, aspect_id, user_id, title):
        self.aspect_id = aspect_id
        self.user_id = user_id
        self.title = title

'''
Here goes the code holding together contexts and aspects -- items and sets, basically.
'''

contexts_to_aspects = Table('contexts_to_aspects', Base.metadata,
    Column('context_id', Integer, ForeignKey('contexts.context_id')),
    Column('aspect_id', Integer, ForeignKey('aspects.aspect_id'))
    )

class  Context(Base):
    __tablename__ = 'contexts'

    context_id =  Column( Integer, primary_key = True)
    user_id =  Column( Integer,  ForeignKey('users.user_id'), nullable = False)
    name =  Column( String(30), nullable = False)
    aspect =  relationship('Aspect', secondary=contexts_to_aspects, backref='contexts')

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

class Aspect(Base):
    __tablename__ = 'aspects'

    aspect_id =  Column( Integer, primary_key = True)
    user_id =  Column( Integer,  ForeignKey('users.user_id'), nullable = False)
    title =  Column( String(120), nullable = False)
    detail =  relationship("Detail")    

    def __init__(self, user_id, title):
        self.user_id = user_id
        self.title = title

'''
Here goes the perspective connection stuff, which is more meant to be like 
halves of a whole or something.
'''

perspectives_to_connections = Table('perspectives_to_connections', Base.metadata,
    Column('connection_id', Integer, ForeignKey('connections.connection_id')),
    Column('perspective_id', Integer, ForeignKey('perspectives.perspective_id'))
    )

class Perspective(Base):
    __tablename__ = 'perspectives'

    perspective_id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable = False)
    context_id = Column(Integer, ForeignKey('contexts.context_id'), nullable = False)

    def __init__(self, user_id, context_id):
        self.user_id = user_id
        self.context_id = context_id

class Connection(Base):
    __tablename__ = 'connections'
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(['first_user_id'], ['users.user_id']),
        sqlalchemy.ForeignKeyConstraint(['second_user_id'], ['users.user_id']),
        {'autoload': True, 'useexisting': True})
    connection_id =  Column( Integer, primary_key = True)
    perspective = relationship('Perspective', secondary = 'perspectives_to_connections',
                                                    backref = 'connections')
    accepted =  Column( Boolean)

    def __init__(self):
        self.accepted =  False

class Image(Base):
    __tablename__ = 'images'

    image_id =  Column( Integer, primary_key = True)
    detail_id = Column(Integer, ForeignKey('details.detail_id'))
    url =  Column( String(300), nullable = False)

    def __init__(self, url):
        self.url = url

# Create tables.
Base.metadata.create_all(bind=engine)
