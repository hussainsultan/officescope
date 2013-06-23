from functools import wraps

from flask import g, flash, redirect, url_for, request
from threading import Thread
from app import app


def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash(u'You need to be signed in to view this page.')
            return redirect(url_for('shafayet.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def async(f):
    def wrapper(*args, **kwargs):
        with app.test_request_context():
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()
    return wrapper


