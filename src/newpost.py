from google.appengine.api import users

import webapp2

from shared.Post import Post

class NewPost(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            title = self.request.get('post_title')
            author= user.email()
            content = self.request.get('post_content')
            tags=self.request.get('post_tags').split(" ")
            post = Post()
            post.title = title
            post.authors.append(author)
            post.content = content
            post.tags = list(set(tags))
            post.views = 0
            post.thumbUp = 0
            post.thumbDown = 0
            post.put()
            self.response.write("<html><body>Post succeed</body></html>")
            #self.redirect('/')
        else:
            self.response.write("<html><body>Not Logged In </body></html>")
            return