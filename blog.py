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

        #check if user is deleted set author = unknown
        author_name = 'Unkown blogger'
        if author:
            author_name = author.username

        base_handler = handler.BaseHandler()
        return base_handler.render_str("post.html",
                                       post=self,
                                       author_name=author_name)


class BlogFront(handler.Handler):
    def get(self):
        #Google procedural language for GQL query
        #It is the same as
        # posts = db.GqlQuery("select * from Blog order by created desc").get()
        posts = Blog.all().order('-created').run(limit=10)

        # self.write('POSTS:' + str(len(posts)))
        self.render("front.html", posts=posts)
        # self.render("front.html")


class PostPage(handler.Handler):
    def get(self, post_id):
        key = db.Key.from_path('Blog', int(post_id), parent=self.user.key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)


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
                self.redirect("/blog/" + str(blog_id))
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
    ('/blog', BlogFront),
    ('/blog/newpost', NewPostFormPage),
    ('/blog/(\d+)', PostPage)
], debug=True)
