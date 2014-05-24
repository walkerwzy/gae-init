# coding: utf-8

from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
import flask

import auth
import config
import model
import modelcms as cms
import util

import logging

from main import app
from markdown import markdown

from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed

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
	post.content = markdown(post.content)
	return flask.render_template(
		theme_file('post.html'),
		cates=cate_list(),
		obj=post)



###########################################
# posts by page
###########################################
@app.route('/')
def index():
	article_qry=cms.Article.query()
	article_db, next_page, prev_page = util.retrieve_dbs_pager(
		article_qry,
		prev=util.param('prev'),
		order='-created',
		limit=PAGESIZE,
		cursor=util.param('curs'))
	if next_page:
		next_page = flask.url_for('index',curs=next_page)
	if prev_page:
		prev_page = flask.url_for('index',curs=prev_page,prev=1)
	return flask.render_template(
		theme_file('index.html'),
		cates=cate_list(),
		data=article_db,
		prev_page=prev_page,
		next_page=next_page)

###########################################
# related posts
###########################################

###########################################
# same category posts
###########################################
@app.route('/category/<category>/',endpoint="cate")
def category(category):
	cate_db=cms.Category.query(cms.Category.name == category).fetch()
	if cate_db:
		cate = cate_db[0]
		article_qry = cms.Article.query()
		article_db, next_page, prev_page = util.retrieve_dbs_pager(
			article_qry,
			prev=util.param('prev'),
			order='-created',
			limit=PAGESIZE,
			cursor=util.param('curs'),
			category=cate.key)
		if next_page:
			next_page = flask.url_for('cate',category=category,curs=next_page)
		if prev_page:
			prev_page = flask.url_for('cate',category=category,curs=prev_page,prev=1)
	else:
		next_page, prev_page, article_db, obj = None, None, None, None
	return flask.render_template(
		theme_file('index.html'),
		obj=cate,
		cates=cate_list(),
		data=article_db,
		prev_page=prev_page,
		next_page=next_page)


###########################################
# posts of tags
###########################################
@app.route('/tag/<tag>/',endpoint="tag")
def tag(tag):
	tag_db=cms.Tag.query(cms.Tag.name == tag).get()
	if tag_db:
		article_qry = cms.Article.query()
		article_db, next_page, prev_page = util.retrieve_dbs_pager(
			article_qry,
			prev=util.param('prev'),
			order='-created',
			limit=PAGESIZE,
			cursor=util.param('curs'),
			tags=tag_db.name)
		if next_page:
			next_page = flask.url_for('tag',tag=tag,curs=next_page)
		if prev_page:
			prev_page = flask.url_for('tag',tag=tag,curs=prev_page,prev=1)
	else:
		next_page, prev_page, article_db, obj = None, None, [], None
	return flask.render_template(
		theme_file('index.html'),
		obj=tag_db,
		cates=cate_list(),
		data=article_db,
		prev_page=prev_page,
		next_page=next_page)

@app.route('/recent.atom')
def rss():
	feed = AtomFeed('Dig-Music.com',
		feed_url=flask.request.url,
		url=flask.request.url_root,
		subtitle="Recent Articles")
	art_dbs = cms.Article.query().order(-cms.Article.modified).fetch(20)
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
	return cms.Category.query().order(cms.Category.sort)

def theme_file(pagename):
	return '%s/%s'%('theme/default',pagename)

def full_url(url):
	return urljoin(flask.request.url_root, url)