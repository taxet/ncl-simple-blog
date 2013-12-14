import os

from google.appengine.api import users

#from shared.User import User
from shared.Post import Post

import jinja2
import webapp2
from newpost import NewPost
JINJA_ENVIRONMENT = jinja2.Environment(
                                       loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)

class MainPage(webapp2.RequestHandler):
    
    def get(self):
        #get user
        user = users.get_current_user()
        if user:
            log_url = users.create_logout_url(self.request.uri)
            log_text = "Log out"
            #check if in database
            """userdb_query = User.query(User.email == user.email())
            userdb_list = userdb_query.fetch()
            if userdb_list:
                pass;
            else:
                #add new entry
                userdb=User(email=user.email(),nickname=user.nickname())
                userdb.put()"""
        else:
            log_url = users.create_login_url(self.request.uri)
            log_text = "Login"
            
        #get posts
        try:
            page=self.response.get("page")
        except (TypeError, ValueError, AttributeError):
            page=1
        posts_list = Post.query().order(-Post.createdDate).fetch()
        all_page=(len(posts_list)-1)/10+1
        page = page+1
        if page>all_page:
            page=all_page
        posts = posts_list[10*(page-1):10*page-1]
        template_values={"posts":posts,
                         "posts_no":len(posts),
                         "page":page,
                         "all_page":all_page,
                         "log_url":log_url,
                         "log_text":log_text,
                         "user":user}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        
application = webapp2.WSGIApplication([('/',MainPage),
                                       ('/newpost',NewPost)],
                                      debug = True)