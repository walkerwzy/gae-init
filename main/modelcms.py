# coding: utf-8

from google.appengine.ext import ndb

import config
import modelx
import util

from model import Base, User

class Category(Base):
    name = ndb.StringProperty()
    slug = ndb.StringProperty()
    sort = ndb.IntegerProperty(default=0)
    entrycount = ndb.IntegerProperty(default=0)
    post_keys = ndb.KeyProperty(kind='Article',repeated=True)
    
    def __unicode__(self):
        return self.name
    
    # @property
    # def posts(self):
    #     men_key = "category_posts_%d"%(self.key().id())
    #     men_data = memcache.get(men_key)
    #     if men_data is None:
    #         men_data = db.get(self.post_keys[:10])
    #         memcache.add(men_key, men_data, 3600)
    #     return men_data

    _PROPERTIES = Base._PROPERTIES.union({
            'name',
            'slug',
            'sort',
            'entrycount',
            'post_keys'
        })

class Ads(Base):
    name = ndb.StringProperty(required=True)
    value = ndb.TextProperty(default='')
    description = ndb.StringProperty(default='')
    
    def __unicode__(self):
        return self.name

    _PROPERTIES = Base._PROPERTIES.union({
            'name',
            'value',
            'description'
        })

# class Tag(db.Model):#key_tag
#     tag = db.StringProperty(multiline=False)
#     entrycount = db.IntegerProperty(default=0)
#     post_keys = db.ListProperty(db.Key)
    
#     def __unicode__(self):
#         return self.tag
    
    # @property
    # def posts(self):
    #     men_key = "tag_posts_%s"%(self.key().name())
    #     men_data = memcache.get(men_key)
    #     if men_data is None:
    #         men_data = db.get(self.post_keys[:10])
    #         memcache.add(men_key, men_data, 3600)
    #     return men_data

class Links(Base):
    name = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True,default='http://')
    sort = ndb.IntegerProperty(default=0)
    
    def __unicode__(self):
        return self.name

    _PROPERTIES = Base._PROPERTIES.union({
            'name',
            'url',
            'sort'
        })

class Article(Base):
    author = ndb.KeyProperty(kind=User)
    # author_profile = ndb.ReferenceProperty(kind=Profile)
    category = ndb.KeyProperty(kind=Category)
    title = ndb.StringProperty(default='')
    slug = ndb.StringProperty(default='')
    abstract = ndb.TextProperty(default='')
    content = ndb.TextProperty(default='')
    tags = ndb.StringProperty(repeated=True)
    commentclosed = ndb.BooleanProperty(default=False)
    # commentcount = ndb.IntegerProperty(default=0)
    # comment_keys = ndb.ListProperty(db.Key)    
    prev_key = ndb.KeyProperty(kind='Article')
    next_key = ndb.KeyProperty(kind='Article')    
    # pub_time = ndb.DateTimeProperty()
    
    def __unicode__(self):
        return self.title
        
#     @property
#     def relateposts(self):
#         men_key = "article_relateposts_%d"%(self.key().id())
#         men_data = memcache.get(men_key)
#         #men_data = None
#         if men_data is None:
#             tag_key_list = []
#             for tag in self.tags:
#                 tag_obj = Tag.get_by_key_name(u"key_%s"%tag)
#                 tag_key_list += tag_obj.post_keys
#             tag_key_list = list(set(tag_key_list))
#             try:tag_key_list.remove(self.key())
#             except:pass
#             men_data = db.get(tag_key_list[:10])
#             try:men_data.remove(None)
#             except:pass
#             memcache.add(men_key, men_data, 3600)
#         return men_data
        
#     @property
#     def strtags(self):
#         return ','.join(self.tags)
        
#     @permalink
#     def get_absolute_url(self):
#         if self.slug:
#             title = self.slug.replace(' ','_')
#         else:
#             title = self.title.strip()
#             title = title.replace(' ','_')
#             title = title.replace(',','_')
#             title = title.replace(u'，','_')
#             title = title.replace("/","%2f")
#             title = title.replace("%","%25")        
#         return ('app1.views.show_article', (), {'keyid': self.key().id(),'title':title})
    
#     @permalink
#     def short_url(self):
#         return ('app1.views.show_article_short', (), {'keyid': self.key().id()})
    
#     @property
#     def next(self):
#         if self.next_key:
#             try:
#                 art = Entry.get(self.next_key)
#             except Exception:
#                 old_key = db.Key(self.next_key)
#                 new_key = db.Key.from_path(old_key.kind(), old_key.id())
#                 self.next_key = str(new_key)
#                 self.put()
#                 art = Entry.get(self.next_key)
#             if art:
#                 return art
#             else:
#                 self.next_key = None
#                 self.put()
#                 memcache.delete("article_post_%d"%self.key().id())
#                 return None
#         else:
#             art = Entry.all().order('pub_time').filter('pub_time >',self.pub_time).get()
#             if art:
#                 self.next_key = str(art.key())
#                 self.put()
#                 memcache.delete("article_post_%d"%self.key().id())
#                 return art
#             else:
#                 return None
    
#     @property
#     def prev(self):
#         if self.prev_key:
#             try:
#                 art = Entry.get(self.prev_key)
#             except Exception:
#                 old_key = db.Key(self.prev_key)
#                 new_key = db.Key.from_path(old_key.kind(), old_key.id())
#                 self.prev_key = str(new_key)
#                 self.put()
#                 art = Entry.get(self.prev_key)
#             if art:
#                 return art
#             else:
#                 self.prev_key = None
#                 self.put()
#                 memcache.delete("article_post_%d"%self.key().id())
#                 return None
#         else:
#             art = Entry.all().order('-pub_time').filter('pub_time <',self.pub_time).get()
#             if art:
#                 self.prev_key = str(art.key())
#                 self.put()
#                 memcache.delete("article_post_%d"%self.key().id())
#                 return art
#             else:
#                 return None    

# class EntryCount(BaseModel):
#     counts=db.IntegerProperty(default=0)