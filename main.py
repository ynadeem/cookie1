"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask
app = Flask(__name__)
app.config['DEBUG'] = True
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

import os
import re ### Used in email and password validation functions
import logging ### Allows use of logging functions to help with debugging
import jinja2 ### Used in html templates
import webapp2

# Import db for database
from google.appengine.ext import db 

# Import HMAC for Cookie hashing
import hmac

### Jinja
template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

# Validation Functions:
def doPasswordsMatch(password, verify):
    return password == verify
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)
PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PASS_RE.match(password)
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    # Email is optional
    if email:
        return EMAIL_RE.match(email)
    else:
        return True

### All future classes will inherit from this class. Defines shorter named functions for 
### faster coding.
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t= jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        self.render("signupform.html", passwordsMatch = True, validUsername = True, 
                        validPassword = True, validEmail = True)
    def post(self):
        # Get user inputs and assign to variables
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        # Assign results of verifications to variables
        passwordsMatch = doPasswordsMatch(password, verify)
        validUsername = valid_username(username)
        validPassword = valid_password(password)
        validEmail = valid_email(email)

        # Set secret string for cookie hashing
        secretString = 'beastingandfeasting'

        # Define function to hash value
        def hash_str(s):
            return hmac.new(secretString, s).hexdigest()
        
        # Define function to combine 'username' + '|' + 'hash' like this 'username | hash'
        def make_secure_val(s):
            return "%s|%s" % (s, hash_str(s))
        
        # Define function to check if username matches hash of username
        def check_secure_val(h):
            val = h.split('|')[0]
            if h == make_secure_val(val):
                return val

        # Assign cookie value as concatenation of secret string and username
        cookieValue = make_secure_val(username)


        # Set Cookie
        self.response.headers.add_header('Set-Cookie', 'name='+str(cookieValue)+'; Path=/')
        cookieUsername = self.request.cookies.get('name')
        secureValue = check_secure_val(cookieUsername)

        # If no error pops, render welcome.html, otherwise render signupform and send error variables to it
        if (passwordsMatch and validUsername and validPassword and validEmail and secureValue):            
            #self.render("welcome.html", username = username)
            self.redirect('/welcome')
        else:
            self.render("signupform.html", passwordsMatch = passwordsMatch, validUsername = validUsername, 
                        validPassword = validPassword, validEmail = validEmail, username = username, email = email)



class Welcome(MainHandler):
    def get(self):
        username = self.request.cookies.get('name')
        self.render("welcome.html", username = username.split('|')[0])
        # Set secret string for cookie hashing
        secretString = 'beastingandfeasting'

        # Define function to hash value
        def hash_str(s):
            return hmac.new(secretString, s).hexdigest()
        
        # Define function to combine 'username' + '|' + 'hash' like this 'username | hash'
        def make_secure_val(s):
            return "%s|%s" % (s, hash_str(s))
        
        # Define function to check if username matches hash of username
        def check_secure_val(h):
            val = h.split('|')[0]
            if h == make_secure_val(val):
                return val
        
        secureValue = check_secure_val(username)
        
        if not secureValue:
            self.redirect('/signup')

app = webapp2.WSGIApplication([
    ('/signup', MainHandler),
    ('/welcome', Welcome) 
], debug=True)

### To get cookie from user: self.request.cookies.get(name)
### To send cookie to user: add header to response: self.response.headers.add_header('Set-Cookie', 'name=value; Path=/')