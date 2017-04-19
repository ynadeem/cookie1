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

### Import db for database
# from google.appengine.ext import db 

### Jinja
template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

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

### Class for Main page
class MainHandler(Handler):
    def get(self):
        return "Hello World Get"
    def post(self):
        return "Hello World Post"

### Connects routes with classes. Add as necessary.
app = webapp2.WSGIApplication([
    ('/', MainHandler) 
], debug=True)