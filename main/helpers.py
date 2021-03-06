from main import app
import modelcms as cms
import config
from markupsafe import Markup
from markdown import markdown

###############################################################################
# jinja2_helpers
###############################################################################

@app.context_processor
def utility_processor():
  def getCateName(cateid):
    c = cms.Category.get_by_id(int(cateid))
    if c:
      return c.name
    return ''
  def getTags():
    return cms.Tag.tagcloud()
  def getLinks():
    return cms.Links.alllinks()
  def getAds(position):
    ad_dbs = cms.Ads.allads()
    ad_db = [a for a in ad_dbs if a.name == position]
    return ad_db[0].value if ad_db else ''
  def renderScript(name):
    for module, scripts in config.SCRIPTS:
      if module == name:
        return Markup(parse_script_str(module,scripts))
    return ''
  def renderStyle(name):
    s = []
    for module, styles in config.STYLES:
      if module == name:
        for style in styles:
          s.append(parse_style_str(style))
        return Markup(''.join(s))
    return ''
  def md(source):
    return markdown(source)

  return dict(getCateName=getCateName,
  	getTags=getTags,
    getAds=getAds,
    getLinks=getLinks,
  	renderScript=renderScript,
    renderStyle=renderStyle,
    markdown=md)

def parse_script_str(module,scripts):
	v = config.CURRENT_VERSION_ID
	if config.DEVELOPMENT:
		s = []
		for script in scripts:
			script=script.replace('.coffee', '.js').replace('src/script/', 'dst/script/')
			s.append('<script src="/p/{0}?{1}"></script>\n'.format(script,v))
		return ''.join(s)
	else:
		return '<script src="/p/min/script/{0}.min.js?{1}"></script>'.format(module,v)

def parse_style_str(style):
  v = config.CURRENT_VERSION_ID
  if config.DEVELOPMENT:
    style = style.replace('.less','.css').replace('src/style','dst/style')
  else:
    style = style.replace('.less','.min.css').replace('src/style','min/style')
  return '<link rel="stylesheet" href="/p/{0}?{1}">'.format(style,v)
