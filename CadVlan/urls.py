# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.conf.urls.defaults import patterns, url
import settings

handler404 = 'CadVlan.Auth.views.handler404'
handler500 = 'CadVlan.Auth.views.handler500'

urlpatterns = patterns('',
    # CSS - JS
    (r'^media/(.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT})
)

# URL's Auth
urlpatterns += patterns('CadVlan.Auth.views',
    url('^$', 'login', name='',),
    url('^login$', 'login', name='login',),
    url('^logout$', 'logout', name='logout',),
    url('^home$', 'home', name='home',)
)

# URL's Script
urlpatterns += patterns('CadVlan.Script.views',
    url('^script/list$', 'list_all', name='script.list',),
    url('^script/delete$', 'delete_all', name='script.delete',),
    url('^script/form$', 'add_form', name='script.form',),
)

# URL's ScriptType
urlpatterns += patterns('CadVlan.ScriptType.views',
    url('^script-type/list$', 'list_all', name='script.type.list',),
    url('^script-type/delete$', 'delete_all', name='script.type.delete',),
    url('^script-type/form$', 'show_form', name='script.type.form',)
)

# URL's ScriptType
urlpatterns += patterns('CadVlan.EquipAccess.views',
    url('^equip-access/search-list$', 'search_list', name='script.type.search.list',),
)