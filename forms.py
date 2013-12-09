from flask.ext.wtf import Form
from models import Base, User

from wtforms import TextField, PasswordField, validators
from wtforms.validators import Required, EqualTo, Length

# Set your classes here.

class RegisterForm(Form):
    name        = TextField('Username', validators = [Required(), Length(min=6, max=25)])
    email       = TextField('Email', validators = [Required(), Length(min=6, max=40)])
    password    = PasswordField('Password', validators = [Required(), Length(min=6, max=40)])
    url = TextField('URL', validators = [Required(), Length(min=)])
    confirm     = PasswordField('Repeat Password', [Required(), EqualTo('password', message='Passwords must match')])

    def validate_url(form, field):
        url_check = User.query.filter(User.url == field.data).first()
        if url_check:
            raise ValidationError("URL suffix must be unique!")

class LoginForm(Form):
    name        = TextField('Username', [Required()])
    password    = PasswordField('Password', [Required()])

class ForgotForm(Form):
    email       = TextField('Email', validators = [Required(), Length(min=6, max=40)])

class CreateDetailForm(Form):
    title = TextField('Title', validators = [Required(), Length(min=1, max=30)])
    aspect = SelectField('Aspect', validators = [Required()])
    text = TextField('Text', validators = [Length(min = 6, max = 420)])
    image = Text('Image (URL)', validators = [Length(min=6, max=60), URL()])

class CreateAspectForm(Form):
    title = TextField('Title', validators = [Required(), Length(min=1, max=30)])
    context = SelectMultipleField('Contexts')

class CreateContextForm(Form):
    name = TextField('Name', validators = [Required(), Length(min=1, max=30)])

class AddAspectContextForm(Form):
    aspect = SelectField('Aspect', validators = [Required()])
    context = SelectField('Context', validators = [Required()])

class RemoveAspectContextForm(Form):
    aspect = SelectField('Aspect', validators = [Required()])
    context = SelectField('Context', validators = [Required()])

class CreateConnectionForm(Form):
    yourContext = SelectField("Your Context", validators = [Required()])
    theirContext = SelectField("Their Context", validators = [Required()])