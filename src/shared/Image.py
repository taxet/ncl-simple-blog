from google.appengine.ext import ndb

class Image(ndb.Model):
    type=ndb.StringProperty()
    name=ndb.StringProperty()
    img=ndb.BlobProperty()
    
    def get_image_url(self):
        return "/pic/"+self.name+"."+self.type