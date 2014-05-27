# coding: utf-8

from flask.ext import wtf
from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import memcache
from markdown import markdown
import flask

import auth
import config
import model
import modelcms as cms
import util

from main import app

import memkey

PAGESIZE = 15
ADS_POSITION = [
  'sidebar_ads',
  'index_left_top',
  'articlelist_top',
  'article_top',
  'articlelist_top',
  'articledetail_left_top',
  'articledetail_right_top']

###########################################
# site configuration
###########################################
@app.route('/flushmemcache',endpoint='flush')
@auth.admin_required
def flush_memcache():
  memcache.flush_all()
  return flask.redirect(flask.url_for('index'))


###########################################
# site configuration
###########################################

class ConfigUpdateForm(wtf.Form):
  analytics_id = wtf.StringField('Tracking ID', filters=[util.strip_filter])
  announcement_html = wtf.TextAreaField('Announcement HTML', filters=[util.strip_filter])
  announcement_type = wtf.SelectField('Announcement Type', choices=[(t, t.title()) for t in model.Config.announcement_type._choices])
  brand_name = wtf.StringField('Brand Name', [wtf.validators.required()], filters=[util.strip_filter])
  facebook_app_id = wtf.StringField('Facebook App ID', filters=[util.strip_filter])
  facebook_app_secret = wtf.StringField('Facebook App Secret', filters=[util.strip_filter])
  feedback_email = wtf.StringField('Feedback Email', [wtf.validators.optional(), wtf.validators.email()], filters=[util.email_filter])
  flask_secret_key = wtf.StringField('Secret Key', [wtf.validators.optional()], filters=[util.strip_filter])
  notify_on_new_user = wtf.BooleanField('Send an email notification when a user signs up')
  twitter_consumer_key = wtf.StringField('Twitter Consumer Key', filters=[util.strip_filter])
  twitter_consumer_secret = wtf.StringField('Twitter Consumer Secret', filters=[util.strip_filter])
  description = wtf.TextAreaField('Description',filters=[util.strip_filter])
  sub_name = wtf.StringField('Site subname',filters=[util.strip_filter])
  keywords = wtf.StringField('Keywords',filters=[util.strip_filter])
  head_metas = wtf.TextAreaField('Head metas',filters=[util.strip_filter],default="http://")
  google_cse_cs = wtf.StringField('Google cse cs')
  domain = wtf.StringField('Doman',filters=[util.strip_filter])

@app.route('/_s/admin/config/', endpoint='admin_config_update_service')
@app.route('/admin/config/', methods=['GET', 'POST'])
@auth.admin_required
def admin_config_update():
  config_db = model.Config.get_master_db()
  form = ConfigUpdateForm(obj=config_db)
  if form.validate_on_submit():
    form.populate_obj(config_db)
    if not config_db.flask_secret_key:
      config_db.flask_secret_key = util.uuid()
    config_db.put()
    reload(config)
    app.config.update(CONFIG_DB=config_db)
    return flask.redirect(flask.url_for('admin_config_update'))

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(config_db)

  instances_url = None
  if config.PRODUCTION:
    instances_url = '%s?app_id=%s&version_id=%s' % (
        'https://appengine.google.com/instances',
        app_identity.get_application_id(),
        config.CURRENT_VERSION_ID,
      )

  return flask.render_template(
      'admin/config_update.html',
      title='Admin Config',
      html_class='admin-config',
      form=form,
      config_db=config_db,
      instances_url=instances_url,
      has_json=True,
    )

###########################################
# article category
###########################################

class CategoryForm(wtf.Form):
  name = wtf.StringField('Category name',validators=[wtf.validators.required()], filters=[util.strip_filter])
  slug = wtf.StringField('Slug',filters=[util.strip_filter])
  sort = wtf.IntegerField('Sort',default=0)

@app.route('/admin',endpoint="admin")
@auth.admin_required
def site():
  return flask.render_template('admin/site.html')

