"""
This module contains class for a base pages handler
and functions for cookies set and read
"""

import os
import hmac
import jinja2
import webapp2
import blog
from user import User

# settings for a jinja environment
template_dir = os.path.join(os.path.dirname(__file__), '../views')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    """
    This class contains base methods for page rendering
    """
    def write(self, *a, **kw):
        """ write page using args and params """
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """ render using jinja template """
        templ = jinja_env.get_template(template)
        return templ.render(params)

    def render(self, template, **kw):
        """ write rendered template with parameters """
        self.write(self.render_str(template, **kw))


class Handler(BaseHandler):
    """
    This class inherits BaseHandler and contains initialize methods for user
    logged in|out check and cookies processing
    """
    def initialize(self, *a, **kw):
        """ this function is called before every request """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        # check if uid exists an store it in self.user
        if uid and User.by_id(int(uid)):
            self.user = User.by_id(int(uid))
        else:
            self.user = None

    def render(self, template, **kw):
        """ write rendered template with parameters """
        # add username as parameter for rendering in templates
        # if user is logged in
        if self.user:
            kw['user'] = self.user.username
        self.write(self.render_str(template, **kw))

# secure cookie block
    def hash_str(self, string):
        """ define hash string for cookie value """
        secret = 'aR45tyh1gxdndshd7u9dsjke80(2j4_^lh'
        return hmac.new(secret, string).hexdigest()

    def make_secure_val(self, string):
        """ create "value|hash" pair for cookie """
        return "%s|%s" % (string, self.hash_str(string))

    def check_secure_val(self, hsh):
        """ compare cookie hash value with generated hash """
        val = hsh.split('|')[0]
        if hsh == self.make_secure_val(val):
            return val

    def set_secure_cookie(self, name, value):
        """ sets secure cookie """
        cookie_val = self.make_secure_val(value)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        """ read and check cookie value """
        cookie_val = self.request.cookies.get(name)
        if cookie_val and self.check_secure_val(cookie_val):
            return self.check_secure_val(cookie_val)


    def login(self, user):
        """ sets secure cookie on user login """
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        """ delete cookie on user logout """
        self.response.headers.add_header('Set-Cookie', "user_id=; Path=/")


class UserPostHandler(Handler):
    """
    This class inherits Handler and contains initialize method that redirects
    to login page if user is not logged in
    """
    def initialize(self, *a, **kw):
        """ Init method checks is a user is logged in """
        Handler.initialize(self, *a, **kw)
        if not self.user:
            self.redirect("/blog/login", abort=True)

    def add_edit_post(self, post=None):
        """ Method adds new or edits existing post """
        subject = self.request.get("subject")
        content = self.request.get("content")
        error, post_id = blog.Blog.put_post(self.user, subject, content)
        if error:
            self.render("newpost.html", subject=subject,
                        content=content, error=error)
        else:
            self.redirect("/blog/%s/%s" %
                          (self.user.username, str(post_id)))

    def get_post(self, post_id):
        """ returns post object by post_id or redirects to newpost form"""
        # if user is not the author, then the statement below will return None
        post = blog.get_post(self.user.username, post_id)
        if not post:
            self.redirect("/blog/newpost", abort=True)
        else:
            return post
