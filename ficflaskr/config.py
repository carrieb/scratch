import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'penguin-koushi'
# configuration
DB_BACKUP = 'compiled_fic.json'
DEBUG = True
SECRET_KEY = 'dev key'
USERNAME = 'admin'
PASSWORD = 'default'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'ficflaskr.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
PROPOGATE_EXCEPTIONS = True

OPENID_PROVIDERS = [{'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'}]
