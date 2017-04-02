"""model module contains a class for post db GAE entity """
import handler
from google.appengine.ext import db
from user import User


class Blog(db.Model):
    """A class for Blog db GAE entity"""
    # post title property
    subject = db.StringProperty(required=True)
    # post text propperty
    content = db.TextProperty(required=True)
    # Creation date time
    created = db.DateTimeProperty(auto_now_add=True)
    # Modification date time
    last_modified = db.DateTimeProperty(auto_now=True)
    # Comments counter
    comment_cnt = db.IntegerProperty(required=True, default=0)
    # likes counter
    like_cnt = db.IntegerProperty(required=True, default=0)

    #TODO: need to use separate entity for counters - last_modified date bug!

    def render(self):
        """
        Method for post render
        actualy, it is a controller method
        """

        # replace new line symbols with <br> tags
        self._render_text = self.content.replace('\n', '<br>')

        # get an author of the post = it's parent username
        if self.parent():
            self.author = self.parent().username
        else:
            # if user is deleted, but his post exist
            self.author = "Unknown"

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
                query.ancestor(user.key())
            # if user not found, return None
            else:
                return
        return query.run(limit=limit)

    @classmethod
    def put_post(cls, user, subject, content, post=None):
        """Method to update an existing post or insert a new one,
        returns a tupple (error, post_id)
        If a subject or a content is None - returns an error, None as post_id
        Else - returns None as error, id of post as post_id
        Arguments:
        user -- a `User` instance
        subject -- a subject of the post
        content -- a content of the post
        post -- a `Blog` instance, if None, creates a new instance.
        """
        if not (subject and content):
            return  ("Subject and content should not be blank!", None)
        if post:
            post.subject = subject
            post.content = content
        else:
            post = cls(parent=user, subject=subject, content=content)
        post.put()
        return (None, post.key().id())

    @classmethod
    def commentcount_fix(cls, posts=None):
        """method for fix comments count"""
        if not posts:
            posts = cls.get_posts()
        for post in posts:
            query = db.GqlQuery("select * from Comment where ANCESTOR IS :1",
                                post)
            cnt = query.count()
            post.comment_cnt = cnt
            post.put()
        return "fix complete"

def get_post(author_name, post_id):
    """Get post by post_id and username"""
    author_key = User.by_name(author_name).key()
    return Blog.get_by_id(int(post_id), parent=author_key)
