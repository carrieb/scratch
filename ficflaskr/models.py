from ficflaskr import db, app
from datetime import datetime
import json
import collections

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

characters = db.Table('characters',
    db.Column('fic_id', db.Integer, db.ForeignKey('fic.id')),
    db.Column('character_id', db.Integer, db.ForeignKey('character.id'))
)

fic_pairings = db.Table('fic_pairings',
	db.Column('fic_id', db.Integer, db.ForeignKey('fic.id')),
	db.Column('pairing_id', db.Integer, db.ForeignKey('pairing.id'))
)

genres = db.Table('genres',
	db.Column('fic_id', db.Integer, db.ForeignKey('fic.id')),
	db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
)

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
	review_cnt = db.Column(db.Integer)

	completed = db.Column(db.Boolean)

	author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
	rating_id = db.Column(db.Integer, db.ForeignKey('rating.id'))

	genres = db.relationship('Genre', secondary=genres,
			backref=db.backref('fics', lazy='dynamic'))

	characters = db.relationship('Character', secondary=characters,
			backref=db.backref('fics', lazy='dynamic'))

	pairings = db.relationship('Pairing', secondary=fic_pairings,
			backref=db.backref('fics', lazy='dynamic'))

	def __init__(self, title, summary, url, author, pub_date, upd_date):
		self.title = title
		self.summary = summary
		self.url = url
		self.pub_date = pub_date
		self.upd_date = upd_date
		self.author = author
		self.completed = False

	def __repr__(self):
		return '<Fic %r>' % self.title

	def allSimpleFields(self):
		return '<%r by %r, Ra:%r, W: %r, C: %r, R: %r, Fa: %r, Fo: %r, Complete:%r>' % (self.title, self.author.name, self.rating.name, self.word_cnt, self.chapter_cnt, self.review_cnt, self.favorite_cnt, self.follow_cnt, self.completed)

class Author(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True)
	url = db.Column(db.String(50))
	fics = db.relationship('Fic', backref='author', lazy='dynamic')

	def __init__(self, name, url):
		self.name = name
		self.url = url

	def __repr__(self):
		return '<Author %r>' % self.name

class Genre(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Genre %r>' % self.name

class Rating(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True)
	fics = db.relationship('Fic', backref='rating', lazy='dynamic')

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Rating %r>' % self.name

pairings = db.Table('pairings',
    db.Column('pairing_id', db.Integer, db.ForeignKey('pairing.id')),
    db.Column('character_id', db.Integer, db.ForeignKey('character.id'))
)

class Character(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True)
	pairings = db.relationship('Pairing', secondary=pairings,
			backref=db.backref('characters', lazy='dynamic'))

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Character %r>' % self.name

class Pairing(db.Model):
	id = db.Column(db.Integer, primary_key=True)

	def __repr__(self):
		return '<Pairing %r>' % map(lambda s: s.name, self.characters)

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

def get_or_create_genre(name):
	genre = Genre.query.filter_by(name=name).first()
	if genre:
		return genre
	else:
		genre = Genre(name)
		db.session.add(genre)
		return genre

def get_or_create_rating(name):
	rating = Rating.query.filter_by(name=name).first()
	if rating:
		return rating
	else:
		rating = Rating(name)
		db.session.add(rating)
		return rating

def get_or_create_character(name):
	character = Character.query.filter_by(name=name).first()
	if character:
		return character
	else:
		character = Character(name)
		db.session.add(character)
		return character

def create_pairing(characters):
	pairing = Pairing()
	for c in characters:
		pairing.characters.append(c)
	return pairing

def get_or_create_pairing(characters):
	query = Pairing.query.filter(Pairing.characters.any(Character.name == characters[0].name))
	for pairing in query.all():
		if collections.Counter(characters) == collections.Counter(pairing.characters):
			return pairing
	else:
		return create_pairing(characters)

def update_from_meta(meta, fic):
        split = meta.split(' - ')
        for i in range(len(split)):
            item = split[i].strip()
            if ':' in item:
                try_updating_counts(item, fic)
            else:
                if item == "English":
                    continue # don't care about language
                if i < 4:
                    try_updating_genre(item, fic)
                else:
                    if item == "Complete":
                        fic.completed = True
                    else:
                        try_updating_chars(item, fic)
                        try_updating_pairings(item, fic)

def try_updating_counts(item, fic):
    # Special case rating
    field, value = map(lambda s: s.strip(), item.split(':'))
    if field == "Rated":
    	rating = get_or_create_rating(value)
        fic.rating = rating
    if field == "Chapters":
        fic.chapter_cnt = int(value.replace(',', ''))
    if field == "Words":
        fic.word_cnt = int(value.replace(',', ''))
    if field == "Reviews":
        fic.review_cnt = int(value.replace(',', ''))
    if field == "Favs":
        fic.favorite_cnt = int(value.replace(',', ''))
    if field == "Follows":
        fic.follow_cnt = int(value.replace(',', ''))

def try_updating_genre(item, fic):
	item = item.replace('Hurt/Comfort', 'Hurt-Comfort') #special case stupid genre
	genre_names = item.split('/')
	for g_name in genre_names:
		genre = get_or_create_genre(g_name)
		fic.genres.append(genre)

def try_updating_chars(item, fic):
	item = item.replace('] [',',').replace(']', '').replace('[','')
	chars = map(lambda s: s.strip(), item.split(','))
	for c_name in chars:
		char = get_or_create_character(c_name)
		fic.characters.append(char)

def try_updating_pairings(item, fic):
	if '[' not in item:
		return
	first, second = item.split(']', 1)
	first_chars = map(lambda s: get_or_create_character(s.strip()), first.replace('[','').split(','))
	fic.pairings.append(get_or_create_pairing(first_chars))
	if '[' in second:
		second_chars = map(lambda s: get_or_create_character(s.strip()), second.replace('[','').split(','))
		fic.pairings.append(get_or_create_pairing(second_chars))


def populate_db_from_file(filename=app.config['DB_BACKUP']):
	with app.open_resource(app.config['DB_BACKUP'], mode='r') as f:
		json_obj = json.load(f)
		for fic_obj in json_obj:
			# Add author
			author_name = fic_obj['author']
			author = get_or_create_author(author_name, '')
			db.session.add(author)
			fic = get_or_create_fic(fic_obj['title'], fic_obj['summary'], fic_obj['url'], author, fic_obj['publish_ts'], fic_obj['update_ts'])
			update_from_meta(fic_obj['meta'], fic)
			db.session.add(fic)
		db.session.commit()
		# Check
		authors = Author.query.order_by(Author.name).all()
		anAuthorsFic = Author.query.first().fics.all()[0]
		fics = Fic.query.order_by(Fic.title).all()

def refresh():
	db.drop_all()
	db.create_all()
	populate_db_from_file()
