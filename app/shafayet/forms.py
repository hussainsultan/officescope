from flask.ext.wtf import (Form, TextField, TextAreaField, SubmitField,
     validators, ValidationError)

class ContactForm(Form):
    name = TextField("Name", [validators.Required("Please enter your name.")])
    email = TextField("Email", [validators.Required("Please enter your email address"), validators.Email("Please enter a valid email address.")])
    message = TextAreaField("Message", [validators.Required("Please enter a message")])
    submit = SubmitField("Send")