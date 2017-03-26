"""controller module for a single post page"""
import handler
import blog
import likes

class PostPage(handler.Handler):
    """
    Class for requested post page. If auhtor of the post is logged in,
    he can edit or delete post on the page.
    """
    def get(self, author_name, post_id):
        """get requestmethod handler. Renders single post page base on
        parameters from url + anchor to scroll to the focused action item of
        the page
        """
        render_params = self.get_postparams(author_name, post_id)
        self.render("permalink.html", **render_params)

    def get_postparams(self, author_name, post_id):
        render_params = {}
        # retrieve post object
        post = blog.get_post(author_name, post_id)
        if not post:
            self.error(404)
            return
        else:
            render_params['post'] = post

        # retrive user's like
        if self.user and likes.Likes.by_username(post, self.user.username):
            render_params['like_st'] = 'Dislike'
        else:
            render_params['like_st'] = 'Like'
        return render_params

    def post(self, author_name, post_id):
        render_params = self.post_postparams(author_name, post_id)
        self.render("permalink.html", **render_params)

    def post_postparams(self, author_name, post_id):
        """Method handles post request for a single post page.
        Returns response, based on user actions from permalink.html
        'actions' form, such as delete post with confirmation, edit post,
        add comment, like or dislike a post.
        Adds comment to a database after comment content validation.
        Parameters:
        author_name -- post author name, taken from url
        post_id -- post id, taken from url
        """
        post_params = {}

        # action_delete is a confirmed deletion of the post
        action_delete = self.request.get('action_delete')
        action = self.request.get('action')

        # if action is perfomed by not logged-in user, redirect him
        # to login page.
        if (action or action_delete) and not self.user:
            self.redirect("/blog/login")

        # get the post object
        post = blog.get_post(author_name, post_id)
        if not post:
            self.error(404)
            return

        # if post deletion is confirmed,
        # and logged in user is an author of the post, delete the post
        if action_delete and self.user.username == author_name:
            post.delete()
            post_params['post_deleted'] = True
        else:
            post_params['post'] = post

            # user actions handlers block
            # Edit post handler
            if action == 'Edit':
                # redirect user to postform page with post id
                self.redirect("/blog/newpost?post_id=" + post_id)

            # Like/dislike post handler
            if action in ('Like', 'Dislike'):
                # check that user logged in and not an author of the post
                # to prevent cheating
                if self.user and (author_name != self.user.username):
                    # switch like/Dislike
                    likes.Likes.set(post, self.user.username)
            # retrive user's like
            if self.user and likes.Likes.by_username(post, self.user.username):
                post_params['like_st'] = 'Dislike'
            else:
                post_params['like_st'] = 'Like'

            post_params['action'] = action

app = handler.webapp2.WSGIApplication([
    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)', PostPage)
], debug=True)
