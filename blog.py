import handler
from google.appengine.ext import db

def blog_key(name = 'default'):
    return db.Key.from_path('/', name)


class Blog(db.Model):

    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    #author = db.StringProperty()

    def render(self):
        """
        Method for post render
        """

        # replace new line symbols with <br> tags
        self._render_text = self.content.replace('\n', '<br>')


        # get an author of the post = it's parent User
        author = self.parent()

        # check if user is deleted set author = unknown
        # TODO get rid of this, problems with a permalink?
        author_name = 'Unkown blogger'
        if author:
            author_name = author.username

        base_handler = handler.BaseHandler()
        return base_handler.render_str("post.html",
                                       post=self,
                                       author_name=author_name)

class RootRedirect(handler.Handler):
    def get(self):
        self.redirect("/blog")


class BlogFront(handler.Handler):
    def get(self, author=''):

        if not author:
            # get author from url parameters
            author_name = self.request.get("author_name")
            if author_name:
                author = handler.User.by_name(author_name)
                if author:
                    posts = Blog.all().ancestor(author)
                else:
                    posts = None
            else:
                posts = Blog.all().order('-created').run(limit=10)


            self.render("front.html", posts=posts)

        else:
            key = db.Key.from_path('Blog', str(author))


class PostPage(handler.Handler):
    def get(self, author, post_id):
        author_key = db.Key.from_path('AVes', 'User')
        self.write('Author: ' + str(author_key))
        author_obj = db.get(author_key)
        # self.write('<br>Author_name: ' + str(author_obj.username))
        post_key = db.Key.from_path('Blog', int(post_id), parent=author_key)
        self.write('<br>post: ' + str(post_key))
        post = db.get(post_key)
        self.write('<br>post: ' + str(post))
        # if not post:
        #     self.error(403)
        #     return

        # self.render("permalink.html", post = post)


class NewPostFormPage(handler.Handler):
        def get(self):
            if self.user:
                self.render("newpost.html")
            else:
                self.redirect("/blog/login")

        def post(self):

            subject = self.request.get("subject")
            content = self.request.get("content")

            if subject and content:
                blog_entity = Blog(parent=self.user,
                                   subject=subject,
                                   content=content)
                blog_entity.put()
                blog_id = blog_entity.key().id()
                self.redirect("/blog/%s/%s" %
                              (self.user.username, str(blog_id)))
            else:
                error = "we need both a subject and some content!"
                self.render("newpost.html", subject = subject,
                                            content = content,
                                            error = error)


class MainPage(handler.Handler):
    def render_front(self, subject="", content="", error=""):

        contents = db.GqlQuery("SELECT * FROM Blog "
                            "ORDER BY created DESC")

        self.render("front.html", subject=subject, content= content,
                    error=error, contents = contents)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            a = Blog(subject = subject, content = content)
            a.put()
            self.redirect("/")
        else:
            error = "we need both a subject and some contentwork!"
            self.render("newpost.html", subject, content, error)

app = handler.webapp2.WSGIApplication([
    ('/', RootRedirect),
    ('/blog', BlogFront),
    ('/blog/newpost', NewPostFormPage),
    ('/blog/([A-Za-z0-9\-\_]+)', BlogFront),

    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)', PostPage)
], debug=True)
