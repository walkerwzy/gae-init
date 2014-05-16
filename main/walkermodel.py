
#db test
from google.appengine.ext import ndb

class Temo(ndb.Model):
    f1=ndb.StringProperty()
    f2=ndb.StringProperty()
    f3=ndb.IntegerProperty(default=0)

    @property
    def ids(self):
        return self.key.id()
    # @ff.setter
    # def ff(self, value):
    #     self._ff = value

    @property
    def fromkey(self):
    	k=4644337115725824
    	return Temo.get_by_id(k)
        # return self._fromkey
    
    @property
    def keystr(self):
        return self.key.urlsafe()

    @property
    def strtokey(self):
    	k=ndb.Key(urlsafe='agxkZXZ-Z2FlLWluaXRyEQsSBFRlbW8YgICAgICAoAgM')
        return k

    def __unicode__(self):
    	return 'f1=%s, f2=%s, f3=%3.2f' % (self.f1, self.f2, self.f3)

# class Category(Base):
#     name = ndb.StringProperty()
#     slug = ndb.StringProperty()
#     sort = ndb.IntegerProperty(default=0)
#     entrycount = ndb.IntegerProperty(default=0)
#     post_keys = ndb.KeyProperty(repeated=True)
    
#     def __unicode__(self):
#         return self.name
    
#     @property
#     def posts(self):
        # men_key = "category_posts_%d"%(self.key().id())
        # men_data = memcache.get(men_key)
        # if men_data is None:
        #     men_data = db.get(self.post_keys[:10])
        #     memcache.add(men_key, men_data, 3600)
        # return men_data
    
#     @permalink
#     def get_absolute_url(self):
#         if self.slug:
#             title = self.slug.replace(' ','_')
#         else:
#             title = self.name.strip()
#             title = title.replace(' ','_')
#             title = title.replace(',','_')
#             title = title.replace(u',','_')
#             title = title.replace("/","%2f")
#             title = title.replace("%","%25")        
#         return ('app1.views.category_article', (), {'keyid': self.key().id(),'name':title})    

# signals.pre_delete.connect(cleanup_relations, sender=Category)

# class Tag(db.Model):#key_tag
#     tag = db.StringProperty(multiline=False)
#     entrycount = db.IntegerProperty(default=0)
#     post_keys = db.ListProperty(db.Key)
    
#     def __unicode__(self):
#         return self.tag
    
#     @property
#     def posts(self):
#         men_key = "tag_posts_%s"%(self.key().name())
#         men_data = memcache.get(men_key)
#         if men_data is None:
#             men_data = db.get(self.post_keys[:10])
#             memcache.add(men_key, men_data, 3600)
#         return men_data