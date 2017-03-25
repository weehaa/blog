""" This module contains a Class for Like objects """

from google.appengine.ext import db

class Likes(db.Model):
    """A class for Like db GAE entity
    it can be used f post's and comment's likes
    'Liked' post or comment is a parent for Like object
    """
    username = db.StringProperty(required = True)
    # TODO: add flag for a dislike support. In this case
    # like (flag = True) dislike (flag = False). No reaction - no record
    # flag = db.BooleanProperty(required = True, default = True)

    @classmethod
    def set(cls, parent, username):
        """Put like to db for a parent post and a username
        ('Like' button pressed).
        If like already exists, delete it from db ('Dislike')
        Update a counter in parent entity
        """
        like = cls.by_username(parent, username)
        if like:
            like.delete()
            parent.like_cnt -= 1
        else:
            like = cls(parent=parent,
                        username=username)
            parent.like_cnt += 1
            like.put()
        parent.put()


    @classmethod
    def by_username(cls, parent, username):
        """Get like for a parent post or comment by username"""
        parent_key = parent.key()
        like = cls.all()
        like.filter('username =', username)
        like.ancestor(parent_key)
        return like.get()
