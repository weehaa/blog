import handler
import blog
from user import User


class RootRedirect(handler.Handler):
    '''
    Class handler for the root url
    '''
    def get(self):
        # redirect to a /blog url
        self.redirect("/blog")


class BlogFront(handler.Handler):
    """
    Class for a front page handler
    """
    def get(self):
        """
        Method for a get response.
        Takes author_name from url and returns all author's posts.
        If there is no author_name in url, return all posts.
        """
        # get author from url parameters
        author_name = self.request.get("author_name")
        # TODO: add filter feature and take limit from get request
        limit = 10
        posts = blog.Blog.get_posts(author_name, limit)

        self.render("front.html", author_name=author_name, posts=posts)


class PostPage(handler.Handler):
    def get(self, author, post_id):
        author_key = User.by_name(author).key()
        post = blog.get_post(post_id, author_key)
        if not post:
            self.error(404)
            return

        self.render("permalink.html", post=post)

    def post(self, author, post_id):
        action = self.request.get('action')
        if action == 'delete':
            self.write('OK')

class NewPostFormPage(handler.Handler):
    def get(self):
        referer = self.request.referer
        post_id = self.request.get("post_id")
        subject = content = ''
         # show newpost page if user has logged in
        if self.user:
            if post_id:
                post = blog.get_post(post_id, self.user.key())
                if post:
                    subject = post.subject
                    content = post.content
                else:
                    self.redirect("/blog/newpost")
            self.render_post(referer, subject, content)
        else:
            self.redirect("/blog/login")

    def post(self):
        referer = self.request.get("referer")
        post_id = self.request.get("post_id")
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            if post_id:
                post = blog.get_post(post_id, self.user.key())
            # if not the author tries to edit, then redirect to empty form
                if post:
                    post.content = content
                    post.subject = subject
                else:
                    self.redirect("/blog/newpost")
            # if no post_id -> new post
            else:
                post = blog.Blog(parent=self.user,
                                 subject=subject,
                                 content=content)
            post.put()
            if not post_id:
                post_id = post.key().id()
            self.redirect("/blog/%s/%s" %
                          (self.user.username, str(post_id))
                          )
        else:
            error = "we need both a subject and some content!"
            self.render_post(referer, subject, content, error)

    def render_post(self, referer, subject, content,  error=''):
        self.render("newpost.html", referer=referer,
                                    subject=subject,
                                    content=content,
                                    error=error)


app = handler.webapp2.WSGIApplication([
    # root path redirection
    ('/', RootRedirect),
    # front page
    ('/blog/?', BlogFront),
    # new post form
    ('/blog/newpost', NewPostFormPage),
    # post page (/blog/username/post_id )
    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)', PostPage)
], debug=True)
