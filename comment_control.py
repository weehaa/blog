"""controller module for a post page + comments"""
import handler
import post_control
import blog
import comment


class DeleteComment(post_control.PostPage):
    """ Delete comment handler """
    def initialize(self, *args, **kwargs):

        if not self.user:
            return self.redirect('/blog/login')
        # TODO add check user == comment_author

        post_control.PostPage.initialize(self, *args, **kwargs)
        uri = self.request.path_qs
        uri = uri[:uri.find('/comments') + len('/comments')]
        comment_id = self.request.get('cid')
        comment.Comment.db_delete(self.render_params['post'],
                                  comment_id,
                                  self.user.username)
        return self.redirect(uri)


class EditComment(post_control.PostPage):
    """ Edit comment handler """
    def get(self, author_name, post_id):
        """ renders post page with comments with content textarea to edit the
        selected comment """
        if not self.user:
            return self.redirect('/blog/login')
        # TODO add check user == comment_author

        self.render_params['edit_id'] = self.request.get('cid')
        self.render_params['comments'] = comment.Comment. \
                                         by_post(self.render_params['post'])
        self.render("comments.html", **self.render_params)


class AddComment(post_control.PostPage):
    """ Add comment handler """
    def get(self, author_name, post_id):
        """ renders post page with comments with empty textarea to add a
        comment """
        if not self.user:
            return self.redirect('/blog/login')

        uri = self.uri_for('post-comments',
                           author_name=author_name, post_id=post_id)

        if self.user.username == author_name:
            return self.redirect(uri)
            
        self.render_params['act'] = 'Add comment'
        self.render_params['comments'] = comment.Comment. \
                                         by_post(self.render_params['post'])
        self.render("comments.html", **self.render_params)

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
        uri = self.uri_for('post-comments',
                           author_name=author_name, post_id=post_id)

        url = '/blog/%s/%s/comments' % (author_name, post_id)
        self.post_params(author_name, post_id)

        action = self.request.get('action')

        # if action is perfomed by not logged-in user, redirect him
        # to login page.
        if action and not self.user:
            self.redirect("/blog/login")

        comment_id = self.request.get('comment_id')

        # action "Edit comment"  handler
        if action == 'Edit comment':
            # redirect user to this page with an anchor to edit comment
            return self.redirect('{}/edit?cid={}#id_{}'.format(uri,
                                                            comment_id,
                                                            comment_id))

        # action "Add comment" handler
        if action == 'Add comment':
            return self.redirect('{}/add?cid=0#id_0'.format(uri,
                                                            comment_id,
                                                            comment_id))

        # handler for "Submit" new or edited comment
        if action == 'Submit comment':
            content = self.request.get('content')
            if content:
                comment.Comment.db_put(self.render_params['post'],
                                       self.user.username,
                                       content=content,
                                       comment_id=comment_id)
                action = ''
            else:
                if comment_id:
                    error = "Please, add some content"
                    url_arg = "?edit_id=%s&error=%s#id_%s" % \
                              (comment_id, error, comment_id)
                else:
                    error = "Please, add some content"
                    url_arg = "?act=Add comment&error=%s#id_0" % error
                self.redirect(url + url_arg)

        if action == 'Delete comment':
            return self.redirect('{}/delete?cid={}'.format(uri,comment_id))

        self.render_params['action'] = action
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