@app.route('/_s/admin/category',endpoint='admin_site_cate')
@app.route('/admin/category', methods=['GET','POST'])
@app.route('/_s/admin/category/<int:cateid>',endpoint='admin_site_cate')
@app.route('/admin/category/<int:cateid>', methods=['GET','POST'])
@app.route('/admin/category/<act>_<int:cateid>')
@auth.admin_required
def category(cateid=0,act=''):
  if act=='delete' and cateid:
    #delete
    k=ndb.Key(cms.Category,cateid)
    k.delete()
    flask.flash('delete category success', category='success')
    memcache.delete(memkey.cate_key)
    return flask.redirect(flask.url_for('category'))
  query=cms.Category.query()
  cate_dbs=cms.Category.allcates()
  if flask.request.path.startswith('/_s/'):
    # if cateid:
    #   return util.jsonify_model_db(cms.Category.get_by_id(cateid))
    # else:
    return util.jsonify_model_dbs(cate_dbs)
  btn = 'Create'
  form = CategoryForm()
  if cateid:
    obj=cms.Category.get_by_id(cateid)
    if not obj:
      flask.flash('invalid obj id', category='danger')
      return flask.render_template('admin/category.html',has_json=True,form=form,data=cate_dbs,btn=btn)
    else:
      btn = 'Save'
      form=CategoryForm(obj=obj)
  if form.validate_on_submit():
    name=form.name.data.capitalize()
    if cateid:
      # update
      # check existence
      if obj.name.capitalize() != name:
        if query.filter(cms.Category.name==name,
          cms.Category.key!=ndb.Key(cms.Category,cateid)).get():
          flask.flash('name exist',category='danger')
          return flask.render_template('admin/category.html',has_json=True,form=form,data=query,btn=btn)
      form.name.data=name
      form.populate_obj(obj)
      obj.put()
      flask.flash('update success',category='success')
    else:
      # create
      # check existence
      if query.filter(cms.Category.name==name).get():
        flask.flash('name exist',category="danger")
        return flask.render_template('admin/category.html',form=form,data=query,btn=btn)
      cate = cms.Category(
        name=name,
        slug=form.slug.data,
        sort=form.sort.data)
      cate.put()
      flask.flash('category add success',category='success')
    memcache.delete(memkey.cate_key)
    return flask.redirect(flask.url_for('category'))
  #get
  else:
    return flask.render_template('admin/category.html',has_json=True,form=form,data=query,btn=btn)


###########################################
# Ads
###########################################

class AdsForm(wtf.Form):
  name = wtf.StringField('Name',validators=[wtf.validators.required()], filters=[util.strip_filter])
  value = wtf.TextAreaField('Value',filters=[util.strip_filter])
  description = wtf.TextAreaField('Description',filters=[util.strip_filter])


@app.route('/_s/admin/ads',endpoint='admin_site_ads')
@app.route('/admin/ads', methods=['GET','POST'])
# @app.route('/_s/admin/ads/<int:id>',endpoint='admin_site_ads')
@app.route('/admin/ads/<int:id>', methods=['GET','POST'])
@app.route('/admin/ads/<act>_<int:id>')
@auth.admin_required
def ads(id=0,act=''):
  if act=='delete' and id:
    #delete
    k=ndb.Key(cms.Ads,id)
    k.delete()
    flask.flash('delete advertisement success', category='success')
    memcache.delete(memkey.ads_key)
    return flask.redirect(flask.url_for('ads'))
  query=cms.Ads.query()
  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_dbs(query.fetch())
  btn = 'Create'
  form = AdsForm()
  if id:
    obj=cms.Ads.get_by_id(id)
    if not obj:
      flask.flash('invalid obj id', category='danger')
      return flask.render_template('admin/ads.html',has_json=True,form=form,data=query,btn=btn)
    else:
      btn = 'Save'
      form=AdsForm(obj=obj)
  elif flask.request.method=='GET':
    # init some ad itmes
    ads_for_add = []
    for ad in ADS_POSITION:
      if not query.filter(cms.Ads.name == ad).get():
        ads_for_add.append(cms.Ads(name=ad))
    if ads_for_add:
      ndb.put_multi(ads_for_add)
  if form.validate_on_submit():
    name=form.name.data.lower()
    if id:
      # update
      # check existence
      if obj.name.lower() != name:
        if query.filter(cms.Ads.name==name,
          cms.Ads.key!=ndb.Key(cms.Ads,id)).get():
          flask.flash('name exist',category='danger')
          return flask.render_template('admin/ads.html',has_json=True,form=form,data=query,btn=btn)
      form.name.data=name
      form.populate_obj(obj)
      obj.put()
      flask.flash('update success',category='success')
    else:
      # create
      # check existence
      if query.filter(cms.Ads.name==name).get():
        flask.flash('name exist',category="danger")
        return flask.render_template('admin/ads.html',has_json=True,form=form,data=query,btn=btn)
      item = cms.Ads(
        name=name,
        value=form.value.data,
        description=form.description.data)
      item.put()
      flask.flash('ads add success',category='success')
    memcache.delete(memkey.ads_key)
    return flask.redirect(flask.url_for('ads'))
  #get
  else:
    return flask.render_template('admin/ads.html',has_json=True,form=form,data=query,btn=btn)


