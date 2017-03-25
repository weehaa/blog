import handler
from google.appengine.ext import db
from user import User

class Comment(db.Model):

    author = db.TextProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self, isedit=False):
        """
        Method for comment render
        Arguments:
        isedit -- flag for the comment edit status
        """
        # replace new line symbols with <br> tags
        self._render_text = self.content.replace('\n', '<br>')
        base_handler = handler.BaseHandler()
        return base_handler.render_str("comment.html",
                                       comment=self,
                                       isedit=isedit)


    @classmethod
    def db_put(cls, parent_post, username, content, comment_id=None):
        """Method to insert new comment or update an existing one"""
        if comment_id.isdigit():
            comment = cls.by_id(int(comment_id), parent_post.key())
            if comment:
                comment.content = content
            else:
                return
        else:
            comment = cls(parent=parent_post,
                                    author=username,
                                    content=content)
            # update  comment counter for parent post
            parent_post.comment_cnt += 1

        if comment.author == username:
            parent_post.put()
            comment.put()

    @classmethod
    def db_delete(cls, parent_post, comment_id, username):
        if comment_id.isdigit():
            comment = cls.by_id(int(comment_id), parent_post.key())
            if comment and comment.author == username:
                parent_post.comment_cnt -= 1
                parent_post.put()
                comment.delete()

    @classmethod
    def by_post(cls, post, limit=None):
        """Returns all comments for a post"""
        query = cls.all().order('-created').ancestor(post)
        return query.run(limit=limit)

    @classmethod
    def by_id(cls, comment_id, post_key):
        """get Comment by id"""
        return cls.get_by_id(comment_id, parent=post_key)
