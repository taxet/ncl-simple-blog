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
    
    def get_blog_url(self):
        return "/blog/"+self.blogname
        