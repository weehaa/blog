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


class NewPostFormPage(handler.UserPostHandler):
    """Class for page form submission to add a new or edit an existing post"""
    def get(self):
        """Get request handler for a post form page"""
        self.render("newpost.html")

    def post(self):
        """post request handler for a post form page"""
        subject = self.request.get("subject")
        content = self.request.get("content")
        error, post_id = blog.Blog.put_post(self.user, subject, content)
        if error:
            self.render("newpost.html", subject=subject,
                        content=content, error=error)
        else:
            self.redirect("/blog/%s/%s" %
                          (self.user.username, str(post_id)))


app = handler.webapp2.WSGIApplication([
    # root path redirection
    ('/', RootRedirect),
    # front page
    ('/blog/?', BlogFront),
    # new post form
    ('/blog/newpost', NewPostFormPage)
], debug=True)
