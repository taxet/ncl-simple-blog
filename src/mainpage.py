import os

from google.appengine.api import users

from shared.Data import User
from shared.Data import Post
from shared.Data import Tag

import jinja2
import webapp2

from newpost import NewPost
from newpost import NewBlog
from newpost import EditPost
from newpost import EditSubmit
from newpost import UploadImage
from page import PostPage
from page import UpPost
from page import DownPost
from page import TagPage
from page import BlogPage
from page import WarningPage
from page import NewBlogPage
from page import BlogTagPage
from page import BlogPicPage
from page import PicPage
from page import RssPage

JINJA_ENVIRONMENT = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)

class Page:
    start_page=1
    curr_page=1
    end_page=1
    all_page=1
    
    def set_curr_page(self,curr_page):
        self.curr_page=curr_page
        if self.curr_page>self.all_page:
            self.curr_page = self.all_page
        if self.curr_page<1:
            self.curr_page = 1
        self.start_page=curr_page/10*10+1
        self.end_page=curr_page/10*10+10
        if self.end_page>self.all_page:
            self.end_page = self.all_page
        self.end_page +=1
            
    def get_page_url(self,page):
        return "/?page="+str(page)
    
    def get_page_html(self,page):
        if self.curr_page==page:
            return str(page)+" "
        else:
            return '<a href="'+self.get_page_url(page)+'">'+str(page)+'</a> '
    def get_html(self):
        result=""
        #get head and previous
        if self.curr_page != 1:
            result+='<a href="'+self.get_page_url(1)+'">'+'|&lt;'+'</a> '
            result+='<a href="'+self.get_page_url(self.curr_page-1)+'">'+'&lt;&lt;'+'</a> '
        #get pages from start to end
        for i in range(self.start_page,self.end_page):
            result+=self.get_page_html(i)
        #get forward and tail
        if self.curr_page != self.all_page:
            result+='<a href="'+self.get_page_url(self.curr_page+1)+'">'+'&gt;&gt;'+'</a> '
            result+='<a href="'+self.get_page_url(self.all_page)+'">'+'&gt;|'+'</a> '
        return result

class MainPage(webapp2.RequestHandler):
    
    def get(self):
        #get user
        user = users.get_current_user()
        userdb=[]
        if user:
            log_url = users.create_logout_url(self.request.uri)
            log_text = "Log out"
            #check if in database
            userdb_list = User.query(User.email == user.email()).fetch()
            if userdb_list:
                userdb=userdb_list[0]
            else:
                #add new entry
                userdb=User(email=user.email(),nickname=user.nickname())
                userdb.put()
        else:
            log_url = users.create_login_url(self.request.uri)
            log_text = "Login"
            
        #get posts
        page=Page()
        posts_list = Post.query().order(-Post.createdDate).fetch()
        all_page=(len(posts_list)-1)/10+1
        page.all_page=all_page
        try:
            page.set_curr_page(int(self.request.get("page")))
        except (TypeError, ValueError, AttributeError):
            page.set_curr_page(1)
        posts = posts_list[10*(page.curr_page-1):10*page.curr_page]
        tags=Tag.query().order(-Tag.posts_num).fetch()
        
        host=self.request.host_url
        template_values={"posts":posts,
                         "posts_no":len(posts),
                         "page":page,
                         "log_url":log_url,
                         "log_text":log_text,
                         "user":user,
                         "userdb":userdb,
                         "tags":tags,
                         "host":host}
        template = JINJA_ENVIRONMENT.get_template('template/index.html')
        self.response.write(template.render(template_values))
        
application = webapp2.WSGIApplication([('/',MainPage),
                                       ('/newpost',NewPost),
                                       ('/newblogpost',NewBlog),
                                       ('/newblog',NewBlogPage),
                                       (r'/blog/([^/]*)/post/([^/]*)',PostPage),
                                       (r'/tag/([^/]*)',TagPage),
                                       (r'/blog/([^/]*)',BlogPage),
                                       (r'/blog/([^/]*)/rss',RssPage),
                                       (r'/blog/([^/]*)/tag/([^/]*)',BlogTagPage),
                                       (r'/user/([^/]*)/pic',BlogPicPage),
                                       (r'/user/([^/]*)/pic/([0-9]*).png',PicPage),
                                       ('/uploadimage',UploadImage),
                                       ('/up',UpPost),
                                       ('/down',DownPost),
                                       ('/edit',EditPost),
                                       ('/editsubmit',EditSubmit),
                                       ('/warning',WarningPage)],
                                      debug = True)
