import handler
from google.appengine.ext import db
from user import User

class Blog(db.Model):

    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    comment_cnt = db.IntegerProperty(required = True, default = 0)
    like_cnt = db.IntegerProperty(required = True, default = 0)

    def render(self):
        """
        Method for post render
        actualy, it is a controller method
        """

        # replace new line symbols with <br> tags
        self._render_text = self.content.replace('\n', '<br>')

        # get an author of the post = it's parent User
        author = self.parent()

        base_handler = handler.BaseHandler()
        return base_handler.render_str("post.html",
                                       post=self)

    @classmethod
    def get_posts(cls, author_name=None, limit=None):
        """Return posts, added by author_name ordered by created DateTime.
        If author_name is not specified, return posts of all authors.
        If author_name is specified, but does not exist, return None
        A number of return posts is limited by limit
        Arguments:
        author_name -- a blogger username, a string or None (default None)
        limit -- number of posts to return, an integer or None (default None)
        """
        query = cls.all().order('-created')
        if author_name:
            user = User.by_name(author_name)
            if user:
                query.ancestor(user)
            # if user not found, return None
            else:
                return
        return query.run(limit=limit)


def get_post(author_name, post_id):
    """Get post by post_id and username"""
    author_key = User.by_name(author_name).key()
    post_key = db.Key.from_path('Blog', int(post_id), parent=author_key)
    return db.get(post_key)
