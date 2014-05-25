# coding: utf-8

from flask.ext import wtf
from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from markdown import markdown
import flask

import auth
import config
import model
import modelcms as cms
import util

from main import app
import os
from flask import Response as response
import logging
from xml.dom.minidom import parse
from datetime import datetime
from collections import Counter

# @app.route('/im')
# @auth.admin_required
# def im():
# 	# import all data
# 	dir = os.path.dirname(os.path.abspath(__file__))
# 	arts = []
# 	for i in range(1,6):
# 		filename = 'importer/0%d.xml'%i
# 		filename = os.path.join(dir,filename)
# 		dom = parse(filename)
# 		for item in dom.getElementsByTagName('item'):
# 			c = getNodeValue(item,'full')
# 			arts.append(cms.Article(
# 				author=auth.current_user_key(),
# 				category=getCategory(getNodeValue(item,'category')),
# 				title=getNodeValue(item,'title'),
# 				abstract=util.remove_html_markup(c)[:200],
# 				content=c,
# 				tags=getNodeValue(item,'tags').split(','),
# 				created=datetime.strptime(getNodeValue(item,'pubDate'),'%a, %d %b %Y %H:%M:%S GMT')
# 				))
# 	ndb.put_multi(arts)
# 	return response('done')
	
# 	# recoculate tag and cate's entrycount
# 	query = cms.Article.query().fetch(projection=['category','tags'])
# 	cates = []
# 	tags = []
# 	for item in query:
# 		cates.append(item.category)
# 		tags+=item.tags
# 	c1 = Counter(cates)
# 	c2 = Counter(tags)
# 	# logging.warning(c1)
# 	# logging.warning(c2)
# 	cs = []
# 	ts = []
# 	for k,v in c1.items():
# 		category = k.get()
# 		category.entrycount = v
# 		cs.append(category)
# 	for k,v in c2.items():
# 		tag = cms.Tag(name = k, entrycount = v)
# 		ts.append(tag)
# 	ndb.put_multi(cs)
# 	ndb.put_multi(ts)
# 	return response('done')

# def getNodeValue(node,name):
# 	node = node.getElementsByTagName(name)[0]
# 	if not node:
# 		return ""
# 	logging.warning('%s,%s'%(name,node.firstChild))
# 	try:
# 		return node.firstChild.nodeValue
# 	except:
# 		return ''

def getCategory(name):
	if not name:
		return None
	c = cms.Category.query(cms.Category.name==name).get()
	return c.key if c else None