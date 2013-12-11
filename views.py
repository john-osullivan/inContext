from models import *
from forms import *
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from flask.ext.login import login_user, current_user, logout_user
from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from app import app, db

@app.context_processor
def add_user():
    return dict(current_user = current_user)

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
        # Look for an existing connection between them
        try:
            connectionContext = Connection.query.filter(Connection.users.contains(pageUser)\
                                                                          ).filter(Connection.users.contains(viewUser)).one()
        # If there isn't one, return the Public context.
        except NoResultFound, e:
            public_context = Context.query.filter(Context.user_id == pageUser.user_id, Context.name == 'Public').one()
            return public_context.aspect
        
        # Otherwise, find the perspective of the pageUser, return the aspects spec'd by its context        
        else:
            perspectives_in_question = connectionContext.perspective            
            for perspective in perspectives_in_question:
                if perspective.user_id == pageUser.user_id:
                    return perspective.context.aspect

@app.route('/user/<profileURL>')
def getProfile(profileURL):
    from math import ceil
    user = User.query.filter(User.url == profileURL).one()
    user_aspects = getVisibleAspects(user, current_user)
    aspects = []
    for each in user_aspects:
        aspect_data = {'title': each.title}
        aspect_data['rows'] = []
        aspect_details = each.detail
        numRows = int(ceil(len(aspect_details) / 3.0))
        for i in range(numRows):
            row = []
            for j in range(3):
                try:
                    row.append(aspect_details[3 * i + j])
                except IndexError:
                    pass
            aspect_data['rows'].append(row)
            print row
        aspects.append(aspect_data)
    return render_template('pages/user_profile.html', user = user, aspects = aspects,
                                             yourPage = user.user_id == current_user.user_id, 
                                             profileURL = profileURL)
