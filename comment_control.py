"""controller module for a post page + comments"""
import handler
import post_control
import blog
import comment


class UserCommentHandler(post_control.PostPage):
    """ Ascendor class for all comment handlers where
    user check is needed """
    def initialize(self, *args, **kwargs):
        """ Not logged in user redirect to login page"""
        post_control.PostPage.initialize(self, *args, **kwargs)
        if not self.user:
            uri = '/blog/login'
            return self.redirect(uri)


class DeleteComment(UserCommentHandler):
    """ Delete comment handler """
    def get(self, author_name, post_id):
        """ The method deletes a comment. Checks if the user is logged in
        (in UserCommentHandler initialize method), checks that user is an
        author of the comment. If all the checks sucsseed, deletes the
        comment and redirects to a post+comments page with a delete message"""
        comment_id = self.request.get('cid')
        uri = self.uri_for('post-comments',
                           author_name=author_name,
                           post_id=post_id)
        if check_author(self.render_params['post'].key(),
                        comment_id,
                        self.user.username):
            comment.Comment.db_delete(self.render_params['post'],
                                      comment_id,
                                      self.user.username)
            uri = self.uri_for('post-comments',
                               author_name=author_name,
                               post_id=post_id,
                               delete_msg='Commment deleted')
        return self.redirect(uri)


class EditComment(UserCommentHandler):
    """ Edit comment handler """
    def get(self, author_name, post_id):
        """ renders post page with comments with content textarea to edit the
        selected comment """

        # TODO add check user == comment_author

        self.render_params['edit_id'] = self.request.get('cid')

        self.render_params['comments'] = comment.Comment. \
                                         by_post(self.render_params['post'])
        self.render("comments.html", **self.render_params)

    def post(self, author_name, post_id):
        """ updates a comment or renders an error"""
        action = self.request.get('action_comment')
        comment_id = self.request.get('comment_id')
        uri = self.uri_for('post-comments', author_name=author_name,
                           post_id=post_id, _fragment='cid_' + str(comment_id))
        if action == 'Submit comment' \
           and check_author(self.render_params['post'].key(),
                            comment_id,
                            self.user.username):
            content = self.request.get('content')
            error, comment_id = submit_comment(self.render_params['post'],
                                               self.user.username,
                                               content=content,
                                               comment_id=comment_id)
            if error:
                uri = self.uri_for('comment-edit', author_name=author_name,
                                   post_id=post_id, error=error)
        return self.redirect(uri)


class AddComment(UserCommentHandler):
    """ Add comment handler """
    def get(self, author_name, post_id):
        """ renders post page with comments with empty textarea to add a
        comment """
        uri = self.uri_for('post-comments',
                           author_name=author_name, post_id=post_id)

        if self.user.username == author_name:
            return self.redirect(uri)
        self.render_params['error'] = self.request.get('error')
        self.render_params['act'] = 'Add comment'
        self.render_params['comments'] = comment.Comment. \
                                         by_post(self.render_params['post'])
        self.render("comments.html", **self.render_params)

    def post(self, author_name, post_id):
        """ Submits a comment a render a error message """
        uri = self.uri_for('post-comments',
                           author_name=author_name, post_id=post_id)

        action = self.request.get('action_comment')
        if action == 'Submit comment':
            content = self.request.get('content')
            error, comment_id = submit_comment(self.render_params['post'],
                                               self.user.username,
                                               content=content)
            if error:
                uri = self.uri_for('comment-add', author_name=author_name,
                                   post_id=post_id, error=error)
            else:
                uri = self.uri_for('post-comments',
                                   author_name=author_name,
                                   post_id=post_id,
                                   _fragment='cid_' + str(comment_id))
        return self.redirect(uri)


def submit_comment(post, username, content, comment_id=None):
    """submits comment to db and returns None
    or returns an error """
    if content:
        error, comment_id = None, comment.Comment.db_put(post, username,
                                            content, comment_id)
    else:
        error, comment_id = 'Please, add some content', None
    return error, comment_id

def check_author(post_key, comment_id, username):
    """ Checks is current user is the author of a comment """
    if comment_id and comment_id.isdigit():
        comm = comment.Comment.by_id(int(comment_id), post_key)
        if comm:
            return comm.author == username


class PostCommentsPage(post_control.PostPage):
    """
    Class for requested post page with comments.
    If auhtor of the post is logged in,
    he can add a new comment, edit or delete his existing one.
    """
    def get(self, author_name, post_id):
        """get request method handler. Renders single post page base on
        parameters from url + anchor to scroll to the focused action item of
        the page
        """
        # user action
        self.render_params['act'] = self.request.get('act')
        # error while comment editing
        self.render_params['error'] = self.request.get('error')
        # delete message
        self.render_params['delete_msg'] = self.request.get('delete_msg')
        # retrieve all comments for the post
        self.render_params['comments'] = \
            comment.Comment.by_post(self.render_params['post'])
        self.render("comments.html", **self.render_params)

    def post(self, author_name, post_id):
        """Method handles post request for a single post page with comments.
        Returns response, based on user actions from comments.html
        'actions' form, such as add/edit/delete comment.
        Adds comment to a database after comment content validation.
        Parameters:
        author_name -- post author name, taken from url
        post_id -- post id, taken from url
        """
        self.post_params(author_name, post_id)
        comment_id = self.request.get('comment_id')
        uri = self.uri_for('post-comments',
                           author_name=author_name, post_id=post_id)
        action = self.request.get('action_comment')
        # if action is perfomed by not logged-in user, redirect him
        # to login page.
        if action and not self.user:
            self.redirect("/blog/login")

        if action == 'Edit comment':
            # redirect user to this page with an anchor to edit comment
            return self.redirect('{}/edit?cid={}#cid_{}'.format(uri,
                                                                comment_id,
                                                                comment_id))
        if action == 'Add comment':
            return self.redirect('{}/add?cid=0#cid_0'.format(uri))
        if action == 'Delete comment':
            return self.redirect('{}/delete?cid={}'.format(uri, comment_id))

        self.render_params['comments'] = comment.Comment. \
                                         by_post(self.render_params['post'])
        self.render("comments.html", **self.render_params)

app = handler.webapp2.WSGIApplication([
    handler.webapp2.Route('/blog/<author_name>/<post_id>/comments',
                          handler=PostCommentsPage, name='post-comments'),
    handler.webapp2.Route('/blog/<author_name>/<post_id>/comments/delete',
                          handler=DeleteComment, name='comment-delete'),
    handler.webapp2.Route('/blog/<author_name>/<post_id>/comments/edit',
                          handler=EditComment, name='comment-edit'),
    handler.webapp2.Route('/blog/<author_name>/<post_id>/comments/add',
                          handler=AddComment, name='comment-add'),
    handler.webapp2.Route('/blog/<author_name>/<post_id>',
                          handler='post_control.PostPage', name='post'),
], debug=True)
