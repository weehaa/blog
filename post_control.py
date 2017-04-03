"""controller module for a single post page"""
import handler
import blog
import likes


class TestPost(handler.UserPostHandler):
    """ Test class, delete it """
    def initialize(self,  *a, **kw):
        handler.UserPostHandler.initialize(self, *a, **kw)
        self.args = self.request.route_kwargs
        # self.args = self.request.path.split('/')
    def get(self, author):
        self.write("TEST %s" % str(self.args))


class LikePost(handler.UserPostHandler):
    """ Class for a post page edit form """
    def get(self, author_name, post_id):
        """ Get request method handler. Sets like/dislike """
        post = blog.get_post(author_name, post_id)
        if not post:
            self.error(404)
            return
        if self.user.username != author_name:
            # switch like/Dislike
            likes.Likes.set(post, self.user.username)
        referer = self.request.referer
        if referer:
            self.redirect(referer)
        else:
            self.redirect("/blog/%s/%s" % (author_name, str(post_id)))


class DeletePost(handler.UserPostHandler):
    """ Delete post handler """
    def get(self, author_name, post_id):
        """ Get request handler for delete post action """
        post = self.get_post(post_id)
        self.render("permalink.html", post=post, action='Delete')

    def post(self, author_name, post_id):
        """Post request handler for a confirmation to delete post action"""
        post = self.get_post(post_id)
        action = self.request.get('action')
        if action == 'Confirm':
            post.delete()
            self.render("permalink.html", post_deleted=True)
            return
        self.redirect("/blog/%s/%s" % (self.user.username, str(post_id)))


class EditPost(handler.UserPostHandler):
    """ Class for a post page edit form """
    def get(self, author_name, post_id):
        """ Get request method handler. Renders single post page edit form """
        post = self.get_post(post_id)
        self.render("newpost.html", post_id=post_id,
                    subject=post.subject, content=post.content)

    def post(self, author_name, post_id):
        """Post request handler for a edit post form page"""
        post = self.get_post(post_id)
        self.add_edit_post(post)


class PostPage(handler.Handler):
    """
    Class for requested post page. If auhtor of the post is logged in,
    he can edit or delete post on the page.
    """
    def params(self, author_name, post_id):
        """ retrieve post instance and it's user's like status
        into render parameters dict"""
        self.render_params = {}
        post = blog.get_post(author_name, post_id)
        if not post:
            self.error(404)
            return
        else:
            self.render_params['post'] = post
        if likes.Likes.by_username(post, self.user.username):
            self.render_params['like_st'] = 'Dislike'
        else:
            self.render_params['like_st'] = 'Like'

    def get(self, author_name, post_id):
        """ Get request method handler. Renders single post page base on
        parameters  author_name and post_id """
        self.params(author_name, post_id)
        self.render("permalink.html", **self.render_params)

    def post(self, author_name, post_id):
        """ Post request handler. Renders single post page base on
        parameters from post request. If user pushes an action,
        redirects it to the corresponding page"""
        self.post_params(author_name, post_id)

    def post_params(self, author_name, post_id):
        self.params(author_name, post_id)
        action = self.request.get('action')
        if action:
            uri = self.uri_for('blogg', author=author_name)
            self.redirect(uri)
            # self.redirect("/blog/%s/%s/%s" %
            #               (author_name,
            #               str(post_id),
            #               action.lower()))

app = handler.webapp2.WSGIApplication([
handler.webapp2.Route('/blog/<author>/test', handler=TestPost, name='blogg'),
    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)', PostPage),
    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)/edit', EditPost),
    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)/delete', DeletePost),
    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)/like', LikePost),
    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)/dislike', LikePost),

], debug=True)
