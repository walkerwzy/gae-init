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
        key = '%s_%s'%(memkey.cate_art_key,self.name)
        arts = memcache.get(key)
        if arts is None:
            arts = Article.query(Article.category==self.key).order(-Article.created).fetch(10)
            memcache.set(key,arts)
        return arts

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
        # todo: from alltags() get all tags, then order
        tags = memcache.get(memkey.tagcloud_key)
        if tags is None:
            tags = cls.query().order(-cls.entrycount).fetch(50)
            memcache.set(memkey.tagcloud_key,tags,3600)
        return tags

    @classmethod
    def alltags(cls):
        tags = memcache.get(memkey.tags_key)
        if tags is None:
            tags = cls.query().fetch()  # probably too much
            memcache.set(memkey.tags_key,tags,3600)
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
        posts = memcache.get(memkey.article_related_key)
        if posts is None:
            art_qry = Article.query(Article.key!=self.key)
            posts = []
            for tag in self.tags:
                tag_db = art_qry.filter(Article.tags==tag).fetch(10)
                posts+=tag_db
                if len(posts)>=10:
                    break
            posts = posts[:10]
            memcache.set(memkey.article_related_key, posts[:10])
        return posts
        
    @property
    def str_tags(self):
        return ','.join(self.tags) if isinstance(self.tags,list) else ''

    @property
    def next(self):
        if self.next_key:
            art = self.next_key.get()
            if art:
                return art
            else:
                return None
        else:
            art = Article.query().order(-Article.created).filter(Article.created<self.created).get()
            if art:
                self.next_key = art.key
                self.put()
                return art
            else:
                return None
    
    @property
    def prev(self):
        if self.prev_key:
            art = self.prev_key.get()
            if art:
                return art
            else:
                return None
        else:
            art = Article.query().order(Article.created).filter(Article.created>self.created).get()
            if art:
                self.prev_key = art.key
                self.put()
                return art
            else:
                return None

# class EntryCount(BaseModel):
#     counts=db.IntegerProperty(default=0)