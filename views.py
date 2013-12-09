from models import *
from forms import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import login_user, current_user
from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from app import app, db

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

def getVisibleAspects(pageUser, viewUser):
    if pageUser == viewUser:
        return pageUser.aspect
    else:
        connectionContext = Connection.query.filter(Connection.user1_id == viewUser.user_id,
                                            Connection.user2_id == pageUser.user_id).user2_context
        return connectionContext.aspect

@app.route('/user/<profileURL>')
def getProfile(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    user_aspects = getVisibleAspects(user, current_user)
    aspects = []
    for each in user_aspects:
        aspect = {'title': each.title}
        aspect[rows] = []
        aspect_cards = each.card
        numRows = math.ceil(len(aspect_cards) / 3)
        for i in range(numRows):
            row = []
            for j in range(3):
                try:
                    row.append(aspect_cards[3 * i + j])
                except IndexError:
                    pass
            aspect[rows].append(row)
    return render_template('pages/user_profile.html', user = user, aspects = aspects)
'''
METHODS TO ADD NEW OBJECTS
'''
@app.route('/user/<profileURL>/addDetail', methods=['GET','POST'])
def addDetail(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    form = CreateDetailForm(request.form)
    form.aspect.choices = [(aspect.aspect_id, aspect.title) for aspect in user.aspect]    
    if form.validate_on_submit():
        aspect = Aspect.query.filter(Aspect.user_id == user.user_id, Aspect.aspect == request.form['aspect']).one()
        newDetail = Detail(aspect.aspect_id, user.user_id, request.form['title'])
        if request.form['image'] != '':
            imageURL = request.form['image']
            newImage = Image(imageURL)
            newDetail.image.append(newImage)
        newDetail.text = request.form['text']
        user.card.append(newDetail)
        aspect.card.append(newDetail)
        db_session.add(newDetail)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))
    else:
        return render_template('create_detail.html', form=form)

@app.route('/user/<profileURL>/addAspect', methods=['GET','POST'])
def addAspect(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    form = CreateAspectForm(request.form)
    form.context.choices = [(context.context_id, context.name) for context in user.context]
    if form.validate_on_submit():
        newAspect = Aspect(user.user_id, request.form['aspectTitle'])
        if request.form['contexts'] != []:
            for contextID in request.form['contexts']:
                Context.get(int(contextID)).aspect.append(newAspect)
        user.aspect.append(newAspect)
        db_session.add(newAspect)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))
    else:
        return render_template('create_aspect.html', form=form)

@app.route('/user/<profileURL>/addContext', methods=['GET','POST'])
def addContext(profileURL):
    form = CreateContextForm(request.form)
    user = User.query.filter(User.url == profileURL).one()
    if form.validate_on_submit():
        newContext = Context(user.user_id, request.form['name'])
        user.context.append(newContext)
        db_session.add(newContext)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))
    else:
        return render_template('create_context.html', form=form)


@app.route('/user/<profileURL>/addConnection')
def addConnection(profileURL):
    form = CreateConnectionForm(request.form)
    otherUser = User.query.filter(User.url == profileURL)
    thisUser = current_user
    form.theirContext.choices = [(context.id, context.name) for context in otherUser.context]
    form.yourContext.choices = [(context.id, context.name) for context in thisUser.context]
    if form.validate_on_submit():
        firstWayConnection = Connection(thisUser.user_id, int(request.form['yourContext']),
                                                            otherUser.user_id, int(request.form['theirContext']), True)
        secondWayConnection = Connection(otherUser.user_id, int(request.form['theirContext']),
                                                            thisUser.user_id, int(request.form['yourContext']), True)
        
        db_session.add(firstWayConnection)
        db_session.add(secondWayConnection)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))
'''
METHODS TO REMOVE OBJECTS (still not implemented in forms or html)
'''
@app.route('/user/<profileURL>/removeDetail', methods=['GET','POST'])
def removeDetail(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    detail = Detail.query.filter(Detail.card_id == int(request.form['detailID']))
    db_session.delete(detail)
    db_session.commit()
    return redirect(url_for('getProfile', profileURL = profileURL))

@app.route('/user/<profileURL>/removeAspect', methods=['GET','POST'])
def removeAspect(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    aspect = Aspect.query.filter(Aspect.aspect_id == int(request.form['aspectID']))
    db_session.delete(aspect)
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
@app.route('/user/<profileURL>/add_aspect_to_context', methods=['GET','POST'])
def add_aspect_to_context(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    form = AddAspectContextForm(request.form)
    form.aspect.choices = [(aspect.aspect_id, aspect.title) for aspect in user.aspect]
    form.context.choices = [(context.context_id, context.name) for context in user.context]
    if form.validate_on_submit():
        context = Context.get(int(request.form['Context']))
        aspect = Aspect.get(int(request.form['Aspect']))
        context.aspect.append(aspect)
        db_session.add(context)
        db_session.add(aspect)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))
    else:
        return render_template('add_aspect_to_context.html', form=form)

@app.route('/user/<profileURL>/remove_aspect_from_context', methods=['GET','POST'])
def remove_aspect_from_context(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    form = RemoveAspectContextForm(request.form)
    form.aspect.choices = [(aspect.aspect_id, aspect.title) for aspect in user.aspect]
    form.context.choices = [(context.context_id, context.name) for context in user.context]    
    if form.validate_on_submit():
        context = Context.get(int(request.form['Context']))
        aspect = Aspect.get(int(request.form['Aspect']))
        context.aspect.remove(aspect)
        db_session.add(context)
        db_session.add(aspect)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))
    else:
        return render_template('remove_aspect_from_context.html', form=form)


# Controllers & Basics
@app.route('/')
def home():
    return render_template('pages/home.html')

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.is_submitted():
        flash("The form submitted...")
        print "submitted form."
    if form.validate():
        flash("And it's valid!")
        print "validated form"
    if form.validate_on_submit():
        user = User.query.filter(User.name == request.form['name']).one()
        print "queried database to find user"
        if user.password == request.form['password']:
            login_user(user)
            print "login should happen"
            flash("Logged in successfully.")
            return redirect(url_for('getProfile', profileURL = user.url))
        else:
            flash("Incorrect username or password!")
            return redirect(url_for('getProfile', profileURL = user.url))
    else:
        flash("Not a valid input.")
        return render_template('forms/login.html', form = form)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.is_submitted():
        flash("The form submitted...")
    if form.validate():
        flash("And it's valid!")
    else:
        flash("Didn't validate :(")
    if form.validate_on_submit():
        newUser = User(request.form['name'], request.form['email'], 
                                    request.form['password'], request.form['url'])
        db_session.add(newUser)
        db_session.commit()
        flash("It all worked, you're in the system!")
        return redirect(url_for('home'))
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