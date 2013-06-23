import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = frozenset(['shafayetkhan@gmail.com'])
SECRET_KEY = 'Change_This_Later'


# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
# SQLALCHEMY_DATABASE_URI = 'mysql://root:iseekm2sn@vi@localhost/officescope'
#SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/shafayet'
#heroku - comment the line below for foreman to work
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'use_a_strong_key'

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = 'blahblahblahblahblahblahblahblahblah'
RECAPTCHA_PRIVATE_KEY = 'blahblahblahblahblahblahprivate'
RECAPTCHA_OPTIONS = {'theme': 'white'}

#Upload Configuration
UPLOADED_FILES_DEST = os.path.realpath('.') + '/app/officescope/fileroom/'

# email server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'shafayetdotcom@gmail.com'
MAIL_PASSWORD = 'iseekm2sn@vi'

ADMINS_EMAIL = ['shafayetkhan@gmail.com']


