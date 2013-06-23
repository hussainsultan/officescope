from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash
from forms import ContactForm
from email import send_email
from config import ADMINS_EMAIL

#from app import db

shafayet = Blueprint('shafayet', __name__)


@shafayet.route('/')
def index():
    return render_template("shafayet/index.html")

@shafayet.route('/about')
def about():
    return render_template("shafayet/about.html")

@shafayet.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('shafayet/contact.html', form=form)
        else:
            body = """From: %s <%s> Message:%s""" % (form.name.data,
                form.email.data, form.message.data)
            send_email(subject="Webmaster", sender='shafayetkhan@gmail.com',
                recipients=ADMINS_EMAIL, text_body=body)
            return render_template('shafayet/contact.html', success=True)
    elif request.method == 'GET':
        return render_template('shafayet/contact.html', form=form)


