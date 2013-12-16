from google.appengine.ext import ndb

from Blog import Blog

class User(ndb.Model):
    '''
    User data
    @param username: the username 
    '''
    email=ndb.StringProperty(required=True)#unique
    nickname=ndb.StringProperty()
    subscribe=ndb.KeyProperty(repeated=True)
    blogs=ndb.StringProperty(repeated=True)
    images=ndb.BlobProperty(repeated=True)
    
    def get_image_url(self,img_no):
        return "/user/"+self.email+"/pic/"+str(img_no)+".png"
    
    def get_blogs(self):
        blogs = []
        for blog in self.blogs:
            blogdb = Blog.query(Blog.name==blog).fetch()[0]
            blogs.append(blogdb)
        return blogs
        