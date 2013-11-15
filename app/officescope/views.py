#!/usr/bin/lib/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os.path

from flask import (Blueprint, Flask, request, session, url_for, redirect,
        render_template, abort, g, flash, _app_ctx_stack)
from werkzeug import check_password_hash, generate_password_hash
from flask.ext.uploads import (UploadSet, configure_uploads, DEFAULTS,
        UploadNotAllowed)

from app import db
from app import app

from models import get_user_name, User, Document, Folder, Favorite

#Uploads
uploaded_files = UploadSet('files', DEFAULTS)
configure_uploads(app, uploaded_files)

officescope = Blueprint('officescope', __name__)

@officescope.before_request
def before_request():
    """Sets user id to g object if not available in session already."""
    g.user = None
    if 'user_id' in session:
        g.user = User.query.filter_by(id=session['user_id']).first()


@officescope.route('/about')
def about():
    return 'about'


# TODO: Change this logic... complex is better than complicated
@officescope.route('/', defaults={'path': 'home'})
@officescope.route('/home', defaults={'path': 'home'})
@officescope.route('/<path:path>')
def home(path):
    """Shows a list of folders and documents owned by the user. The home page also
    shows a list of favorites the user has added. If the user is not session, it will
    redirect to the login page."""
    if g.user:
        """ TODO
        if not path_exists(path):
            flash("Folder '%s' does not exist" % path)
            return redirect(url_for('home', path='home'))
        """
        folders = Folder.query.filter(Folder.owner_id == g.user.id,
            Folder.path == path).all()
        documents = Document.query.filter(Document.owner_id == g.user.id,
            Document.folder_url == path).all()
        favorites = Favorite.query.join(Folder).filter(Favorite.user_id == g.user.id,
            Folder.id == Favorite.folder_id).all()
        return render_template('officescope/home.html', folders=folders, documents=documents,
            parent_path=path, favorites=favorites)
    else:
        return redirect(url_for('officescope.login'))


@officescope.route('/<path:path>/create_folder', methods=['POST'])
def create_folder(path):
    """Creates a new folder in the provided path"""
    if not g.user:
        return redirect(url_for('login'))
    #error = None
    if g.user and request.method =='POST':
        parent_folder = Folder.query.filter(Folder.owner_id == g.user.id,
            Folder.target == path).first()
        if parent_folder.owner_id != g.user.id:
            abort(401)
        target_url = '%s/%s' % (path, request.form['folder_name'])
        new_folder = Folder(request.form['folder_name'], path, target_url)
        #folder backref
        new_folder.parent_folder = parent_folder
        new_folder.owner = g.user
        db.session.add(new_folder)
        db.session.commit()
        return redirect(url_for('officescope.home', path=path))


@officescope.route('/<path:path>/<folder_id>/favorite')
def add_favorite(path, folder_id):
    """Adds a new favorite folder into favorites"""
    if not g.user:
        return redirect(url_for('officescope.login'))
    #error = None
    if g.user:
        favorite_folder = Folder.query.filter_by(id=folder_id).first()
        new_favorite = Favorite()
        new_favorite.user = g.user
        new_favorite.folder = favorite_folder
        db.session.add(new_favorite)
        db.session.commit()
        return redirect(url_for('officescope.home', path=path))


@officescope.route('/<path:path>/<folder_id>/delete_folder')
def delete_folder(path, folder_id):
    """Wrapper for delet_folder_recursively and returns to the path of origin."""
    if not g.user:
        return redirect(url_for('officescope.login'))
    if g.user:
        delete_folder_recursively(folder_id)
        return redirect(url_for('officescope.home', path=path))


def delete_folder_recursively(parent_folderid):
    """Deletes a folder recursively as well as any favorites and documents contained
    by the folder."""
    subfolders = Folder.query.filter(Folder.owner_id == g.user.id,
                                  Folder.folder_id == parent_folderid).all()
    folder_to_delete = Folder.query.filter(Folder.owner_id == g.user.id,
                                           Folder.id == parent_folderid).first()
    favorite_to_delete = Favorite.query.filter(Favorite.user_id == g.user.id,
                                               Favorite.folder_id == parent_folderid).first()
    documents_to_delete = Document.query.filter(Document.owner_id == g.user.id,
                                                Document.folder_id == parent_folderid).all()

    for subfolder in subfolders:
        delete_folder_recursively(subfolder.id)
    if favorite_to_delete:
        db.session.delete(favorite_to_delete)
    for document in documents_to_delete:
        delete_document_and_unlink(document.id)
    db.session.delete(folder_to_delete)
    db.session.commit()



@officescope.route('/<path:path>/<doc_id>/delete_document')
def delete_document(path, doc_id):
    """Wrapper for delete_document_and_unlink. Redirects to path of origin."""
    if not g.user:
        return redirect(url_for('officescope.login'))
    #error = None
    if g.user:
        delete_document_and_unlink(doc_id)
        return redirect(url_for('officescope.home', path=path))


def delete_document_and_unlink(doc_id):
    """Deletes a particular document and also unlinks the document from disk."""
    document_to_delete = Document.query.filter_by(id=doc_id).first()
    file_to_delete = app.config['UPLOADED_FILES_DEST'] + document_to_delete.title
    db.session.delete(document_to_delete)
    db.session.commit()
    if os.path.isfile(file_to_delete):
        os.remove(file_to_delete)


@officescope.route('/<path:path>/upload', methods=['POST'])
def upload_file(path):
    """Uploads a file to the supplied path and creates a new document."""
    if not g.user:
        return redirect(url_for('officescope.login'))
    #error = None
    if g.user and request.method == 'POST' and ('file' in request.files):
        parent_folder = Folder.query.filter(Folder.owner_id == g.user.id,
            Folder.target == path).first()
        if parent_folder.owner_id != g.user.id:
            abort(401)
        try:
            filename = uploaded_files.save(request.files['file'])
            file_url = uploaded_files.url(filename)
            new_document = Document(title=filename, folder_url=parent_folder.target,
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
        user = User.query.filter_by(username=request.form['username']).first()

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
        elif User.query.filter_by(username=request.form['username']).first() is not None:
            error = 'The username is already taken'
        else:
            user = User(request.form['fullname'], request.form['username'],
                request.form['email'], generate_password_hash(request.form['password']))
            new_folder = Folder('home', 'ROOT', 'home')
            new_folder.owner = user
            db.session.add(user)
            db.session.add(new_folder)
            db.session.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('officescope.login'))
    return render_template('officescope/register.html', error=error)

#jinja filters
app.jinja_env.filters['getusername'] = get_user_name
