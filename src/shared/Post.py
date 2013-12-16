import urllib
import re

from google.appengine.ext import ndb

from Tag import Tag
from User import User

class Post(ndb.Model):
    '''
    A class that record all posts from database.
    '''
    post_id=ndb.StringProperty()#key.safeurl
    title=ndb.StringProperty()
    createdDate=ndb.DateTimeProperty(auto_now_add=True)
    lastEditDate=ndb.DateTimeProperty()
    tags=ndb.StringProperty(repeated=True)
    content=ndb.StringProperty(indexed=False)
    authors=ndb.StringProperty(repeated=True)
    blog=ndb.StringProperty()
    views=ndb.IntegerProperty()
    #comment=ndb.
    thumbUp=ndb.IntegerProperty()
    thumbDown=ndb.IntegerProperty()
    
    def cap500(self):
        result = self.content[0:499]
        if len(self.content)>500:
            result += "..."
        return result
    
    def get_url(self):
        href="/blog/"+self.blog+"/post/"
        urlsafe=self.key.urlsafe()
        href += urlsafe
        return href
    
    def parse_content(self):
        result = re.sub(r'(http[s]?://[^,\s\n]*)', '<a href="\\1">\\1</a>', self.content)
        result = re.sub(r'<a href="(http[s]?://[^,\s\n]*[(.jpg)(.png)(.gif)])">.*</a>', '<img src="\\1">', result)
        result = result.replace('\n', '<br />')
        return result
    
    def get_up_url(self):
        urlsafe=self.key.urlsafe()
        para={'id':urlsafe}
        return "/up?"+urllib.urlencode(para)
    def get_down_url(self):
        urlsafe=self.key.urlsafe()
        para={'id':urlsafe}
        return "/down?"+urllib.urlencode(para)
    
    def get_tags(self):
        all_tags = []
        for tag in self.tags:
            tag_entity=Tag.query(Tag.name==tag).fetch()[0]
            all_tags.append(tag_entity)
        return all_tags
    
    def get_authors(self):
        all_authors=[]
        for author in self.authors:
            user_entity=User.query(User.email==author).fetch()[0]
            all_authors.append(user_entity)
        return all_authors
    
    def get_tags_str(self):
        result=""
        for tag in self.tags:
            result=result+tag+" "
        return result