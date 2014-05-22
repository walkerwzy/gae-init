# coding: utf-8

from main import app
import flask
from flask.ext import wtf
import walkermodel
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

@app.route('/test')
def test():
  '''demo of how to use raw Response obj and mimetype'''
  return flask.Response("hello world",mimetype="text/plain")

#formtest
class myform(wtf.Form):
    fdtxt=wtf.StringField("name",[wtf.validators.required()])
    fdddl=wtf.SelectField("type",choices=[(1,'a'),(2,'b'),(3,'c')],default=2)
    fdpost=wtf.TextAreaField("post")

@app.route('/walker')
def index():
    form=myform()
    return flask.render_template('theme/default/testform.html',name="walker",form=form)

class testform(wtf.Form):
    f1=wtf.StringField('f1',[wtf.validators.required("required")])
    f2=wtf.StringField('f2')
    f3=wtf.IntegerField('f3',default=0)
    

@app.route('/update',methods=['GET','POST'])
def testlist():
    # u=walkermodel.Temo(f1='aa',f2='bb',f3=1)
    # u2=walkermodel.Temo(f1='aa',f2='bb',f3=2)
    # u3=walkermodel.Temo(f1='aa',f2='bb',f3=3)
    # ndb.put_multi([u,u2,u3])
    form = testform()
    if form.validate_on_submit():
        item = walkermodel.Temo(f1=form.f1.data,f2=form.f2.data,f3=form.f3.data)
        item.put()
        flask.flash('add obj success')
        return flask.redirect(flask.url_for('testlist'))
    else:
        next_curs, prev_curs = None, None
        query = walkermodel.Temo.query()
        curs = Cursor(urlsafe=flask.request.args.get('curs'))
        ls, nextcurs, more = query.order(walkermodel.Temo.f3).fetch_page(3,start_cursor=curs)
        if more and nextcurs:
            next_curs = flask.url_for('testlist',curs=nextcurs.urlsafe())
        revcurs = curs.reversed()
        pls, precurs, more = query.order(-walkermodel.Temo.f3).fetch_page(3,start_cursor=revcurs)
        if more and precurs:
            prev_curs = flask.url_for('testlist',curs=precurs.urlsafe())
        # return flask.render_template('theme/default/testlist.html',ls=ls,form=form,abc=flask.request.args.get('abc'))
        return flask.render_template('theme/default/testlist.html',ls=ls,form=form,next_curs=next_curs,prev_curs=prev_curs)

@app.route('/blog')
def blog():
    return flask.render_template('theme/default/demo.html')