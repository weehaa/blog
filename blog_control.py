"""controller module for a blog pages"""
import handler
import blog


class RootRedirect(handler.Handler):
    '''
    Class handler for the root url
    '''
    def get(self):
        """get request handler"""
        self.redirect("/blog")


class BlogFront(handler.Handler):
    """
    Class for a front page handler
    """
    def get(self):
        """
        Method for a get response.
        Takes author_name parameter from request and returns
        author's posts.
        If there is no author_name in request, return posts of all authors.
        Number of posts is limited by limit parameter (default 10, max 99).
        TODO: add pagination
        """
        # get author from url parameters
        author_name = self.request.get("author_name")
        # validate author_name
        if not handler.User.valid_username(author_name):
            author_name = ''

        limit = self.request.get("limit")
        # validate limit
        if limit.isdigit() and len(limit) < 3:
            limit = int(limit)
        else:
            limit = 10
        posts = blog.Blog.get_posts(author_name, limit)

        self.render("front.html",
                    author_name=author_name,
                    limit=limit,
                    posts=posts)


class NewPostFormPage(handler.Handler):
    """Class for page form submission to add a new or edit an existing post"""
    def get(self):
        """get request handler for a post form page"""
        referer = self.request.referer
        post_id = self.request.get("post_id")
        subject = content = ''
        # show newpost page if user has logged in
        if self.user:
            if post_id:
                post = blog.get_post(self.user.username, post_id)
                if post:
                    subject = post.subject
                    content = post.content
                else:
                    self.redirect("/blog/newpost")
            self.render_post(referer, subject, content)
        else:
            self.redirect("/blog/login")
            return

    def post(self):
        """post request handler for a post form page"""

        if not self.user:
            self.redirect("/blog/login")
            return

        referer = self.request.get("referer")
        post_id = self.request.get("post_id")
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            if post_id:
                post = blog.get_post(self.user.username, post_id)
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
                          (self.user.username, str(post_id)))
        else:
            error = "we need both a subject and some content!"
            self.render_post(referer, subject, content, error)

    def render_post(self, referer, subject, content, error=''):
        self.render("newpost.html",
                    referer=referer,
                    subject=subject,
                    content=content,
                    error=error)


app = handler.webapp2.WSGIApplication([
    # root path redirection
    ('/', RootRedirect),
    # front page
    ('/blog/?', BlogFront),
    # new post form
    ('/blog/newpost', NewPostFormPage)
], debug=True)
