import handler
from google.appengine.ext import db
from user import User

class Comment(db.Model):

    author = db.TextProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        """
        Method for comment render
        """

        # replace new line symbols with <br> tags
        self._render_text = self.content.replace('\n', '<br>')

        base_handler = handler.BaseHandler()
        return base_handler.render_str("comment.html",
                                       comment=self)



    @classmethod
    def by_post(cls, post, limit=None):
        """Returns all comments for a post"""
        query = cls.all().order('-created').ancestor(post)
        return query.run(limit=limit)

    @classmethod
    def by_id(cls, comment_id, post_key):
        """get Comment by id"""
        return cls.get_by_id(comment_id, parent=post_key)
