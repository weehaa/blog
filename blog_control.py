import handler
import blog


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


class PostPage(handler.Handler):
    """
    Class for requested post page. If auhtor of the post is logged in,
    he can edit or delete post on the page.
    """
    def get(self, author_name, post_id):

        post = blog.get_post(author_name, post_id)
        if not post:
            self.error(404)
            return

        self.render("permalink.html", post=post)

    def post(self, author_name, post_id):
        action = self.request.get('action')
        action_delete = self.request.get('action_delete')
        post = blog.get_post(author_name, post_id)
        if not post:
            self.error(404)
            return

        if action:
            if action == 'Edit':
                self.redirect("/blog/newpost?post_id=" + post_id)
            else:
                self.render("permalink.html", post=post, action=action)

        elif action_delete and self.user.username == author_name:
            post.delete()
            self.render("permalink.html", post_deleted=True)

        else:
            self.render("permalink.html", post=post)


class NewPostFormPage(handler.Handler):
    def get(self):
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

    def post(self):
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
