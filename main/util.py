# coding: utf-8

from datetime import datetime
from datetime import date
from uuid import uuid4
import re
import unicodedata
from unidecode import unidecode
import urllib

from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
import flask

import config


###############################################################################
# Request Parameters
###############################################################################
def param(name, cast=None):
  value = None
  if flask.request.json:
    return flask.request.json.get(name, None)

  if value is None:
    value = flask.request.args.get(name, None)
  if value is None and flask.request.form:
    value = flask.request.form.get(name, None)

  if cast and value is not None:
    if cast == bool:
      return value.lower() in ['true', 'yes', '1', '']
    if cast == list:
      return value.split(',') if len(value) > 0 else []
    return cast(value)
  return value


def get_next_url():
  next_url = param('next')
  if next_url:
    return next_url
  referrer = flask.request.referrer
  if referrer and referrer.startswith(flask.request.host_url):
    return referrer
  return flask.url_for('welcome')


###############################################################################
# Model manipulations
###############################################################################
def retrieve_dbs(
    query, order=None, limit=None, cursor=None, keys_only=None, **filters
  ):
  '''Retrieves entities from datastore, by applying cursor pagination
  and equality filters. Returns dbs or keys and more cursor value
  '''
  limit = limit or config.DEFAULT_DB_LIMIT
  cursor = Cursor.from_websafe_string(cursor) if cursor else None
  model_class = ndb.Model._kind_map[query.kind]
  if order:
    for o in order.split(','):
      if o.startswith('-'):
        query = query.order(-model_class._properties[o[1:]])
      else:
        query = query.order(model_class._properties[o])

  for prop in filters:
    if filters.get(prop, None) is None:
      continue
    if isinstance(filters[prop], list):
      for value in filters[prop]:
        query = query.filter(model_class._properties[prop] == value)
    else:
      query = query.filter(model_class._properties[prop] == filters[prop])

  model_dbs, more_cursor, more = query.fetch_page(
      limit, start_cursor=cursor, keys_only=keys_only,
    )
  more_cursor = more_cursor.to_websafe_string() if more else None
  return list(model_dbs), more_cursor


###############################################################################
# JSON Response Helpers
###############################################################################
def jsonify_model_dbs(model_dbs, more_cursor=None):
  '''Return a response of a list of dbs as JSON service result
  '''
  result_objects = []
  for model_db in model_dbs:
    result_objects.append(model_db_to_object(model_db))

  response_object = {
      'status': 'success',
      'count': len(result_objects),
      'now': datetime.utcnow().isoformat(),
      'result': result_objects,
    }
  if more_cursor:
    response_object['more_cursor'] = more_cursor
    response_object['more_url'] = generate_more_url(more_cursor)
  response = jsonpify(response_object)
  return response


def jsonify_model_db(model_db):
  result_object = model_db_to_object(model_db)
  response = jsonpify({
      'status': 'success',
      'now': datetime.utcnow().isoformat(),
      'result': result_object,
    })
  return response


def model_db_to_object(model_db):
  model_db_object = {}
  for prop in model_db._PROPERTIES:
    if prop == 'id':
      try:
        value = json_value(getattr(model_db, 'key', None).id())
      except:
        value = None
    else:
      value = json_value(getattr(model_db, prop, None))
    if value is not None:
      model_db_object[prop] = value
  return model_db_object


def json_value(value):
  if isinstance(value, datetime) or isinstance(value, date):
    return value.isoformat()
  if isinstance(value, ndb.Key):
    return value.urlsafe()
  if isinstance(value, blobstore.BlobKey):
    return urllib.quote(str(value))
  if isinstance(value, ndb.GeoPt):
    return '%s,%s' % (value.lat, value.lon)
  if isinstance(value, list):
    return [json_value(v) for v in value]
  if isinstance(value, long):
    # Big numbers are sent as strings for accuracy in JavaScript
    if value > 9007199254740992 or value < -9007199254740992:
      return str(value)
  if isinstance(value, ndb.Model):
    return model_db_to_object(value)
  return value


def jsonpify(*args, **kwargs):
  if param('callback'):
    content = '%s(%s)' % (
        param('callback'), flask.jsonify(*args, **kwargs).data,
      )
    mimetype = 'application/javascript'
    return flask.current_app.response_class(content, mimetype=mimetype)
  return flask.jsonify(*args, **kwargs)


###############################################################################
# Helpers
###############################################################################
def generate_more_url(more_cursor, base_url=None, cursor_name='cursor'):
  '''Substitutes or alters the current request URL with a new cursor parameter
  for next page of results
  '''
  if not more_cursor:
    return None
  base_url = base_url or flask.request.base_url
  args = flask.request.args.to_dict()
  args[cursor_name] = more_cursor
  return '%s?%s' % (base_url, urllib.urlencode(args))


