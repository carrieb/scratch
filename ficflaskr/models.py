from ficflaskr import db, app
from datetime import datetime
import json

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	email = db.Column(db.String(120), unique=True)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.id)
		except NameError:
			return str(self.id)

	def __init__(self, username, email):
		self.username = username
		self.email = email

	def __repr__(self):
		return '<User %r>' % self.username

class Fic(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(80))
	summary = db.Column(db.String(300))
	url = db.Column(db.String(120))
	pub_date = db.Column(db.DateTime)
	upd_date = db.Column(db.DateTime)

	favorite_cnt = db.Column(db.Integer)
	follow_cnt = db.Column(db.Integer)
	word_cnt = db.Column(db.Integer)
	chapter_cnt = db.Column(db.Integer)

	author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
	author = db.relationship('Author', backref=db.backref('fics', lazy='dynamic'))

	def __init__(self, title, summary, url, author, pub_date, upd_date):
		self.title = title
		self.summary = summary
		self.url = url
		self.pub_date = pub_date
		self.upd_date = upd_date
		self.author = author

	def __repr__(self):
		return '<Fic %r>' % self.title

class Author(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True)
	url = db.Column(db.String(50))

	def __init__(self, name, url):
		self.name = name
		self.url = url

	def __repr__(self):
		return '<Author %r>' % self.name

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def get_or_create_author(name, url):
	author = Author.query.filter_by(name=name).first()
	if author:
		return author
	else:
		author = Author(name, url)
		db.session.add(author)
		return author

def get_or_create_fic(title, summary, url, author, publish_ts, update_ts):
	fic = Fic.query.filter_by(url=url).first()
	if fic:
		return fic
	else:
		fic = Fic(title, summary, url, author, datetime.fromtimestamp(publish_ts), datetime.fromtimestamp(update_ts))
		db.session.add(fic)
		return fic

def populate_db_from_file(filename=app.config['DB_BACKUP']):
	with app.open_resource(app.config['DB_BACKUP'], mode='r') as f:
		json_obj = json.load(f)
		for fic in json_obj:
			# Add author
			author_name = fic['author']
			author = get_or_create_author(author_name, '')
			db.session.add(author)

			fic = get_or_create_fic(fic['title'], fic['summary'], fic['url'], author, fic['publish_ts'], fic['update_ts'])
			db.session.add(fic)
		db.session.commit()
		# Check
		authors = Author.query.order_by(Author.name).all()
		anAuthorsFics = Author.query.first().fics
		fics = Fic.query.order_by(Fic.title).all()
		print authors
		print anAuthorsFics
		print fics

def format_ts(ts, typ):
	dt = datetime.fromtimestamp(ts)
	string = dt.strftime('%m-%d-%Y')
	print typ, string
	return string
