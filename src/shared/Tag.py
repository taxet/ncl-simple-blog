from google.appengine.ext import ndb

class Tag(ndb.Model):
    name=ndb.StringProperty(required=True)#unique
    posts=ndb.StringProperty(repeated=True)
    posts_num=ndb.IntegerProperty()
    
    def get_url(self):
        return "/tag/"+self.name
    
    def append(self, post_id):
        if post_id in self.posts:
            pass
        else:
            self.posts.append(post_id)
            self.posts_num=len(self.posts)
        
    def remove(self,post_id):
        if post_id in self.posts:
            self.posts.remove(post_id)
            self.posts_num=len(self.posts)