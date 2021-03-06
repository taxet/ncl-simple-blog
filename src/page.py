import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

from shared.Data import User
from shared.Data import Post
from shared.Data import Tag
from shared.Data import Blog

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


JINJA_ENVIRONMENT = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)

class TagPage(webapp2.RequestHandler):
    def get(self, tag_name):
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
            
        #get tag
        if Tag.query(Tag.name==tag_name).fetch():
            tag_entity=Tag.query(Tag.name==tag_name).fetch()[0]
            #get posts
            page=Page()
        
            posts_list = Post.query(Post.post_id.IN(tag_entity.posts)).order(-Post.createdDate).fetch()
            all_page=(len(posts_list)-1)/10+1
            page.all_page=all_page
            try:
                page.set_curr_page(int(self.request.get("page")))
            except (TypeError, ValueError, AttributeError):
                page.set_curr_page(1)
            if page>all_page:
                page=all_page
            posts = posts_list[10*(page.curr_page-1):10*page.curr_page]
        else:
            page=Page()
            page.all_page=1
            page.set_curr_page(1)
            posts=[]
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
        
class PostPage(webapp2.RequestHandler):
    def get(self,blogname, keystr):
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
        post_key=ndb.Key(urlsafe=keystr)
        post = post_key.get()
        if post:
            post.views+=1
            post.put()
            #wanted blog
            wanted_blog=[]
            if Blog.query(Blog.name==blogname).fetch():
                wanted_blog=Blog.query(Blog.name==blogname).fetch()[0]
                tags=[]
                all_tags=Tag.query().order(-Tag.posts_num).fetch()
                for tag in all_tags:
                    flag=False
                    for tag_post in tag.posts:
                        p=Post.query(Post.post_id==tag_post).fetch()[0]
                        if p.blog == wanted_blog.name:
                            flag=True
                    if flag:
                        tags.append(tag)
                if post.post_id in wanted_blog.posts:
                    host=self.request.host_url
                    template_values={"post":post,
                                     "log_url":log_url,
                                     "log_text":log_text,
                                     "user":user,
                                     "wanted_blog":wanted_blog,
                                     "tags":tags,
                                     "userdb":userdb,
                                     "host":host}
                    template = JINJA_ENVIRONMENT.get_template('template/post.html')
                    self.response.write(template.render(template_values))
                else:
                    para={'title':"WARNING","warning":"3"}
                    self.redirect('/warning?'+urllib.urlencode(para))
            else:
                para={'title':"WARNING","warning":"3"}
                self.redirect('/warning?'+urllib.urlencode(para))
        else:
            para={'title':"WARNING","warning":"3"}
            self.redirect('/warning?'+urllib.urlencode(para))
            
            
            
class UpPost(webapp2.RequestHandler):
    def get(self):
        #get posts
        try:
            keystr=self.request.get("id")
            post_key=ndb.Key(urlsafe=keystr)
            post=post_key.get()
            if(post):
                post.thumbUp+=1
                post.put()
                self.redirect(post.getUrl())
        except (TypeError, ValueError, AttributeError):
            self.redirect('/')
    
class DownPost(webapp2.RequestHandler):
    def get(self):
        #get posts
        try:
            keystr=self.request.get("id")
            post_key=ndb.Key(urlsafe=keystr)
            post=post_key.get()
            if(post):
                post.thumbDown+=1
                post.put()
                self.redirect(post.getUrl())
        except (TypeError, ValueError, AttributeError):
            self.redirect('/')


class BlogPage(webapp2.RequestHandler):
    def get(self, blogname):
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
        
        #get wanted user
        wanted_blog=[]
        if Blog.query(Blog.name==blogname).fetch():
            wanted_blog=Blog.query(Blog.name==blogname).fetch()[0]
            #get posts
            if wanted_blog.posts:
                page=Page()
                posts_list = Post.query(Post.post_id.IN(wanted_blog.posts)).order(-Post.createdDate).fetch()
                all_page=(len(posts_list)-1)/10+1
                page.all_page=all_page
                try:
                    page.set_curr_page(int(self.request.get("page")))
                except (TypeError, ValueError, AttributeError):
                    page.set_curr_page(1)
                if page>all_page:
                    page=all_page
                posts = posts_list[10*(page.curr_page-1):10*page.curr_page]
            else:
                page=Page()
                page.all_page=1
                page.set_curr_page(1)
                posts=[]
            tags=[]
            all_tags=Tag.query().order(-Tag.posts_num).fetch()
            for tag in all_tags:
                flag=False
                for tag_post in tag.posts:
                    p=Post.query(Post.post_id==tag_post).fetch()[0]
                    if p.blog == wanted_blog.name:
                        flag=True
                if flag:
                    tags.append(tag)
            
            host=self.request.host_url
            template_values={"posts":posts,
                             "posts_no":len(posts),
                             "page":page,
                             "log_url":log_url,
                             "log_text":log_text,
                             "user":user,
                             "userdb":userdb,
                             "wanted_blog":wanted_blog,
                             "tags":tags,
                             "host":host}
            template = JINJA_ENVIRONMENT.get_template('template/blog.html')
            self.response.write(template.render(template_values))
        else:
            para={'title':"WARNING","warning":"4"}
            self.redirect('/warning?'+urllib.urlencode(para))
        
