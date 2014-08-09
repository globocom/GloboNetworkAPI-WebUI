# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.forms.widgets import RadioFieldRenderer
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class RadioCustomRenderer(RadioFieldRenderer):

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        idt = u'%s_content' % self.attrs.get('id')
        return mark_safe(u"<div id='%s'>\n%s\n</div>" % (idt, u'\n'.join([u'%s' % force_unicode(w) for w in self])))
