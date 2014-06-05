# coding: utf-8

from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import memcache

import flask

import auth
import config
import model
import modelcms as cms
import util

import logging

from main import app
# from markdown import markdown

from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
from pager import Pager

import memkey


PAGESIZE = 10

###########################################
# post with id
###########################################
@app.route('/article/<int:id>/<title>',endpoint='article')
@app.route('/a/<int:id>',endpoint='plink')
def get_article_by_id(id,title=''):
	post = cms.Article.get_by_id(id)
	if not post:
		flask.abort(404)
	# post.content = markdown(post.content)
	return flask.render_template(
		theme_file('post.html'),
		cates=cate_list(),
		obj=post)



###########################################
# posts by page
###########################################
@app.route('/')
def index():
	article_qry=cms.Article.query().order(-cms.Article.created)
	pager = Pager(query=article_qry, page=util.param('page') or 1)
	article_dbs, _, _ = pager.paginate(page_size=PAGESIZE)
	return flask.render_template(
		theme_file('index.html'),
		cates=cate_list(),
		data=article_dbs,
		pager=pager)
	# article_db, next_page, prev_page = util.retrieve_dbs_pager(
	# 	article_qry,
	# 	prev=util.param('prev'),
	# 	order='-created',
	# 	limit=PAGESIZE,
	# 	cursor=util.param('curs'))
	# if next_page:
	# 	next_page = flask.url_for('index',curs=next_page)
	# if prev_page:
	# 	prev_page = flask.url_for('index',curs=prev_page,prev=1)
	# return flask.render_template(
	# 	theme_file('index.html'),
	# 	cates=cate_list(),
	# 	data=article_db,
	# 	prev_page=prev_page,
	# 	next_page=next_page)


###########################################
# same category posts
###########################################
@app.route('/category/<category>/',endpoint="cate")
def category(category):
	cate_dbs = [c for c in cms.Category.allcates() if c.name.lower() == category.lower()]
	if cate_dbs:
		cate_db = cate_dbs[0]
		article_qry = cms.Article.query(cms.Article.category==cate_db.key).order(-cms.Article.created)
		pager = Pager(query=article_qry, page=util.param('page') or 1)
		article_dbs, _, _ = pager.paginate(page_size=PAGESIZE)
	else:
		pager, article_dbs, cate_db = None, None, None
	return flask.render_template(
		theme_file('index.html'),
		obj=cate_db,
		cates=cate_list(),
		data=article_dbs,
		pager=pager)


###########################################
# posts of tags
###########################################
@app.route('/tag/<tag>/',endpoint="tag")
def tag(tag):
	tag_dbs = [t for t in cms.Tag.alltags() if t.name.lower() == tag.lower()]
	if tag_dbs:
		tag_db = tag_dbs[0]
		article_qry = cms.Article.query(cms.Article.tags==tag).order(-cms.Article.created)
		pager = Pager(query=article_qry, page=util.param('page') or 1)
		article_dbs, _, _ = pager.paginate(page_size=PAGESIZE)
	else:
		pager, article_db, tag_db = None, [], None
	return flask.render_template(
		theme_file('index.html'),
		obj=tag_db,
		cates=cate_list(),
		data=article_dbs,
		pager=pager)

@app.route('/recent.atom',endpoint='rss')
def rss():
	feed = AtomFeed('Dig-Music.com',
		feed_url=flask.request.url,
		url=flask.request.url_root,
		subtitle="Recent Articles")
	art_dbs = memcache.get(memkey.rss_key)
	if art_dbs is None:
		art_dbs = cms.Article.query().order(-cms.Article.modified).fetch(20)
		memcache.set(memkey.rss_key,art_dbs,3600)
	for art in art_dbs:
		feed.add(
				art.title,
				art.content,
				author=art.author.get().name,
				url=full_url(art.absolute_url),
				id=art.key.id(),
				updated=art.modified,
				published=art.created
			)
	return feed.get_response()

###########################################
# helper
###########################################
def cate_list():
	'''get category list'''
	return cms.Category.allcates()

def theme_file(pagename):
	return '%s/%s'%('theme/default',pagename)

def full_url(url):
	return urljoin(flask.request.url_root, url)