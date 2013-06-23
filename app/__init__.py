from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
mail = Mail(app)


#@app.errorhandler(404)
#def not_found(error):
#   return render_template('404.html'), 404

from app.officescope.views import officescope as officescope_mod
app.register_blueprint(officescope_mod)
