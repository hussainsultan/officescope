#!/usr/local/bin/env python
import os
import unittest

from config import _basedir
from app import app, db
from app.officescope.models import User, Folder, Document, Favorite

class OfficescopeTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:iseekm2sn@vi@localhost/officescope_dev'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_registration(self):
        pass

    def register(self, name, username, email, password, cpassword):
        return self.app.post('/register', data=dict(
            fullname=name,
            username=username,
            email=email,
            password=password,
            password2=cpassword
        ), follow_redirects=True)
