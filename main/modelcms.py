# coding: utf-8

from google.appengine.ext import ndb

import config
import modelx
import util

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

    _PROPERTIES = Base._PROPERTIES.union({
            'name',
            'slug',
            'sort',
            'entrycount'
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
        return url_for('cate', tag=self.name)

    _PROPERTIES = Base._PROPERTIES.union({
            'name',
            'entrycount'
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
            art = self.next_key.get()
            if art:
                return art
            else:
                return None
        else:
            arts = Article.query().order(-Article.created).filter(Article.created>self.created).fetch(1)
            if arts:
                self.next_key = arts[0].key
                self.put()
                return arts[0]
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
            arts = Article.query().order(-Article.created).filter(Article.created<self.created).fetch(1)
            if arts:
                self.prev_key = arts[0].key
                self.put()
                return arts[0]
            else:
                return None    

# class EntryCount(BaseModel):
#     counts=db.IntegerProperty(default=0)