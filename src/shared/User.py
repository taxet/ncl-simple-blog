from google.appengine.ext import ndb

class User(ndb.Model):
    '''
    User data
    @param username: the username 
    '''
    email=ndb.StringProperty(required=True)#unique
    nickname=ndb.StringProperty()
    posts=ndb.KeyProperty(repeated=True)

        