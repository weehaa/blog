"""controller module for a blog pages"""
import handler
import blog
import comment
import likes


class RootRedirect(handler.Handler):
    '''
    Class handler for the root url
    '''
    def get(self):
        """get request handler"""
        # redirect to a /blog url
        self.redirect("/blog")
        # self.write(blog.Blog.commentcount_fix())
        # post = blog.get_post('AVes',5034182707249152)
        # self.write(post.subject)
        #
        # self.write('Likes: ' + likes.Likes.by_post(post,'user1').username)


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
        """get requestmethod handler. Renders single post page base on
        parameters from url + anchor to scroll to the focused action item of
        the page
        """
        render_params = {}
        # comment id that is edited
        render_params['edit_id'] = self.request.get('edit_id')
        # user action
        render_params['act'] = self.request.get('act')
        # error while comment editing
        render_params['error'] = self.request.get('error')

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
        # retrieve all comments for the post
        render_params['comments'] = comment.Comment.by_post(post)

        self.render("permalink.html", **render_params)

    def post(self, author_name, post_id):
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

            # Edit comment handler
            if action == 'Edit comment':
                comment_id = self.request.get('comment_id')
                # redirect user to this page with an anchor to edited comment
                url_arg = 'edit_id=%s#id_%s' % (comment_id, comment_id)
                self.redirect("/blog/%s/%s?%s" %
                              (author_name, post_id, url_arg))
            # Add comment handler
            if action == 'Add comment':
                # redirect user to this page with anchor to empty comment form
                if self.user.username == author_name:
                    error = "You can't comment your own post"
                    url_arg = "error=%s#id_0" % error

                else:
                    url_arg = 'act=Add comment#id_0'

                self.redirect("/blog/%s/%s?%s" %
                              (author_name, post_id, url_arg))

            # handler for Submit new or edited comment
            if action == 'Submit comment':
                content = self.request.get('content')
                comment_id = self.request.get('comment_id')
                if content:
                    comment.Comment.db_put(post, self.user.username,
                                           content=content,
                                           comment_id=comment_id)
                else:
                    if comment_id:
                        error = "Please, add some content"
                        url_arg = "edit_id=%s&error=%s#id_%s" % \
                                  (comment_id, error, comment_id)
                    else:
                        error = "Please, add some content"
                        url_arg = "act=Add comment&error=%s#id_0" % error

                    self.redirect("/blog/%s/%s?%s" %
                                  (author_name, post_id, url_arg))

            if action == 'Delete comment':
                comment_id = self.request.get('comment_id')
                comment.Comment.db_delete(post, comment_id, self.user.username)

            post_params['action'] = action

        post_params['comments'] = comment.Comment.by_post(post)

        self.render("permalink.html", **post_params)




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

    def post(self):
        """post request handler for a post form page"""
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
    ('/blog/newpost', NewPostFormPage),
    # post page (/blog/username/post_id )
    ('/blog/([A-Za-z0-9\-\_]+)/(\d+)', PostPage)
], debug=True)
