""" This module contains a class for User object """

import re
from google.appengine.ext import db
from passlib.hash import pbkdf2_sha256 as sha


class User(db.Model):
    """
    This class determins user GAE entity properties
    and some methods for user checks,
    password hashing, username, password and email
    regular expression templatres verification
    """

    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty(required=False)

    @classmethod
    def by_id(cls, uid):
        """get User by id"""
        return cls.get_by_id(uid)

    @classmethod
    def by_name(cls, username):
        """get User by name"""
        query = db.GqlQuery("select * from User where username=:1", username)
        user = query.get()
        return user

    @classmethod
    def valid_username(cls, username):
        """
        check that entered username contains only letters, digits
        dash or and underscores
        """
        user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return user_re.match(username)

    @classmethod
    def valid_password(cls, password):
        """
        check that length of entered password is between 3 and 20
        characters
        """
        pass_re = re.compile(r"^.{3,20}$")
        return pass_re.match(password)

    @classmethod
    def valid_verify(cls, password, verify):
        """check that passwords match"""
        return password == verify

    @classmethod
    def valid_email(cls, email):
        """check that email has no spaces, has at sign and dot"""
        email_re = re.compile(r"^[\S]+@[\S]+.[\S]+$")
        if email_re.match(email) or not email:
            return True

    @classmethod
    def email_exists(cls, email):
        """check if entered email exists in the database"""
        if email:
            query = db.GqlQuery("select * from User where email=:1", email)
            q_email = query.get()
            if q_email:
                return True

    @classmethod
    def check_password(cls, username, password):
        """password verification"""
        user = cls.by_name(username)
        if user:
            return sha.verify(password, user.pw_hash)

    @classmethod
    def register(cls, username, password, email=None):
        """create new User object without saving it to the DB"""
        pw_hash = sha.hash(password)
        return User(username=username,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def get_user(cls, username, password):
        """get exisiting User object from DB with password verify"""
        user = cls.by_name(username)
        if user and cls.check_password(username, password):
            return user
