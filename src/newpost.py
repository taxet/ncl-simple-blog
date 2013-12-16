import urllib
from datetime import datetime
from google.appengine.api import users

import webapp2

from shared.Post import Post
from shared.Tag import Tag
from shared.User import User
from shared.Blog import Blog
import jinja2
import os

class NewPost(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        author = self.request.get('post_author')
        if user and user.email()==author:
            #put post
            title = self.request.get('post_title')
            author= user.email()
            content = self.request.get('post_content')
            tags=self.request.get('post_tags').split(" ")
            blogname = self.request.get('blog_name')    
            post = Post()
            post.title = title
            post.authors.append(author)
            post.content = content
            post.tags = list(set(tags))
            post.views = 0
            post.thumbUp = 0
            post.thumbDown = 0
            post.blog=blogname
            post_key=post.put()
            post.post_id=post_key.urlsafe()
            post.put()
            #put tags
            for tag in post.tags:
                if Tag.query(Tag.name==tag).fetch():
                    tag_entity=Tag.query(Tag.name==tag).fetch()[0]
                    tag_entity.append(post.post_id)
                    tag_entity.put()
                else:
                    #put new tag
                    new_tag=Tag()
                    new_tag.name = tag
                    new_tag.append(post.post_id)
                    new_tag.put()
            #put blog
            blogdb = Blog.query(Blog.name == blogname).fetch()[0]
            blogdb.posts.append(post.post_id)
            blogdb.put()
            self.redirect('/')
        else:
            para={'title':"WARNING","warning":"0"}
            self.redirect('/warning?'+urllib.urlencode(para))
            return

class NewBlog(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        author = self.request.get('post_author')
        blogname=self.request.get("blog_name")
        if user and user.email()==author:
            userdb = User.query(User.email==user.email()).fetch()[0]
            #already exist
            if Blog.query(Blog.name==blogname).fetch():
                para={"warning":"0"}
                self.redirect('/newblog?'+urllib.urlencode(para))
                return
            #illegal name
            elif '/' in blogname:
                para={"warning":"1"}
                self.redirect('/newblog?'+urllib.urlencode(para))
                return
            else:
                blog=Blog(name=blogname)
                blog.put()
                userdb.blogs.append(blogname)
                userdb.put()
                para={'title':"Congratulations","warning":"2"}
                self.redirect('/warning?'+urllib.urlencode(para))
                
        else:
            para={'title':"WARNING","warning":"0"}
            self.redirect('/warning?'+urllib.urlencode(para))
            return
            

class EditPost(webapp2.RequestHandler):
    def post(self):
        post_id=self.request.get("post_id")
        user=users.get_current_user()
        if user:
            #get target post
            if Post.query(Post.post_id==post_id).fetch():
                post = Post.query(Post.post_id==post_id).fetch()[0]
                if user.email() in post.authors:
                    JINJA_ENVIRONMENT = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                                           extensions=['jinja2.ext.autoescape'],
                                                           autoescape=True)
                    template_values={"post":post,
                                     "user":user}
                    template = JINJA_ENVIRONMENT.get_template('edit.html')
                    self.response.write(template.render(template_values))
                else:
                    para={'title':"WARNING","warning":"5"}
                    self.redirect('/warning?'+urllib.urlencode(para))
                    return
            else:
                para={'title':"WARNING","warning":"3"}
                self.redirect('/warning?'+urllib.urlencode(para))
                return
        else:
            para={'title':"WARNING","warning":"0"}
            self.redirect('/warning?'+urllib.urlencode(para))
            return
        
class EditSubmit(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            post_id = self.request.get("post_id")
            post = Post.query(Post.post_id == post_id).fetch()[0]
            if user.email() in post.authors:
                title=self.request.get("post_title")
                content=self.request.get("post_content")
                old_tags=post.tags
                new_tags=list(set(self.request.get('post_tags').split(" ")))
                post.title=title
                post.content=content
                post.tags=new_tags
                post.lastEditDate=datetime.now()
                post.put()
                #edit tags
                for tag in old_tags:
                    tag_entity=Tag.query(Tag.name==tag).fetch()[0]
                    tag_entity.remove(post.post_id)
                    tag_entity.put()
                for tag in new_tags:
                    if Tag.query(Tag.name==tag).fetch():
                        tag_entity=Tag.query(Tag.name==tag).fetch()[0]
                        tag_entity.append(post.post_id)
                        tag_entity.put()
                    else:
                        tag_entity=Tag()
                        tag_entity.name=tag
                        tag_entity.append(post.post_id)
                        tag_entity.put()
                for tag in old_tags:
                    tag_entity=Tag.query(Tag.name==tag).fetch()[0]
                    if tag_entity.posts_num==0:
                        tag_entity.key.delete()
                self.redirect(post.get_url())
            else:
                para={'title':"WARNING","warning":"5"}
                self.redirect('/warning?'+urllib.urlencode(para))
                return
        else:
            para={'title':"WARNING","warning":"0"}
            self.redirect('/warning?'+urllib.urlencode(para))
            return
            
            
class UploadImage(webapp2.RequestHandler):
    def post(self):
        user=users.get_current_user()
        if user:
            author=self.request.get('user_email')
            if author == user.email():
                img = self.request.get('img')
                userdb = User.query(User.email==user.email()).fetch()[0]
                userdb.images.append(img)
                userdb.put()
                para={'title':"Message","warning":"6"}
                self.redirect('/warning?'+urllib.urlencode(para))
                return    
            else:
                para={'title':"WARNING","warning":"5"}
                self.redirect('/warning?'+urllib.urlencode(para))
                return                
        else:
            para={'title':"WARNING","warning":"0"}
            self.redirect('/warning?'+urllib.urlencode(para))
            return