###########################################
# Links
###########################################

class LinksForm(wtf.Form):
  name = wtf.StringField('Name',validators=[wtf.validators.required()], filters=[util.strip_filter])
  url = wtf.StringField('Value',filters=[util.strip_filter],default="http://")
  sort = wtf.IntegerField('Sort',default=0)

@app.route('/_s/admin/links',endpoint='admin_site_links')
@app.route('/admin/links', methods=['GET','POST'])
@app.route('/admin/links/<int:id>', methods=['GET','POST'])
@app.route('/admin/links/<act>_<int:id>')
@auth.admin_required
def links(id=0,act=''):
  if act=='delete' and id:
    #delete
    k=ndb.Key(cms.Links,id)
    k.delete()
    flask.flash('delete link success', category='success')
    memcache.delete(memkey.links_key)
    return flask.redirect(flask.url_for('links'))
  query=cms.Links.query()
  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_dbs(query.fetch())
  btn = 'Create'
  form = LinksForm()
  if id:
    obj=cms.Links.get_by_id(id)
    if not obj:
      flask.flash('invalid obj id', category='danger')
      return flask.render_template('admin/links.html',has_json=True,form=form,data=query,btn=btn)
    else:
      btn = 'Save'
      form=LinksForm(obj=obj)
  if form.validate_on_submit():
    name=form.name.data
    if id:
      # update
      # check existence
      if obj.name != name:
        if query.filter(cms.Links.name==name,
          cms.Links.key!=ndb.Key(cms.Links,id)).get():
          flask.flash('name exist',category='danger')
          return flask.render_template('admin/links.html',has_json=True,form=form,data=query,btn=btn)
      form.populate_obj(obj)
      obj.put()
      flask.flash('update success',category='success')
    else:
      # create
      # check existence
      if query.filter(cms.Links.name==name).get():
        flask.flash('name exist',category="danger")
        return flask.render_template('admin/links.html',has_json=True,form=form,data=query,btn=btn)
      item = cms.Links(
        name=name,
        url=form.url.data,
        sort=form.sort.data)
      item.put()
      flask.flash('link add success',category='success')
    memcache.delete(memkey.links_key)
    return flask.redirect(flask.url_for('links'))
  #get
  else:
    return flask.render_template('admin/links.html',has_json=True,form=form,data=query,btn=btn)

###########################################
# Article
###########################################

class ArticleForm(wtf.Form):
  category = wtf.SelectField('Category',coerce=int,choices=[(v.key.id(),v.name) for v in cms.Category.query().fetch()])
  title = wtf.StringField('Title',validators=[wtf.validators.required()], filters=[util.strip_filter])
  slug = wtf.StringField('Slug',filters=[util.strip_filter])
  abstract = wtf.TextAreaField('Abstract',filters=[util.strip_filter])
  content = wtf.TextAreaField('Content',validators=[wtf.validators.required()], filters=[util.strip_filter], description='You can use markdown and <button type="button" class="btn btn-success btn-xs" data-toggle="modal" id="btnpreview" data-target="#preview"><i class="fa fa-eye">&nbsp;</i>preview</button> here')
  tags = wtf.StringField('Tags')
  commentclosed = wtf.BooleanField('Close comment',default=False)

