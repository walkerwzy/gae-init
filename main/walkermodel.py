
#db test
from google.appengine.ext import ndb

class Temo(ndb.Model):
    f1=ndb.StringProperty()
    f2=ndb.StringProperty()
    f3=ndb.IntegerProperty(default=0)

    @property
    def ids(self):
        return self.key.id()
    # @ff.setter
    # def ff(self, value):
    #     self._ff = value

    @property
    def fromkey(self):
    	k=4644337115725824
    	return Temo.get_by_id(k)
        # return self._fromkey
    
    @property
    def keystr(self):
        return self.key.urlsafe()

    @property
    def strtokey(self):
    	k=ndb.Key(urlsafe='agxkZXZ-Z2FlLWluaXRyEQsSBFRlbW8YgICAgICAoAgM')
        return k

    def __unicode__(self):
    	return 'f1=%s, f2=%s, f3=%3.2f' % (self.f1, self.f2, self.f3)
