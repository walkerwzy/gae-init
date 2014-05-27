# coding: utf-8

from google.appengine.ext import ndb
from google.appengine.api import memcache

import config
import modelx
import util
import memkey

from model import Base, User
from flask import url_for

class Category(Base):
    name = ndb.StringProperty()
    slug = ndb.StringProperty()
    sort = ndb.IntegerProperty(default=0)
    entrycount = ndb.IntegerProperty(default=0)
    # post_keys = ndb.KeyProperty(kind='Article',repeated=True)
    
    def __unicode__(self):
        return self.name
    
    @property
    def posts(self):
        return Article.query(Article.category==self.key).fetch()

    @property
    def absolute_url(self):
        return url_for('cate', category=self.name)

    @classmethod
    def allcates(cls):
        cate_dbs = memcache.get(memkey.cate_key)
        if cate_dbs is None:
            cate_dbs = cls.query().order(cls.sort).fetch()
            memcache.set(memkey.cate_key,cate_dbs)
        return cate_dbs

    _PROPERTIES = Base._PROPERTIES.union({
            'name',
            'slug',
            'sort',
            'entrycount',
            'absolute_url'
        })

class Tag(Base):
    name = ndb.StringProperty(required=True)
    entrycount = ndb.IntegerProperty(default=0)
    
    def __unicode__(self):
        return self.name

    @property
    def posts(self):
        return Article.query(Article.category==self.key).fetch()

    @property
    def absolute_url(self):
        return url_for('tag', tag=self.name)

    @classmethod
    def tagcloud(cls):
        tags = memcache.get(memkey.tagcloud_key)
        if tags is None:
            tags = cls.query().order(-cls.entrycount).fetch(50)
            memcache.set(memkey.tagcloud_key,tags,3600)
        return tags

    _PROPERTIES = Base._PROPERTIES.union({
            'name',
            'entrycount',
            'absolute_url'
        })

class Ads(Base):
    name = ndb.StringProperty(required=True)
    value = ndb.TextProperty(default='')
    description = ndb.StringProperty(default='')
    
    def __unicode__(self):
        return self.name

    @classmethod
    def allads(cls):
        ads = memcache.get(memkey.ads_key)
        if ads is None:
            ads = cls.query().fetch()
            memcache.set(memkey.ads_key,ads)
        return ads

    _PROPERTIES = Base._PROPERTIES.union({
            'name',
            'value',
            'description'
        })

class Links(Base):
    name = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True,default='http://')
    sort = ndb.IntegerProperty(default=0)
    
    def __unicode__(self):
        return self.name

    @classmethod
    def alllinks(cls):
        links = memcache.get(memkey.links_key)
        if links is None:
            links = cls.query().fetch()
            memcache.set(memkey.links_key,links)
        return links

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

    @property
    def absolute_url(self):
        title = self.title
        if self.slug:
            title=self.slug
        return url_for('article', id=self.key.id(), title=util.slugify(title))

    _PROPERTIES = Base._PROPERTIES.union({
            'title',
            'category',
            'tags',
            'absolute_url'
        })
        
    @property
    def relateposts(self):
        art_qry = Article.query(Article.key!=self.key)
        posts = []
        for tag in self.tags:
            tag_db = art_qry.filter(Article.tags==tag).fetch(10)
            posts+=tag_db
            if len(posts)==10:
                break
        return posts
        
    @property
    def str_tags(self):
        return ','.join(self.tags) if isinstance(self.tags,list) else ''

    @property
    def next(self):
        if self.next_key:
            art = Article.getbyid(self.next_key.id()) # self.next_key.get()
            if art:
                return art
            else:
                return None
        else:
            self_mem_key = '%s_%s'%(memkey.article_key,self.key.id())
            art = Article.query().order(-Article.created).filter(Article.created<self.created).get()
            if art:
                self.next_key = art.key
                self.put()
                memcache.delete(self_mem_key)
                return art
            else:
                return None
    
    @property
    def prev(self):
        if self.prev_key:
            art = Article.getbyid(self.prev_key.id()) # self.prev_key.get()
            if art:
                return art
            else:
                return None
        else:
            self_mem_key = '%s_%s'%(memkey.article_key,self.key.id())
            art = Article.query().order(Article.created).filter(Article.created>self.created).get()
            if art:
                self.prev_key = art.key
                self.put()
                memcache.delete(self_mem_key)
                return art
            else:
                return None

    @classmethod
    def getbyid(cls,id):
        mem_art_key = '%s_%s'%(memkey.article_key,id)
        art = memcache.get(mem_art_key)
        if art is None:
            art = cls.get_by_id(id)
            memcache.set(mem_art_key,art,3600)
        return art

# class EntryCount(BaseModel):
#     counts=db.IntegerProperty(default=0)