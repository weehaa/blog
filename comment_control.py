"""controller module for a post page + comments"""
import handler
import post_control
import blog
import comment


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
        # call a inherited method from PostPage Class
        self.params(author_name, post_id)
        # comment id that is edited
        self.render_params['edit_id'] = self.request.get('edit_id')
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
            url_arg = '?edit_id=%s#id_%s' % (comment_id, comment_id)
            self.redirect(url + url_arg)

        # action "Add comment" handler
        if action == 'Add comment':
            # redirect user to this page with anchor to empty comment form
            if self.user.username == author_name:
                error = "You can't comment your own post"
                url_arg = "?error=%s#id_0" % error
            else:
                url_arg = '?act=Add comment#id_0'
            self.redirect(url + url_arg)

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
            comment.Comment.db_delete(self.render_params['post'],
                                      comment_id,
                                      self.user.username)
            action = ''

        self.render_params['action'] = action
        self.render_params['comments'] = comment.Comment. \
                                         by_post(self.render_params['post'])
        self.render("comments.html", **self.render_params)

app = handler.webapp2.WSGIApplication([
    # post + comments page (/blog/username/post_id/comments )
    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)/comments', PostCommentsPage)
], debug=True)
