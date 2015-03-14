from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Optional

class FilterForm(Form):
	# Autocomplete strings
	saved_filters_autocomplete = StringField('saved filters autocomplete')
	character_autocomplete = StringField('character autocomplete')
	genre_autocomplete = StringField('genre autocomplete')
	pairing_autocomplete = StringField('pairing autocomplete')

	# Boolean fields
	one_shot = BooleanField('one chapter')
	complete = BooleanField('complete')

	# Scalar fields
	word_min = IntegerField('word min')
	word_max = IntegerField('word max')
	avg_chapter_length_min = IntegerField('min avg words per chapter')

