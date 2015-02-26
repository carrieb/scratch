# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
		  abort, render_template, flash
from contextlib import closing
import json
from datetime import datetime

# configuration
DATABASE = '/tmp/ficflaskr.db'
DB_BACKUP = 'compiled_fic.json'
DEBUG = True
SECRET_KEY = 'dev key'
USERNAME = 'admin'
PASSWORD = 'default'

# create out little application ;)
app = Flask(__name__)
app.config.from_object(__name__)

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def populate_db_from_file(filename=app.config['DB_BACKUP']):
	with closing(connect_db()) as db:
		with app.open_resource(app.config['DB_BACKUP'], mode='r') as f:
			json_obj = json.load(f)
			for fic in json_obj:
				# Add author
				author_name = fic['author']
				db.cursor().execute('insert into authors (name) values (?)', [author_name])
				db.cursor().execute('insert into fics (title, summary, author, url, publishdate, updatedate) values (?, ?, ?, ?, ?, ?)', [fic['title'], fic['summary'], fic['author'], fic['url'], fic['publish_ts'], fic['update_ts']])
			db.commit()
			# Check
			cur = db.execute('select name from authors order by name desc')
			print cur.fetchall()
			cur = db.execute('select title, author, url from fics order by title asc')
			print cur.fetchall()


def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

def format_ts(ts, typ):
	dt = datetime.fromtimestamp(ts)
	string = dt.strftime('%m-%d-%Y')
	print typ, string
	return string

@app.route('/')
def show_fics():
	cur = g.db.execute('select title, url, author, summary, updatedate, publishdate from fics order by title desc')
	fics = [dict(title=row[0], url=row[1], author=row[2], summary=row[3], publish=format_ts(row[4], 'pub'), updated=format_ts(row[5], 'up')) for row in cur.fetchall()]
	return render_template('show_fics.html', fics=fics)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_fics'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_fics'))


if __name__ == '__main__':
	app.run()
