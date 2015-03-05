from ficflaskr import app, db, lm, oid
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import request, session, g, redirect, url_for, \
		  abort, render_template, flash, jsonify
from contextlib import closing
from .forms import LoginForm
from .models import User, Fic, Author

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user

@app.route('/')
@app.route('/fics')
@app.route('/fics/<int:page>')
def show_fics(page=1):
	user = g.user
	fics = Fic.query.order_by(Fic.title).paginate(page, 25, False)
	return render_template('show_fics.html', fics=fics, user=user)

@app.route('/authors')
@app.route('/authors/<int:page>')
def show_authors(page=1):
	authors = Author.query.order_by(Author.name).paginate(page, 25, False)
	print authors.items
	return render_template('show_authors.html', authors=authors)

@app.template_filter('create_link')
def create_link(fic):
	return '<a href="%s">%s</a>' % (fic.url, fic.title)

@app.route('/_favorite')
def favorite():
	fic_id = request.args.get('fic_id', 0, type=int)
	print fic_id
	fic = Fic.query.get(fic_id)
	if fic and g.user is not None and g.user.is_authenticated():
		g.user.favorite(fic)
		return jsonify(result="Added to favs")
	return jsonify(result="Didn't add to favs")

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		print g.user
		return redirect(url_for('show_fics', page=1))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
	return render_template('login.html', 
							title='Sign In',
							form=form,
							providers=app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
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