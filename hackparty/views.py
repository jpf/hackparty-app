from gdomain import Domain
from hackparty import app

from google.appengine.api import memcache
from google.appengine.api import mail

from flask import render_template, request
from flask import url_for
import json

import uuid

def get_app_domain():
    d = Domain("hackparty.org", "jeff.lindsay@hackparty.org", memcache.get("domain_pass"))
    return d

@app.route('/preregistration', methods=['GET', 'POST'])
def preregistration():
    if request.method == 'GET':
        return render_template('preregistration.html')
    if request.method == 'POST':
        email = request.form['email'] 
        guid = uuid.uuid1()
        fob = guid.get_hex()

        url = app.config['SERVER_NAME']
        if not url: #wtf.
            url = 'http://localhost:8083'

        memcache.add(fob, email, 6000)

        url = url + url_for( 'register', guid=fob )

        mail.send_mail(
            sender="Example.com Support <support@example.com>",
            to=email,
            subject="You're one step away from having a HackParty account!",
            body="""
Hey there!

Go here: %s

""" % url)

        template_values = {
            'email' : email,
            'url' : url
        }        

        return render_template('email_sent.html', **template_values)

@app.route('/complete_register/<guid>', methods=['GET', 'POST'])
def register(guid=''):
    if guid == '':
        return "invalid token."

    email = memcache.get(guid)
    if not email:
        return "super invalid token, yo."

    if request.method == 'GET':
        return render_template('register.html', email=email, guid=guid)
    if request.method == 'POST':

        fname = request.form['fname'] 
        lname = request.form['lname'] 
        password = request.form['password'] 
        password2 = request.form['password2'] 

        if password == '':
            return "invalid password."
        if lname == '':
            return "please enter a last name."
        if fname == '':
            return "please enter a first name."
        if password != password2:
            return "passwords did not match."

        username = "%s.%s" % (fname,lname)

        d = get_app_domain()
        _u = d.users.create(username, password, fname, lname)

        return str(_u)

@app.route('/')
def hello_world():
    return render_template('helloworld.html')

@app.route('/users')
def users():
    d = get_app_domain()
    return json.dumps(d.email.get_forwarding('jeff.lindsay'))