# @app.route('/_s/admin/posts',endpoint='admin_site_lposts')
@app.route('/admin/posts', methods=['GET','POST'])
@app.route('/admin/posts/<int:id>', methods=['GET','POST'])
@app.route('/admin/posts/<act>_<int:id>')
@auth.admin_required
def posts(id=0,act=''):
  if act=='delete' and id:
    #delete
    # k=ndb.Key(cms.Article,id)
    article=cms.Article.get_by_id(id)
    update_category(None,article.category)
    update_tags([],article.tags)
    article.key.delete()
    flask.flash('delete post success', category='success')
    memcache.flush_all()
    return flask.redirect(flask.url_for('posts'))
  # pager
  article_qry=cms.Article.query()
  # return util.jsonify_model_dbs(article_qry)
  # next_curs, prev_curs = None, None
  # curs = Cursor.from_websafe_string(util.param('curs')) if util.param('curs') else None
  # if curs and util.param('prev'):
  #   curs = curs.reversed()
  # query, nextcurs, more = article_qry.order(-cms.Article.created).fetch_page(PAGESIZE,start_cursor=curs)
  # if more and nextcurs:
  #   next_curs = flask.url_for('posts',curs=nextcurs.urlsafe())
  # if curs:
  #   revcurs = curs.reversed()
  #   query2, precurs, more = article_qry.order(cms.Article.created).fetch_page(PAGESIZE,start_cursor=revcurs)
  #   if precurs:
  #     prev_curs = flask.url_for('posts',curs=precurs.urlsafe(),prev=1)

  btn = 'Create'
  form = ArticleForm()
  if id:
    obj=cms.Article.get_by_id(id)
    if not obj:
      flask.flash('invalid obj id', category='danger')
      return flask.render_template(
        'admin/posts.html',
        form=form,
        data=query,
        btn=btn)
        # next_curs=next_curs,
        # prev_curs=prev_curs)
    else:
      btn = 'Save'
      form=ArticleForm(obj=obj)
      if flask.request.method=='GET':
        form.category.data=obj.category.id()
        form.tags.data=obj.str_tags
  if form.validate_on_submit() and flask.request.method=='POST':
    name=form.title.data
    cate=ndb.Key(cms.Category,form.category.data)
    tags=util.settag(form.tags.data)
    if id:
      # update
      # check existence
      if obj.title != name:
        if article_qry.filter(cms.Article.title==name,
          cms.Article.key!=ndb.Key(cms.Article,id)).get():
          flask.flash('title exist',category='danger')
          return flask.render_template(
            'admin/posts.html',
            form=form,
            data=query,
            btn=btn)
            # next_curs=next_curs,
            # prev_curs=prev_curs)
      form.category.data=cate
      form.tags.data=tags
      form.abstract.data=get_abstract(form.abstract.data,form.content.data)

      update_category(form.category.data,obj.category)
      update_tags(tags,obj.tags)

      form.populate_obj(obj)
      obj.put()
      flask.flash('update success',category='success')
      art_mem_key = '%s_%s'%(memkey.article_key,id)
      memcache.delete(art_mem_key)
    else:
      # create
      # check existence
      if article_qry.filter(cms.Article.title==name).get():
        flask.flash('title exist',category="danger")
        return flask.render_template('admin/posts.html',form=form,data=query,btn=btn)
      # todo: abstract
      item = cms.Article(
        author=auth.current_user_key(),
        title=name,
        category=cate,
        slug=form.slug.data,
        abstract= get_abstract(form.abstract.data,form.content.data),
        content=form.content.data,
        tags=tags,
        commentclosed=bool(form.commentclosed.data))
      item.put()
      update_category(cate)
      update_tags(tags)
      flask.flash('post success',category='success')
      memcache.flush_all()
    return flask.redirect(flask.url_for('posts'))
  #get
  else:
    return flask.render_template(
      'admin/posts.html',
      form=form,
      data=[], #query
      btn=btn)
      # next_curs=next_curs,
      # prev_curs=prev_curs)

def get_abstract(source, bkup):
  if not source:
    source = bkup
  source = util.remove_html_markup(markdown(source))
  return source[:200]

@ndb.transactional(xg=True)
def update_category(new_key=None, old_key=None):
  try:
    if old_key == new_key:
      return
    if new_key:
      nc = new_key.get()
      nc.entrycount = nc.entrycount+1 if nc.entrycount>0 else 1
      nc.put()
    if old_key:
      oc = old_key.get()
      oc.entrycount = oc.entrycount-1 if oc.entrycount>0 else 0
      oc.put()
    memcache.delete(memkey.cate_key)
  except Exception:
    pass

def update_tags(new_tags, old_tags=[]):
  try:
    tag_qry = cms.Tag.query()
    #decrease not used
    for t in old_tags:
      if t not in new_tags:
        tags = tag_qry.filter(cms.Tag.name == t).fetch()
        if tags:
          tag = tags[0]
          tag.entrycount = tag.entrycount-1 if tag.entrycount>0 else 0
          if tag.entrycount == 0:
            tag.key.delete()
          else:
            tag.put()
    #increase new added
    for t in new_tags:
      if t not in old_tags:
          tags = tag_qry.filter(cms.Tag.name == t).fetch()
          if tags:
            tag = tags[0]
            tag.entrycount = tag.entrycount+1 if tag.entrycount>0 else 1
          else:
            tag = cms.Tag(name=t,entrycount=1)
          tag.put()
  except Exception:
    pass
