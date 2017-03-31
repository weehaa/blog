GAE multiuser blog without JS</br>
Simple multiuser blog is built using Google App Engine
# Installation
Download and Install the GAE SDK for python here: https://cloud.google.com/appengine/docs/standard/python/download
Clone the source code to your local directory: 
```bash
git clone git@github.com:weehaa/blog.git
```
## Run
cd to directory where you have cloned the project and run the app server: `dev_appserver.py` .

### Modules info
This app is based on MVC (model - view - controller) model.
#### Model modules 
  are stored at /models folder, basicaly contain a GAE entity DB classes:</br>
  `user.py` - user GAE entity class</br>
  `blog.py` - blog post GAE entity class, a descendor of a user entity</br>
  `comment.py` - comment GAE entity class, a descendor of a blog entity</br>
  `likes.py` - "likes" GAE entity class, a descendor of a blog entity</br>
#### Controller modules</br>
  `account_control.py` - handles user signup, login and logout</br>
  `blog_control.py` - contains front page and newpost render handlers</br>
  `post_control.py` - contains post page and likes render handler</br>
  `comment_control.py` - contains comment render handlers</br>
#### Views modules</br>
  are the jinja templates:</br>
  `base.html` - headers and top menu</br>
  `front.html` - front page of the blog</br>
  `newpost.html` - form to add new or edit existing post (TODO: rename to formpost.html)</br>
  `permalink.html` - single post page where user can "like" or left comment to the post. The author can edit or delete his post here.</br>
  `post.html` - single post template to render it on any page</br>
  `comment.html` - single new/existing comment template for render it inside `comments.html`</br>
  `comments.html` - "Comments" title, comment form with Add/Edit/Delete buttons</br>
  