def uuid():
  return uuid4().hex


# _slugify_strip_re = re.compile(r'[^\w\s-]')
# _slugify_hyphenate_re = re.compile(r'[-\s]+')


# def slugify(text):
#   if not isinstance(text, unicode):
#     text = unicode(text)
#   text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
#   text = unicode(_slugify_strip_re.sub('', text).strip().lower())
#   return _slugify_hyphenate_re.sub('-', text)

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))

def is_valid_username(username):
  return True if re.match('^[a-z0-9]+(?:[\.][a-z0-9]+)*$', username) else False


def update_query_argument(name, value=None, ignore='cursor', is_list=False):
  ignore = ignore.split(',') if isinstance(ignore, str) else ignore or []
  arguments = {}
  for key, val in flask.request.args.items():
    if key not in ignore and (is_list and value is not None or key != name):
      arguments[key] = val
  if value is not None:
    if is_list:
      values = []
      if name in arguments:
        values = arguments[name].split(',')
        del arguments[name]
      if value in values:
        values.remove(value)
      else:
        values.append(value)
      if values:
        arguments[name] = ','.join(values)
    else:
      arguments[name] = value
  query = '&'.join('%s=%s' % item for item in sorted(arguments.items()))
  return '%s%s' % (flask.request.path, '?%s' % query if query else '')


###############################################################################
# Lambdas
###############################################################################
strip_filter = lambda x: x.strip() if x else ''
email_filter = lambda x: x.lower().strip() if x else ''
sort_filter = lambda x: sorted(x) if x else []

###############################################################################
# walker_helpers
###############################################################################

def remove_html_markup(s):
  """http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python"""
  tag = False
  quote = False
  out = ""
  for c in s:
          if c == '<' and not quote:
              tag = True
          elif c == '>' and not quote:
              tag = False
          elif (c == '"' or c == "'") and tag:
              quote = not quote
          elif not tag:
              out = out + c
  return out

def settag(tagsstr):
    if tagsstr:
        tagsstr = remove_html_markup(tagsstr)
        if tagsstr:
            tagsstr = tagsstr.lower()
            tagsstr = tagsstr.replace(u"，",",")
            tagsstr = tagsstr.replace("/",",")
            tagsstr = tagsstr.replace("%",",")
            tagslist = map((lambda x: x.strip()),tagsstr.split(','))
            tagslist = list(set(tagslist))
            try:tagslist.remove('')
            except:pass
            return tagslist
        else:
            return []
    else:
        return []

def retrieve_dbs_pager(
    query, prev=False, order=None, limit=None, cursor=None, keys_only=None, **filters
  ):
  '''Retrieves entities from datastore, by applying cursor pagination
  and equality filters. Returns dbs or keys and more cursor value
  and return prev_page and next_page cursor
  '''
  limit = limit or config.DEFAULT_DB_LIMIT
  cursor = Cursor.from_websafe_string(cursor) if cursor else None
  if cursor and prev:
    cursor = cursor.reversed()
  model_class = ndb.Model._kind_map[query.kind]
  if order:
    for o in order.split(','):
      if o.startswith('-'):
        qry = query.order(-model_class._properties[o[1:]])
        qry_r = query.order(model_class._properties[o[1:]])
      else:
        qry = query.order(model_class._properties[o])
        qry_r = query.order(-model_class._properties[o])

  for prop in filters:
    if filters.get(prop, None) is None:
      continue
    if isinstance(filters[prop], list):
      for value in filters[prop]:
        qry = qry.filter(model_class._properties[prop] == value)
        qry_r = qry_r.filter(model_class._properties[prop] == value)
    else:
      qry = qry.filter(model_class._properties[prop] == filters[prop])
      qry_r = qry_r.filter(model_class._properties[prop] == filters[prop])

  model_dbs, more_cursor, more = qry.fetch_page(
      limit, start_cursor=cursor, keys_only=keys_only,
    )
  more_cursor = more_cursor.to_websafe_string() if more else None
  prev_more_cursor = None
  if cursor:
    prev_model_dbs, prev_more_cursor, prev_more = qry_r.fetch_page(
        limit, start_cursor=cursor.reversed(),keys_only=True,
      )
    prev_more_cursor = prev_more_cursor.to_websafe_string() if prev_more_cursor else None
    # thought prev_more is False, but we did't render that page, so there's a page left (prev)
  return list(model_dbs), more_cursor, prev_more_cursor
