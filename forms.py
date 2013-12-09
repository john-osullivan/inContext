from flask.ext.wtf import Form
from models import Base, User

from wtforms import TextField, PasswordField, validators, SelectField, SelectMultipleField
from wtforms.validators import Required, EqualTo, Length, URL, Email

# Set your classes here.
class BaseForm(Form):
    class Meta:
        csrf = True

class RegisterForm(BaseForm):
    name = TextField('Username', validators = [Required(message = "Need username."), Length(min=6, max=25)])
    email   = TextField('Email', validators = [Required(message = "Need email."), Length(min=6, max=40), Email(message = "Not a valid email address.")])
    password    = PasswordField('Password', validators = [Required(message = "Need password."), Length(min=6, max=40)])
    url = TextField('URL', validators = [Required(message = "Specify a URL for your page to live at!"), Length(min=6, max=25)])
    confirm = PasswordField('Repeat Password', [Required(message = "Write that thang twice."), EqualTo('password', message='Passwords must match')])

    def validate_url(form, field):
        url_check = User.query.filter(User.url == field.data).first()
        if url_check != None:
            print "it's bitching about the URL not being unique!"
            raise ValidationError("URL suffix must be unique!")
        return True

class LoginForm(BaseForm):
    name        = TextField('Username', [Required()])
    password    = PasswordField('Password', [Required()])

class ForgotForm(BaseForm):
    email       = TextField('Email', validators = [Required(), Length(min=6, max=40)])

class CreateDetailForm(BaseForm):
    title = TextField('Title', validators = [Required(), Length(min=1, max=30)])
    aspect = SelectField('Aspect', validators = [Required()])
    text = TextField('Text', validators = [Length(min = 6, max = 420)])
    image = TextField('Image (URL)', validators = [Length(min=6, max=60), URL()])

class CreateAspectForm(BaseForm):
    title = TextField('Title', validators = [Required(), Length(min=1, max=30)])
    context = SelectMultipleField('Contexts')

class CreateContextForm(BaseForm):
    name = TextField('Name', validators = [Required(), Length(min=1, max=30)])

class AddAspectContextForm(BaseForm):
    aspect = SelectField('Aspect', validators = [Required()])
    context = SelectField('Context', validators = [Required()])

class RemoveAspectContextForm(BaseForm):
    aspect = SelectField('Aspect', validators = [Required()])
    context = SelectField('Context', validators = [Required()])

class CreateConnectionForm(BaseForm):
    yourContext = SelectField("Your Context", validators = [Required()])
    theirContext = SelectField("Their Context", validators = [Required()])