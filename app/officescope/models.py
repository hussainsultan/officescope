from app import db
from app.officescope import constants as USER
from datetime import datetime
import uuid


class Officescope_user(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(100))

    folders = db.relationship('Officescope_folder', backref='owner', lazy='dynamic')
    documents = db.relationship('Officescope_document', backref='owner', lazy='dynamic')
    favorites = db.relationship('Officescope_favorite', backref='user', lazy='dynamic')

    def __init__(self, name, username, email, pw_hash):
        self.id = unique_id()
        self.name = name
        self.username = username
        self.email = email
        self.pw_hash = pw_hash

    def __repr__(self):
        return '<Officescope_user %r>' % self.username


class Officescope_folder(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(80))
    path = db.Column(db.String(1000))
    target = db.Column(db.String(1000))
    add_date = db.Column(db.DateTime)
    folder_id = db.Column(db.String(100), db.ForeignKey('officescope_folder.id'))
    owner_id = db.Column(db.String(100), db.ForeignKey('officescope_user.id'))

    subfolders = db.relationship('Officescope_folder',
        backref=db.backref('parent_folder', remote_side=[id]),lazy='dynamic')
    documents = db.relationship('Officescope_document', backref='parent_folder',
        lazy='dynamic')
    favorites = db.relationship('Officescope_favorite', backref='folder', lazy='dynamic')





    def __init__(self, title, path, target, add_date=None):
        self.id = unique_id()
        self.title = title
        self.path = path
        self.target = target
        if add_date is None:
            add_date = datetime.utcnow()
        self.add_date = add_date

    def __repr__(self):
        return '<Officescope_folder %r>' % self.title

class Officescope_document(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(80))
    folder_url = db.Column(db.String(1000))
    download_url = db.Column(db.String(1000))
    add_date = db.Column(db.DateTime)
    owner_id = db.Column(db.String(100), db.ForeignKey('officescope_user.id'))
    folder_id = db.Column(db.String(100), db.ForeignKey('officescope_folder.id'))



    def __init__(self, title, folder_url, download_url, add_date=None):
        self.id = unique_id()
        self.title = title
        self.folder_url = folder_url
        self.download_url = download_url
        if add_date is None:
            add_date = datetime.utcnow()
        self.add_date = add_date

    def __repr__(self):
        return '<Officescope_document %r>' % self.title


class Officescope_favorite(db.Model):
    user_id = db.Column(db.String(100), db.ForeignKey('officescope_user.id'), primary_key=True)
    folder_id = db.Column(db.String(100), db.ForeignKey('officescope_folder.id'), primary_key=True)



#returns a unique id
def unique_id():
    return hex(uuid.uuid4().time)[2:-1]

def get_user_name(id):
    user = Officescope_user.query.filter_by(id=id).first()
    username = user.name
    return username
