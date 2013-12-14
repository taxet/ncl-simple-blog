from google.appengine.ext import ndb

class Post(ndb.Model):
    '''
    A class that record all posts from database.
    '''
    title=ndb.StringProperty()
    createdDate=ndb.DateTimeProperty(auto_now_add=True)
    lastEditDate=ndb.DateTimeProperty()
    tags=ndb.StringProperty(repeated=True)
    content=ndb.StringProperty(indexed=False)
    authors=ndb.StringProperty(repeated=True)
    views=ndb.IntegerProperty()
    #comment=ndb.
    thumbUp=ndb.IntegerProperty()
    thumbDown=ndb.IntegerProperty()
    
    def cap500(self):
        result = self.content[0:499]
        result += "..."
        return result