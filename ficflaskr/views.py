from ficflaskr import app, db, lm, oid
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import request, session, g, redirect, url_for, \
		  abort, render_template, flash, jsonify
from contextlib import closing
from .forms import LoginForm, FilterForm
from .models import User, Fic, Author, Genre, Character, Pairing, Filter
import json
import urllib

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user

def query_fics_given_form(form):
	query = Fic.query
	if form.word_min.data:
		query = query.filter(Fic.word_cnt >= form.word_min.data)
	if form.word_max.data:
		query = query.filter(Fic.word_cnt <= form.word_max.data)
	if form.avg_chapter_length_min.data:
		query = query.filter(Fic.word_cnt/Fic.chapter_cnt >= form.avg_chapter_length_min.data)
	if form.one_shot.data:
		query = query.filter(Fic.chapter_cnt == 1)
	if form.complete.data:
		query = query.filter(Fic.completed == True)
	if form.genre_autocomplete.data:
		genres = form.genre_autocomplete.data.split(',')
		query = query.filter(Fic.genres.any(Genre.name.in_(genres)))
	if form.character_autocomplete.data:
		characters = form.character_autocomplete.data.split(',')
		query = query.filter(Fic.characters.any(Character.name.in_(characters)))
	if form.pairing_autocomplete.data:
		pairings = form.pairing_autocomplete.data.split(',')
		query = query.filter(Fic.pairings.any(Pairing.name.in_(pairings)))
	return query

@app.route('/_character_autocomplete')
def character_autocomplete():
	term = request.args.get('term')
	search = term + '%' if len(term) <= 5 else '%' + term + '%'
	similar_chars = Character.query.filter(Character.name.like(search)).all()
	return jsonify(json_list=[char.name for char in similar_chars])

def cleanup_query(query):
	query = query.replace("&amp;", "&")
	split = query.split('&')
	result = []
	for s in split:
		if not s.endswith('='):
			result.append(s)
	return '&'.join(result)

@app.route('/_save_filter')
def favorite_query():
	query = cleanup_query(request.args.get('query'))
	name = request.args.get('name')
	# Guaranteed that g.user is not None, only available in view when logged in
	fltr = g.user.get_or_create_filter(name, query)
	if fltr and g.user is not None and g.user.is_authenticated():
		if g.user.is_saved(fltr):
			g.user.unsave(fltr)
			return jsonify(result="Unsaved filter")
		else:
			g.user.save(fltr)
			return jsonify(result="Saved filter")
	return jsonify(result="Didn't find filter to save")

@app.route('/user')
@app.route('/user/<path:username>')
def show_user(username=""):
	if username == "":
		return render_template('show_user.html', user=g.user)
	else:
		user = User.query.filter_by(username=username).first()
		return render_template('show_user.html', user=user)

@app.route('/')
@app.route('/fics')
@app.route('/fics/<int:page>')
def show_fics(page=1):
	user = g.user
	form = FilterForm(request.args)
	if form.saved_filters_autocomplete.data:
		# Don't need to worry about g.user since option only available when logged in
		fltr = g.user.saved_filters.filter_by(name=form.saved_filters_autocomplete.data).first()
		print 'saved filter', fltr
		return redirect(url_for('show_fics', page=1) + '?' + fltr.query_string)
	else:
		fics = query_fics_given_form(form).order_by(Fic.title).paginate(page, 25, False)
		return render_template('show_fics.html', fics=fics, user=user, form=form)

@app.route('/authors')
@app.route('/authors/<int:page>')
def show_authors(page=1):
	authors = Author.query.order_by(Author.name).paginate(page, 25, False)
	return render_template('show_authors.html', authors=authors)

@app.template_filter('create_link')
def create_link(fic):
	return '<a href="%s">%s</a>' % (fic.url, fic.title)

@app.route('/_hide')
def hide():
	fic_id = request.args.get('fic_id', 0, type=int)
	fic = Fic.query.get(fic_id)
	if fic and g.user is not None and g.user.is_authenticated():
		if g.user.is_hidden(fic):
			g.user.unhide(fic)
			return jsonify(result="unHid fic")
		else:
			g.user.hide(fic)
			return jsonify(result="hid fic")
	return jsonify(result="didn't find fic to hide")

@app.route('/_favorite')
def favorite():
	fic_id = request.args.get('fic_id', 0, type=int)
	fic = Fic.query.get(fic_id)
	if fic and g.user is not None and g.user.is_authenticated():
		if g.user.is_favorited(fic):
			g.user.unfavorite(fic)
			return jsonify(result="Added to favs")
		else:
			g.user.favorite(fic)
			return jsonify(result="Removed from favs")
	return jsonify(result="Didn't find fic to fav")

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
	print "hi"
	if g.user is not None and g.user.is_authenticated():
		print g.user
		return redirect(url_for('show_fics', page=1))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		print "Trying oid"
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
	return render_template('login.html', 
							title='Sign In',
							form=form,
							providers=app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
	print "after login"
	if resp.email is None or resp.email == "":
		flash('Invalid login. Please try again.')
		return redirect(url_for('login'))
	user = User.query.filter_by(email=resp.email).first()
	if user is None:
		username = resp.nickname
		if username is None or username == "":
			username = resp.email.split('@')[0]
		user = User(username=username, email=resp.email)
		db.session.add(user)
		db.session.commit()
	print User.query.all()
	remember_me = False
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('show_fics', page=1))

@app.route('/data/characters.json')
def characters_json():
	return json.dumps([char.name for char in Character.query.all()])

@app.route('/data/genres.json')
def genres_json():
	return json.dumps([genre.name for genre in Genre.query.all()])

@app.route('/data/pairings.json')
def pairings_json():
	return json.dumps([str(pairing) for pairing in Pairing.query.all()])

@app.route('/data/saved_filters.json')
def saved_filters_json():
	user_id = request.args.get('user_id', 0, type=int)
	if user_id > 0:
		return json.dumps([fltr.name for fltr in User.query.get(user_id).saved_filters.all()])
	else:
		return json.dumps([])