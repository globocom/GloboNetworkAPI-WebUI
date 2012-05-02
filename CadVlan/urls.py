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
    url('^[/]?$', 'login', name='',),
    url('^login[/]?$', 'login', name='login',),
    url('^logout[/]?$', 'logout', name='logout',),
    url('^home[/]?$', 'home', name='home',),
    url('^lost-pass[/]?$','lost_pass',name="home.lost.pass",),
    url('^change-pass[/]?$','change_password',name="home.change.pass",),
)

# URL's Script
urlpatterns += patterns('CadVlan.Script.views',
    url('^script/list[/]?$', 'list_all', name='script.list',),
    url('^script/delete[/]?$', 'delete_all', name='script.delete',),
    url('^script/form[/]?$', 'add_form', name='script.form',),
)

# URL's ScriptType
urlpatterns += patterns('CadVlan.ScriptType.views',
    url('^script-type/list[/]?$', 'list_all', name='script.type.list',),
    url('^script-type/delete[/]?$', 'delete_all', name='script.type.delete',),
    url('^script-type/form[/]?$', 'show_form', name='script.type.form',)
)

# URL's EquipAccess
urlpatterns += patterns('CadVlan.EquipAccess.views',
    url('^equip-access/search-list[/]?$', 'search_list', name='equip.access.search.list',),
    url('^equip-access/search-list/(?P<id_equip>\d+)[/]?$', 'search_list_param', name='equip.access.search.list.param',),
    url('^equip-access/form[/]?$','add_form', name='equip.access.form',),
    url('^equip-access/form/(?P<id_access>\d+)[/]?$','edit', name='equip.access.edit',),
    url('^equip-access/delete[/]?$','delete', name='equip.access.delete',),
)

# URL's Equipment Script
urlpatterns += patterns('CadVlan.EquipScript.views',
    url('^equip-script/list[/]?$', 'search_list', name='equip.script.search.list',),
    url('^equip-script/delete[/]?$','delete_all', name='equip.script.delete',),
    url('^equip-script/add[/]?$', 'ajax_add_form', name='equip.script.add.ajax',),
)

# URL's Equipment Interface
urlpatterns += patterns('CadVlan.EquipInterface.views',
    url('^equip-interface/list[/]?$', 'search_list', name='equip.interface.search.list',),
    url('^equip-interface/delete[/]?$','delete_all', name='equip.interface.delete',),
)

# URL's Equipment
urlpatterns += patterns('CadVlan.Equipment.views',
    url('^equipment/autocomplete[/]?$', 'ajax_autocomplete_equips', name='equipment.autocomplete.ajax',),
    url('^equipment/list[/]?$', 'search_list', name='equipment.search.list',),
    url('^equipment/find[/]?$', 'ajax_list_equips', name='equipment.list.ajax',),
)

# URL's Environment
urlpatterns += patterns('CadVlan.Environment.views',
    url('^environment/list[/]?$','list_all', name='environment.list',),
    url('^environment/ambiente-logico[/]?$','insert_ambiente_logico', name='environment.insert.ambiente.logico',),
    url('^environment/grupo-l3[/]?$','insert_grupo_l3', name='environment.insert.grupo.l3',),
    url('^environment/divisao-dc[/]?$','insert_divisao_dc', name='environment.insert.divisao.dc',),
    url('^environment/form[/]?$','insert_ambiente', name='environment.form',),
)

# URL's Vlans
urlpatterns += patterns('CadVlan.Vlan.views',
    url('^vlan/get/(?P<id_vlan>\d+)[/]?$', 'list_by_id', name='vlan.list.by.id',), 
    url('^vlan/list[/]?$','search_list', name='vlan.search.list',),
    url('^vlan/find[/]?$','ajax_list_vlans', name='vlan.list.ajax',),
    
)

# URL's Network
urlpatterns += patterns('CadVlan.Net.views',
    url('^network/get/ip4/(?P<id_net>\d+)[/]?$', 'list_netip4_by_id', name='network.ip4.list.by.id',),
    url('^network/get/ip6/(?P<id_net>\d+)[/]?$', 'list_netip6_by_id', name='network.ip6.list.by.id',),
    url('^network/ip4/(?P<id_net>\d+)[/]?$','insert_ip4',name="network.insert.ip4",),
    url('^network/ip6/(?P<id_net>\d+)[/]?$','insert_ip6',name="network.insert.ip6",),
    url('^network/edit/ip4/(?P<id_net>\d+)/(?P<id_ip4>\d+)[/]?$','edit_ip4',name='network.edit.ip4',),
    url('^network/edit/ip6/(?P<id_net>\d+)/(?P<id_ip6>\d+)[/]?$','edit_ip6',name='network.edit.ip6',),
    url('^network/delete/(?P<id_net>\d+)/ip4[/]?$','delete_ip4',name='network.delete.ip4',),
    url('^network/delete/ip6/(?P<id_net>\d+)[/]?$','delete_ip6',name='network.delete.ip6',),
)