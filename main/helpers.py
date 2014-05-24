from main import app
import modelcms as cms
import config
from markupsafe import Markup

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
    return cms.Tag.query().order(-cms.Tag.entrycount).fetch(50)
  def getLinks():
    return cms.Links.query().order(cms.Links.sort)
  def getAds(position):
    ad_db = cms.Ads.query(cms.Ads.name==position).get()
    return ad_db.value if ad_db else ''
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

  return dict(getCateName=getCateName,
  	getTags=getTags,
    getAds=getAds,
    getLinks=getLinks,
  	renderScript=renderScript,
    renderStyle=renderStyle)

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
