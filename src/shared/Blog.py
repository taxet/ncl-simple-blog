from google.appengine.ext import ndb

class Blog(ndb.Model):
    name=ndb.StringProperty(required=True)#unique
    posts=ndb.StringProperty(repeated=True)
    
    def get_blog_url(self):
        return "/blog/"+self.name