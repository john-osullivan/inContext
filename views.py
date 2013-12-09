from models import *
from forms import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, request, session, g, redirect, url_for,\
     abort, render_template, flash, make_response
from app import app, db

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
    user_aspects = user.aspect
    aspects = []
    for each in user_aspects:
        aspect = {'title': each.title}
        lens[rows] = []
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
    return render_template('pages/user_profile', user = user, aspects = aspects)
'''
METHODS TO ADD NEW OBJECTS
'''
@app.route('/user/<profileURL>/addDetail', methods=['GET','POST'])
def addDetail(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    if request.method == 'GET':
        form = CreateDetailForm(request.form)
        form.aspect.choices = [(aspect.aspect_id, aspect.title) for aspect in user.aspect]
        # Populate select listing here
        return render_template('create_detail.html', form=form)
    elif request.method == "POST":      
        aspect = Aspect.query.filter(Aspect.user_id == user.user_id, Aspect.aspect == request.form['aspect']).one()
        newDetail = Detail(lens.lens_id, user.user_id, request.form['title'])
        if request.form['image'] != '':
            imageURL = request.form['image']
            newImage = Image(imageURL)
            newDetail.image.append(newImage)
        newDetail.text = request.form['text']
        user.card.append(newDetail)
        lens.card.append(newDetail)
        db_session.add(newDetail)
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
        newContext = Context(user.user_id, request.form['name'])
        user.context.append(newContext)
        db_session.add(newContext)
        db_session.commit()
        return redirect(url_for('getProfile', profileURL = profileURL))

'''
METHODS TO REMOVE OBJECTS
'''
@app.route('/user/<profileURL>/removeDetail', methods=['GET','POST'])
def removeDetail(profileURL):
    user = User.query.filter(User.url == profileURL).one()
    detail = Detail.query.filter(Detail.card_id == int(request.form['detailID']))
    db_session.delete(detail)
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