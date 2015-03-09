from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired

class LoginForm(Form):
	openid = StringField('openid', validators=[DataRequired()])
	remember_me = BooleanField('remember_me', default=False)

class FilterForm(Form):
	genre = SelectMultipleField('genre', [])
	characters = SelectMultipleField('characters', [])
	pairings = SelectMultipleField('pairings', [])
	word_cnt = IntegerField('word_cnt')
