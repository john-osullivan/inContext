from flask.ext.wtf import Form
from models import Base, User

from wtforms import TextField, PasswordField, validators, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import Required, EqualTo, Length, URL, Email, Optional

# Set your classes here.
class BaseForm(Form):
    class Meta:
        csrf = True

class RegisterForm(BaseForm):
    name = TextField('Username', validators = [Required(message = "Need username."), Length(min=6, max=25)])
    password    = PasswordField('Password', validators = [Required(message = "Need password."), Length(min=6, max=40)])
    url = TextField('URL', validators = [Required(message = "Specify a URL for your page to live at!"), Length(min=3, max=25)])
    confirm = PasswordField('Repeat Password', [Required(message = "Write that thang twice."), EqualTo('password', message='Passwords must match')])

    def validate_url(form, field):
        print "it got to the validation function"
        url_check = User.query.filter(User.url == field.data).first()
        print "it queried the database in validation"
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
    aspect = SelectField('Aspect', validators = [Required()], coerce = int)
    text = TextAreaField('Text', validators = [Length(min = 6, max = 420)])
    image = TextField('Image (URL)', validators = [Optional(), URL()])

class CreateAspectForm(BaseForm):
    title = TextField('Title', validators = [Required(), Length(min=1, max=30)])
    context = SelectMultipleField('Contexts', coerce = int)

class CreateContextForm(BaseForm):
    name = TextField('Name', validators = [Required(), Length(min=1, max=30)])

class AddAspectContextForm(BaseForm):
    aspect = SelectField('Aspect', validators = [Required()], coerce=int)
    context = SelectField('Context', validators = [Required()], coerce = int)

class RemoveAspectContextForm(BaseForm):
    aspect = SelectField('Aspect', validators = [Required()], coerce = int)
    context = SelectField('Context', validators = [Required()], coerce = int)

class CreateConnectionForm(BaseForm):
    yourContext = SelectField("Your Context", validators = [Required()], coerce = int)
    theirContext = SelectField("Their Context", validators = [Required()], coerce = int)