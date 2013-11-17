#!/usr/local/bin/env python
import os
import unittest

from app import app, db
from app.officescope.models import User, Folder


class OfficescopeTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://shafayet@localhost/officescope_dev'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_registration(self):
        rv = self.register('Shafayet Khan', 'shafayet', 'shafayetkhan@gmail.com',
                           'youwillneverguess','youwillneverguess')

        assert 'You were successfully registered and can login now' in rv.data


    def register(self, name, username, email, password, cpassword):
        return self.app.post('/register', data=dict(
            fullname=name,
            username=username,
            email=email,
            password=password,
            password2=cpassword
        ), follow_redirects=True)

    def test_login(self):
        self.register('Shafayet Khan', 'shafayet', 'shafayetkhan@gmail.com',
                           'youwillneverguess','youwillneverguess')

        rv = self.login('shafayet', 'youwillneverguess')

        assert 'You were logged in' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_empty_home(self):
        self.register('Shafayet Khan', 'shafayet', 'shafayetkhan@gmail.com',
                           'youwillneverguess','youwillneverguess')
        rv = self.login('shafayet', 'youwillneverguess')

        assert 'Start by creating a new folder' in rv.data
        assert 'Start by creating a new folder' in rv.data

    def test_create_folder(self):
        self.register('Shafayet Khan', 'shafayet', 'shafayetkhan@gmail.com',
                           'youwillneverguess','youwillneverguess')
        self.login('shafayet', 'youwillneverguess')
        rv = self.create_folder('testfolder','home/test', 'shafayet')
        assert 'testfolder' in rv.data

    def create_folder(self, name, parent_folder_path, username):
        user = User.query.filter_by(username=username).first()
        parent_folder = Folder.query.filter(Folder.owner_id == user.id,
            Folder.target == parent_folder_path).first()
        target_url = '%s/%s' % (parent_folder_path, name)
        new_folder = Folder(name, parent_folder_path, target_url)
        new_folder.parent_folder = parent_folder
        new_folder.owner = user
        db.session.add(new_folder)
        db.session.commit()
        return self.app.get(parent_folder_path)

if __name__ == '__main__':
    unittest.main()
