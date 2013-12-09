from flask.ext.wtf import Form

from wtforms import TextField, PasswordField, validators
from wtforms.validators import Required, EqualTo, Length

# Set your classes here.

class RegisterForm(Form):
    name        = TextField('Username', validators = [Required(), Length(min=6, max=25)])
    email       = TextField('Email', validators = [Required(), Length(min=6, max=40)])
    password    = PasswordField('Password', validators = [Required(), Length(min=6, max=40)])
    confirm     = PasswordField('Repeat Password', [Required(), EqualTo('password', message='Passwords must match')])

class LoginForm(Form):
    name        = TextField('Username', [Required()])
    password    = PasswordField('Password', [Required()])

class ForgotForm(Form):
    email       = TextField('Email', validators = [Required(), Length(min=6, max=40)])

class CreateDetailForm(Form):
    title = TextField('Title', validators = [Required(), Length(min=1, max=30)])
    lens = SelectField('Lens', validators = [Required()])
    text = TextField('Text', validators = [Length(min = 6, max = 420)])
    image = Text('Image (URL)', validators = [Length(min=6, max=60)])

class CreateLensForm(Form):
    title = TextField('Title', validators = [Required(), Length(min=1, max=30)])
    context = SelectMultipleField('Contexts')

class CreateContextForm(Form):
    name = TextField('Name', validators = [Required(), Length(min=1, max=30)])

class AddLensContextForm(Form):
    lens = SelectField('Lens', validators = [Required()])
    context = SelectField('Context', validators = [Required()])

class RemoveLensContextForm(Form):
    lens = SelectField('Lens', validators = [Required()])
    context = SelectField('Context', validators = [Required()])