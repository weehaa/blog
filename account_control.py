""" This is a controller module for signup, login and logout """
from user import User as usr
import handler


class SignupPage(handler.Handler):
    """Class for the Signup Page (/signup) handler"""
    def get(self):
        """ get request """
        self.render("signup.html")

    def post(self):
        """ post request """
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        # verification of entered user params
        error_username = error_password = error_verify = error_email = ""

        if not usr.valid_username(username):
            error_username = "Username is not valid"
        else:
            if usr.by_name(username):
                error_username = "Username already exists"

        if not usr.valid_password(password):
            error_password = "Password was not valid"

        if not usr.valid_verify(password, verify):
            error_verify = "Passwords didn't match"

        if not usr.valid_email(email):
            error_email = "Email is not valid"
        else:
            if usr.email_exists(email):
                error_email = "Email already registered"

        # if any error is present - render the same signup page
        if error_username or error_password \
           or error_verify or error_email:
            self.render("signup.html", username=username, email=email,
                        error_username=error_username,
                        error_password=error_password,
                        error_verify=error_verify,
                        error_email=error_email)
        else:
            # create new user and put into db
            new_user = usr.register(username, password, email)
            new_user.put()
            self.login(new_user)
            self.redirect("/blog/welcome")


class WelcomePage(handler.Handler):
    """Class for the Welcome Page (/welcome) handler"""
    def get(self):
        """ self.user sets up in Handler initialize function """
        if self.user:
            self.render("welcome.html", username=self.user.username)
        else:
            self.redirect("/signup")


class LoginPage(handler.Handler):
    """ Class for the Login Page (/login) handler"""
    def get(self):
        """ get request """
        self.render("login.html")

    def post(self):
        """ post request """
        username = self.request.get("username")
        password = self.request.get("password")

        user = usr.get_user(username, password)
        if user:
            self.login(user)
            self.redirect("welcome")
        else:
            error_login = "Invalid login or password"
            self.render("login.html", error_login=error_login)


class LogoutPage(handler.Handler):
    """ Class for the Login Page (/login) handler """
    def get(self):
        """ get request method """
        self.logout()
        self.redirect('signup')


app = handler.webapp2.WSGIApplication([
    ('/blog/signup', SignupPage),
    ('/blog/welcome', WelcomePage),
    ('/blog/login', LoginPage),
    ('/blog/logout', LogoutPage)
], debug=True)
