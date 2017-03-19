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
