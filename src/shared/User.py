from google.appengine.ext import ndb

class User(ndb.Model):
    '''
    User data
    @param username: the username 
    '''
    email=ndb.StringProperty(required=True)#unique
    nickname=ndb.StringProperty()
    posts=ndb.StringProperty(repeated=True)
    subscribe=ndb.KeyProperty(repeated=True)
    blogname=ndb.StringProperty()
    images=ndb.BlobProperty(repeated=True)
    
    def get_blog_url(self):
        return "/blog/"+self.blogname
    
    def get_image_url(self,img_no):
        return "/blog/"+self.blogname+"/pic/"+str(img_no)+".png"