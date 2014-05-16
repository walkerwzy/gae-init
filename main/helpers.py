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
  def getTags(tags):
    if isinstance(tags,list):
      return ','.join(tags)
    return ''
  def renderScript(name=''):
  	if not name:
  		# load base scripts for all pages (e==True)
  		s = []
  		for module, scripts, e in config.SCRIPTS:
  			if e:
  				s.append(parse_script_str(module,scripts))
  		return Markup(''.join(s))
  	else:
  		# load specific scripts
  		for m, s, e in config.SCRIPTS:
  			if m == name and not e:
  				return Markup(parse_script_str(m,s))
  		return ''

  return dict(getCateName=getCateName,
  	getTags=getTags,
  	renderScript=renderScript)

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
