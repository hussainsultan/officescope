from __future__ import with_statement
import os.path
import datetime
import uuid
from hashlib import md5
from datetime import datetime
from flask import (Blueprint, Flask, request, session, url_for, redirect,
        render_template, abort, g, flash, _app_ctx_stack)

from werkzeug import check_password_hash, generate_password_hash
from flask.ext.uploads import (UploadSet, configure_uploads, DEFAULTS,
        UploadNotAllowed)

from app import db
from app import app

from models import get_user_name, Officescope_user, Officescope_document, Officescope_folder, Officescope_favorite

#Uploads
uploaded_files = UploadSet('files', DEFAULTS)
configure_uploads(app, uploaded_files)

officescope = Blueprint('officescope', __name__, url_prefix='/officescope')

@officescope.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = Officescope_user.query.filter_by(id=session['user_id']).first()


@officescope.route('/about')
def about():
    return 'about'


####################################
#Change this!
#Change the home route '/path:path>
#to '/home/<path:path>'
#change the target of the created
#folder to ROOT instead of home
####################################

@officescope.route('/', defaults={'path': 'home'})
@officescope.route('/home', defaults={'path': 'home'})
@officescope.route('/<path:path>')
def home(path):
    if g.user:
        """
        if not path_exists(path):
            flash("Officescope_folder '%s' does not exist" % path)
            return redirect(url_for('home', path='home'))
        """
        folders = Officescope_folder.query.filter(Officescope_folder.owner_id == g.user.id,
            Officescope_folder.path == path).all()
        documents = Officescope_document.query.filter(Officescope_document.owner_id == g.user.id,
            Officescope_document.folder_url == path).all()
        #join query
        favorites = Officescope_favorite.query.join(Officescope_folder).filter(Officescope_favorite.user_id == g.user.id,
            Officescope_folder.id == Officescope_favorite.folder_id).all()
        return render_template('officescope/home.html', folders=folders, documents=documents,
            parent_path=path, favorites=favorites)
    else:
        return redirect(url_for('officescope.login'))


@officescope.route('/<path:path>/create_folder', methods=['POST'])
def create_folder(path):
    if not g.user:
        return redirect(url_for('login'))
    #error = None
    if g.user and request.method =='POST':
        parent_folder = Officescope_folder.query.filter(Officescope_folder.owner_id == g.user.id,
            Officescope_folder.target == path).first()
        if parent_folder.owner_id != g.user.id:
            abort(401)
        target_url = '%s/%s' % (path, request.form['folder_name'])
        new_folder = Officescope_folder(request.form['folder_name'], path, target_url)
        #folder backref
        new_folder.parent_folder = parent_folder
        new_folder.owner = g.user
        db.session.add(new_folder)
        db.session.commit()
        return redirect(url_for('officescope.home', path=path))


@officescope.route('/<path:path>/<folder_id>/favorite')
def add_favorite(path, folder_id):
    if not g.user:
        return redirect(url_for('officescope.login'))
    #error = None
    if g.user:
        favorite_folder = Officescope_folder.query.filter_by(id=folder_id).first()
        new_favorite = Officescope_favorite()
        new_favorite.user = g.user
        new_favorite.folder = favorite_folder
        db.session.add(new_favorite)
        db.session.commit()
        return redirect(url_for('officescope.home', path=path))

@officescope.route('/<path:path>/<folder_id>/delete_folder')
def delete_folder(path, folder_id):
    #TODO
    #A recursive way to delete subfolders with while folder.subfolders
    if not g.user:
        return redirect(url_for('officescope.login'))
    #error = None
    if g.user:
        folder_to_delete = Officescope_folder.query.filter_by(id=folder_id).first()
        favorite_to_delete = Officescope_favorite.query.filter(Officescope_favorite.user_id == g.user.id,
            Officescope_favorite.folder_id == folder_id).first()
        if favorite_to_delete:
            db.session.delete(favorite_to_delete)
        db.session.delete(folder_to_delete)
        db.session.commit()
        return redirect(url_for('officescope.home', path=path))


@officescope.route('/<path:path>/<doc_id>/delete_document')
def delete_document(path, doc_id):
    if not g.user:
        return redirect(url_for('officescope.login'))
    #error = None
    if g.user:
        document_to_delete = Officescope_document.query.filter_by(id=doc_id).first()
        db.session.delete(document_to_delete)
        db.session.commit()
        file_to_delete = app.config['UPLOADED_FILES_DEST'] + document_to_delete.title
        if os.path.isfile(file_to_delete):
            os.remove(file_to_delete)
        return redirect(url_for('officescope.home', path=path))





@officescope.route('/<path:path>/upload', methods=['POST'])
def upload_file(path):
    if not g.user:
        return redirect(url_for('officescope.login'))
    #error = None
    if g.user and request.method == 'POST' and ('file' in request.files):
        parent_folder = Officescope_folder.query.filter(Officescope_folder.owner_id == g.user.id,
            Officescope_folder.target == path).first()
        if parent_folder.owner_id != g.user.id:
            abort(401)
        try:
            filename = uploaded_files.save(request.files['file'])
            file_url = uploaded_files.url(filename)
            new_document = Officescope_document(title=filename, folder_url=parent_folder.target,
                download_url=file_url)
            #documents backref
            new_document.parent_folder = parent_folder
            new_document.owner = g.user

            db.session.add(new_document)
            db.session.commit()
        except UploadNotAllowed:
            flash("Failed to upload file.")

        return redirect(url_for('officescope.home', path=path))






@officescope.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('officescope.home'))
    error = None
    if request.method == 'POST':
        user = Officescope_user.query.filter_by(username=request.form['username']).first()

        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user.pw_hash, request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user.id
            return redirect(url_for('officescope.home'))
    return render_template('officescope/login.html', error=error)

@officescope.route('/logout')
def logout():
    """Logs the user out."""
    if g.user:
        session.pop('user_id', None)
        flash('You were logged out')
        return redirect(url_for('officescope.login'))


@officescope.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('officescope.home'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
            '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif Officescope_user.query.filter_by(username=request.form['username']).first() is not None:
            error = 'The username is already taken'
        else:
            user = Officescope_user(request.form['fullname'], request.form['username'],
                request.form['email'], generate_password_hash(request.form['password']))
            new_folder = Officescope_folder('home', 'ROOT', 'home')
            new_folder.owner = user
            db.session.add(user)
            db.session.add(new_folder)
            db.session.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('officescope.login'))
    return render_template('officescope/register.html', error=error)

#jinja filters
app.jinja_env.filters['getusername'] = get_user_name