class BlogTagPage(webapp2.RequestHandler):
    def get(self,blogname, tagname):
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
        
        #get wanted user
        wanted_blog=[]
        if Blog.query(Blog.name==blogname).fetch():
            wanted_blog=Blog.query(Blog.name==blogname).fetch()[0]
            if Tag.query(Tag.name==tagname).fetch():
                wanted_tag=Tag.query(Tag.name==tagname).fetch()[0]
                #get posts
                if wanted_blog.posts:
                    page=Page()
                    posts_list = Post.query(ndb.AND(Post.post_id.IN(wanted_blog.posts),Post.post_id.IN(wanted_tag.posts))).order(-Post.createdDate).fetch()
                    all_page=(len(posts_list)-1)/10+1
                    page.all_page=all_page
                    try:
                        page.set_curr_page(int(self.request.get("page")))
                    except (TypeError, ValueError, AttributeError):
                        page.set_curr_page(1)
                    if page>all_page:
                        page=all_page
                    posts = posts_list[10*(page.curr_page-1):10*page.curr_page]
                else:
                    page=Page()
                    page.all_page=1
                    page.set_curr_page(1)
                    posts=[]
            tags=[]
            all_tags=Tag.query().order(-Tag.posts_num).fetch()
            for tag in all_tags:
                flag=False
                for tag_post in tag.posts:
                    p=Post.query(Post.post_id==tag_post).fetch()[0]
                    if p.blog == wanted_blog.name:
                        flag=True
                if not flag:
                    tags.append(tag)
        
            host=self.request.host_url    
            template_values={"posts":posts,
                             "posts_no":len(posts),
                             "page":page,
                             "log_url":log_url,
                             "log_text":log_text,
                             "user":user,
                             "userdb":userdb,
                             "wanted_blog":wanted_blog,
                             "tags":tags,
                             "host":host}
            template = JINJA_ENVIRONMENT.get_template('template/blog.html')
            self.response.write(template.render(template_values))
        else:
            para={'title':"WARNING","warning":"4"}
            self.redirect('/warning?'+urllib.urlencode(para))
            
class BlogPicPage(webapp2.RequestHandler):
    def get(self,user_email):
        #get user
        user = users.get_current_user()
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
            
        #get images
        #wanted blog
        wanted_user=[]
        if User.query(User.email==user_email).fetch():
            wanted_user=User.query(User.email==user_email).fetch()[0]
            all_images = wanted_user.images
            page=Page()
            all_page=(len(all_images)-1)/10+1
            page.all_page=all_page
            try:
                page.set_curr_page(int(self.request.get("page")))
            except (TypeError, ValueError, AttributeError):
                page.set_curr_page(1)
            if page>all_page:
                page=all_page
            image_no = [10*(page.curr_page-1),10*page.curr_page]
            if len(all_images)<10*page.curr_page:
                image_no[1]=len(all_images)
            template_values={"image_no":image_no,
                             "log_url":log_url,
                             "log_text":log_text,
                             "user":user,
                             "wanted_user":wanted_user,
                             "page":page,
                             "userdb":userdb}
            template = JINJA_ENVIRONMENT.get_template('template/image.html')
            self.response.write(template.render(template_values))
        else:
            para={'title':"WARNING","warning":"4"}
            self.redirect('/warning?'+urllib.urlencode(para))


class WarningPage(webapp2.RequestHandler):
    def get(self):
        WARNING_LIST=["Please login or login as a correct user first.",
                      "You already have a blog.",
                      "You have a new blog now.",
                      "Target post does not exist. or belongs to another blog.",
                      "Target blog does not exist.",
                      "Permission denied.",
                      "Uploading image succeed.",
                      "Target image does not exist.",
                      ""]
        warning_title=self.request.get("title")
        warning=WARNING_LIST[int(self.request.get("warning"))]
        
        template_values={"warning_title":warning_title,
                         "warning":warning}
        template = JINJA_ENVIRONMENT.get_template('template/warning.html')
        self.response.write(template.render(template_values))


class NewBlogPage(webapp2.RequestHandler):
    def get(self):
        #get user
        user = users.get_current_user()
        if user:
            #check if in database
            userdb_list = User.query(User.email == user.email()).fetch()
            if userdb_list:
                userdb=userdb_list[0]
            else:
                #add new entry
                userdb=User(email=user.email(),nickname=user.nickname())
                userdb.put()
                
            WARNING_LIST=["This blog name has alredy been used.",
                          "Please do not contain \"/\" in blog name",
                          ""]
            try:
                warning=WARNING_LIST[int(self.request.get("warning"))]
            except (TypeError, ValueError, AttributeError):
                warning=""
            template_values={"warning":warning,
                             "userdb":userdb}
            template = JINJA_ENVIRONMENT.get_template('template/newblog.html')
            self.response.write(template.render(template_values))
        else:
            para={'title':"WARNING","warning":"0"}
            self.redirect('/warning?'+urllib.urlencode(para))
            return


class PicPage(webapp2.RequestHandler):
    def get(self,user_email,pic_no):
        wanted_user=[]
        if User.query(User.email==user_email).fetch():
            wanted_user=User.query(User.email==user_email).fetch()[0]
            img_no=int(pic_no)
            if img_no<len(wanted_user.images):
                self.response.headers['Content-Type'] = 'image/png'
                self.response.out.write(wanted_user.images[img_no])
            else:
                para={'title':"WARNING","warning":"7"}
                self.redirect('/warning?'+urllib.urlencode(para))
        else:
            para={'title':"WARNING","warning":"4"}
            self.redirect('/warning?'+urllib.urlencode(para))

class RssPage(webapp2.RequestHandler):
    def get(self,blogname):
        if Blog.query(Blog.name==blogname).fetch():
            blog=Blog.query(Blog.name==blogname).fetch()[0]
        
            template_values={"blog":blog}
            template = JINJA_ENVIRONMENT.get_template('template/template.rss')
            self.response.headers['Content-Type'] = 'application/rss+xml'
            self.response.write(template.render(template_values))