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
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
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

# URL's EquipAccess
urlpatterns += patterns('CadVlan.EquipAccess.views',
    url('^equip-access/search-list$', 'search_list', name='equip.access.search.list',),
    url('^equip-access/search-list/(?P<id_equip>\d+)/$', 'search_list_param', name='equip.access.search.list.param',),
    url('^equip-access/form$','add_form', name='equip.access.form',),
    url('^equip-access/form/(?P<id_access>\d+)/$','edit', name='equip.access.edit',),
    url('^equip-access/delete/$','delete', name='equip.access.delete',),
)

# URL's Equipment Script
urlpatterns += patterns('CadVlan.EquipScript.views',
    url('^equip-script/list$', 'search_list', name='equip.script.search.list',),
    url('^equip-script/delete$','delete_all', name='equip.script.delete',),
    url('^equip-script/add$', 'ajax_add_form', name='equip.script.add.ajax',),
)

# URL's Equipment Interface
urlpatterns += patterns('CadVlan.EquipInterface.views',
    url('^equip-interface/list$', 'search_list', name='equip.interface.search.list',),
    url('^equip-interface/delete$','delete_all', name='equip.interface.delete',),
)

# URL's Equipment
urlpatterns += patterns('CadVlan.Equipment.views',
    url('^equipment/list$', 'ajax_list_equips', name='equipment.list.ajax',),
)

# URL's Environment
urlpatterns += patterns('CadVlan.Environment.views',
    url('^environment/list$','list_all', name='environment.list',),
)