'''
METHODS TO ADD NEW OBJECTS
'''
@app.route('/user/<profileURL>/addDetail', methods=['GET','POST'])
def addDetail(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    form = CreateDetailForm(request.form)
    form.aspect.choices = [(aspect.aspect_id, aspect.title) for aspect in user.aspect]    
    if form.validate_on_submit():
        print "form.aspect.data: ",form.aspect.data
        aspect = Aspect.query.filter(Aspect.user_id == user.user_id, Aspect.aspect_id == int(form.aspect.data)).one()
        newDetail = Detail(aspect.aspect_id, user.user_id, form.title.data)
        if form.image.data != '':
            imageURL = form.image.data
            newImage = Image(imageURL)
            newDetail.image.append(newImage)
        newDetail.text = form.text.data
        user.detail.append(newDetail)
        aspect.detail.append(newDetail)
        db.session.add(newDetail)
        db.session.commit()
        flash("You just added a detail called " + request.form['title'] + "!")
        return redirect(url_for('getProfile', profileURL = profileURL))
    elif form.submitted():
        flash(form.errors)
    else:
        return render_template('forms/create_detail.html', form=form)

@app.route('/user/<profileURL>/addAspect', methods=['GET','POST'])
def addAspect(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    form = CreateAspectForm(request.form)
    form.context.choices = [(context.context_id, context.name) for context in user.context]
    if form.validate_on_submit():
        newAspect = Aspect(user.user_id, form.title.data)
        if form.context.data != []:
            for contextID in request.form['context']:
                Context.query.get(int(contextID)).aspect.append(newAspect)
        user.aspect.append(newAspect)
        db.session.add(newAspect)
        db.session.commit()
        flash("You just created an aspect called " + request.form['title'] + "!")
        return redirect(url_for('getProfile', profileURL = profileURL))
    elif form.submitted():
        flash(form.errors)
    else:
        return render_template('forms/create_aspect.html', form=form)

@app.route('/user/<profileURL>/addContext', methods=['GET','POST'])
def addContext(profileURL):
    form = CreateContextForm(request.form)
    user = User.query.filter(User.url == profileURL).one()
    if form.validate_on_submit():
        print "it's making contexts!"
        newContext = Context(user.user_id, request.form['name'])
        user.context.append(newContext)
        db.session.add(newContext)
        db.session.commit()
        flash("You just created a context called " + request.form['name'] + "!")
        return redirect(url_for('getProfile', profileURL = profileURL))
    elif form.submitted():
        flash(form.errors)
    else:
        return render_template('forms/create_context.html', form=form)


@app.route('/user/<profileURL>/addConnection')
def addConnection(profileURL, methods=["POST", "GET"]):

    # Helper function to create/find user perspectives to prevent duplication
    def check_for_perspective(user_id, context_id):
        perspective_check = Perspective.query.filter(Perspective.user_id == thisUser.user_id, Perspective.context_id == context_id).first()
        if perspective_check == None:
            newPerspective = Perspect(user_id, context_id)
            db.session.add(newPerspective)
            db.session.commit()
        else:
            newPerspective = perspective_check
        return newPerspective

    # Actual function
    form = CreateConnectionForm(request.form)
    otherUser = User.query.filter(User.url == profileURL).one()
    thisUser = current_user
    form.theirContext.choices = [(context.context_id, context.name) for context in otherUser.context]
    form.yourContext.choices = [(context.context_id, context.name) for context in thisUser.context]
    if form.validate_on_submit():
        yourPerspective = check_for_perspective(thisUser.user_id, int(form.yourContext.data))
        theirPerspective = check_for_perspective(otherUser.user_id, int(form.theirContext.data))
        newConnection = Connection()
        newConnection.users.append(thisUser.user_id)
        newConnection.users.append(otherUser.user_id)
        newConnection.perspective.append(yourPerspective)
        newConnection.perspective.append(theirPerspective)
        db.session.add(newConnection)
        db.session.commit()
        flash("It worked, connection made!")
        return redirect(url_for('getProfile', profileURL = profileURL))
    else:
        return render_template('forms/create_connection.html', form=form, profileURL = profileURL,
                                                                                                     other_user = otherUser)
        
'''
METHODS TO REMOVE OBJECTS (still not implemented in forms or html)
'''
@app.route('/user/<profileURL>/removeDetail', methods=['GET','POST'])
def removeDetail(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    detail = Detail.query.filter(Detail.card_id == int(request.form['detailID']))
    db.session.delete(detail)
    db.session.commit()
    return redirect(url_for('getProfile', profileURL = profileURL))

@app.route('/user/<profileURL>/removeAspect', methods=['GET','POST'])
def removeAspect(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    aspect = Aspect.query.filter(Aspect.aspect_id == int(request.form['aspectID']))
    db.session.delete(aspect)
    db.session.commit()
    return redirect(url_for('getProfile', profileURL = profileURL))

@app.route('/user/<profileURL>/removeContext', methods=['GET','POST'])
def removeContext(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    context = Context.query.filter(Context.context_id == int(request.form['contextID']))
    db.session.delete(context)
    db.session.commit()
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
        context = Context.query.get(int(form.context.data))
        aspect = Aspect.query.get(int(form.aspect.data))
        context.aspect.append(aspect)
        db.session.add(context)
        db.session.add(aspect)
        db.session.commit()
        flash("Aspect added!")
        return redirect(url_for('getProfile', profileURL = profileURL))
    elif form.submitted():
        flash(form.errors)        
    else:
        return render_template('forms/add_aspect_to_context.html', form=form)

@app.route('/user/<profileURL>/remove_aspect_from_context', methods=['GET','POST'])
def remove_aspect_from_context(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    form = RemoveAspectContextForm(request.form)
    form.aspect.choices = [(aspect.aspect_id, aspect.title) for aspect in user.aspect]
    form.context.choices = [(context.context_id, context.name) for context in user.context]    
    if form.validate_on_submit():
        context = Context.get(int(form.context.data))
        aspect = Aspect.get(int(form.aspect.data))
        context.aspect.remove(aspect)
        db.session.add(context)
        db.session.add(aspect)
        db.session.commit()
        flash("Aspect removed!")
        return redirect(url_for('getProfile', profileURL = profileURL))
    elif form.submitted():
        flash(form.errors)
    else:
        return render_template('forms/remove_aspect_from_context.html', form=form)


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
        flash("The form submitted but didn't validate :(")
    if form.validate():
        flash("And it's valid!")
    if form.validate_on_submit():
        user = User.query.filter(User.name == request.form['name']).one()
        if user.password == request.form['password']:
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for('getProfile', profileURL = user.url))
        else:
            flash("Incorrect username or password!")
            return redirect(url_for('getProfile', profileURL = user.url))
    else:
        return render_template('forms/login.html', form = form)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash("Logged out!")
    return redirect(url_for("home"))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        print "It validated, therefore the issue is within this logic."
        newUser = User(request.form['name'], request.form['email'], 
                                    request.form['password'], request.form['url'])
        print "The user was made freely."
        db.session.add(newUser)
        db.session.commit()
        public_context = Context(newUser.user_id, "Public")
        public_context.aspect.append(basic_info)
        basic_info = Aspect(newUser.user_id, "Basic Info")
        print "Their initial context and aspect were made."
        db.session.add(public_context)
        db.session.add(basic_info)
        db.session.commit()
        login_user(newUser)
        flash("It all worked, you're in the system!")
        return redirect(url_for('home'))
    elif form.is_submitted():
        flash("It submitted but didn't validate! :(")
        flash(form.errors)
        print "It was submitted with these errors:"
        print form.errors
    else:
        print "Shit ain't working!"
    return render_template('forms/register.html', form = form)

@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form = form)

# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    #db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html'), 404