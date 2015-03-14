from ficflaskr import db, app
from datetime import datetime
import json
import collections

hidden_fics = db.Table('hidden_fics',
	db.Column('fic_id', db.Integer, db.ForeignKey('fic.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

favorited_fics = db.Table('favorited_fics',
	db.Column('fic_id', db.Integer, db.ForeignKey('fic.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

saved_filters = db.Table('saved_filters',
	db.Column('filter_id', db.Integer, db.ForeignKey('filter.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	email = db.Column(db.String(120), unique=True)

	hidden_fics = db.relationship('Fic', secondary=hidden_fics,
			backref=db.backref('hidden_users', lazy='dynamic'), lazy='dynamic')

	favorited_fics = db.relationship('Fic', secondary=favorited_fics,
			backref=db.backref('favorited_users', lazy='dynamic'), lazy='dynamic')

	saved_filters = db.relationship('Filter', secondary=saved_filters,
			backref=db.backref('saved_users', lazy='dynamic'), lazy='dynamic')

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def hide(self, fic):
		if not self.is_hidden(fic):
			self.hidden_fics.append(fic)
			db.session.commit()

	def unhide(self, fic):
		if self.is_hidden(fic):
			self.hidden_fics.remove(fic)
			db.session.commit()

	def is_hidden(self, fic):
		return fic in self.hidden_fics.all()

	def favorite(self, fic):
		if not self.is_favorited(fic):
			self.favorited_fics.append(fic)
			db.session.commit()

	def unfavorite(self, fic):
		if self.is_favorited(fic):
			self.favorited_fics.remove(fic)
			db.session.commit()

	def is_favorited(self, fic):
		return fic in self.favorited_fics.all()

	def is_saved(self, fltr):
		return fltr in self.saved_filters.all()

	def is_query_string_saved_fitler(self, query_string):
		res = []
		for s in query_string.split('&'):
			if not s.endswith('='):
				res.append(s)
		query = '&'.join(res)
		fltr = Filter.query.filter_by(query_string=query).first()
		return fltr

	def is_saved_fitler(self, name):
		fltr = self.saved_filters.filter_by(name=name).first()
		if fltr:
			return True
		else:
			return False

	def get_or_create_filter(self, name, query):
		fltr = self.saved_filters.filter_by(name=name).filter_by(query=query).first()
		if fltr:
			return fltr
		else:
			fltr = Filter(name, query)
			db.session.add(fltr)
			return fltr

	def save(self, fltr):
		if not self.is_saved(fltr):
			self.saved_filters.append(fltr)
			db.session.commit()

	def unsave(self, fltr):
		if self.is_saved(fltr):
			self.saved_filters.remove(fltr)
			db.session.commit()

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

class Filter(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	query_string = db.Column(db.String(200), unique=True)
	name = db.Column(db.String(80))

	def __init__(self, name, query_string):
		self.name = name
		self.query_string = query_string

	def __repr__(self):
		return '<Filter %r:%r>' % (self.name, self.query_string)

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

	favorite_cnt = db.Column(db.Integer, default = 0)
	follow_cnt = db.Column(db.Integer, default = 0)
	word_cnt = db.Column(db.Integer, default = 0)
	chapter_cnt = db.Column(db.Integer, default = 0)
	review_cnt = db.Column(db.Integer, default = 0)

	completed = db.Column(db.Boolean)

	author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
	rating_id = db.Column(db.Integer, db.ForeignKey('rating.id'))

	genres = db.relationship('Genre', secondary=genres,
			backref=db.backref('fics', lazy='dynamic'), lazy="dynamic")

	characters = db.relationship('Character', secondary=characters,
			backref=db.backref('fics', lazy='dynamic'), lazy="dynamic")

	pairings = db.relationship('Pairing', secondary=fic_pairings,
			backref=db.backref('fics', lazy='dynamic'), lazy="dynamic")

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
	name = db.Column(db.String)

	def __repr__(self):
		return '<Pairing %r>' % map(lambda s: s.name, self.characters)

	def __str__(self):
		return '/'.join(map(lambda s: s.name, self.characters))

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
	pairing.name = '/'.join([c.name for c in pairing.characters.all()])
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
	item = item.replace('] [',',').replace(']', ',', 1).replace(']', '').replace('[','')
	chars = map(lambda s: s.strip(), item.split(','))
	print chars
	for c_name in chars:
		if len(c_name) > 0:
			char = get_or_create_character(c_name)
			fic.characters.append(char)

def try_updating_pairings(item, fic):
	if '[' not in item:
		return
	first, second = item.split(']', 1)
	first_chars = map(lambda s: get_or_create_character(s.strip()), first.replace('[','').split(','))
	fic.pairings.append(get_or_create_pairing(first_chars))
	if '[' in second:
		second_chars = map(lambda s: get_or_create_character(s.strip()), second.replace('[','').replace(']','').split(','))
		fic.pairings.append(get_or_create_pairing(second_chars))


def populate_db_from_file(filename=app.config['DB_BACKUP']):
	with app.open_resource(filename, mode='r') as f:
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

def refresh(limit=1):
	db.drop_all()
	db.create_all()
	for i in xrange(limit):
		print i
		populate_db_from_file('data/fanfic_data_'+str(i) +'.json');
