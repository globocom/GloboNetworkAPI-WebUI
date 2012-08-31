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
    url('^equip-interface/add/(?P<equip_name>[^/]+)[/]?$','add_form', name='equip.interface.form',),
    url('^equip-interface/edit/(?P<equip_name>[^/]+)/(?P<id_interface>\d+)[/]?$','edit_form', name='equip.interface.edit.form',),
    url('^equip-interface/addseveral/(?P<equip_name>[^/]+)[/]?$','add_several_forms', name='equip.interface.several.form',),
    url('^equip-interface/disconnect/(?P<id_interface>\d+)/(?P<back_or_front>\d+)/(?P<equip_name>[^/]+)/(?P<id_interf_edit>\d+)[/]?$','disconnect', name='equip.interface.disconnect',),
    url('^equip-interface/connect/(?P<id_interface>\d+)/(?P<front_or_back>\d+)[/]?$','connect', name='equip.interface.connect',),
)

# URL's Equipment
urlpatterns += patterns('CadVlan.Equipment.views',
    url('^equipment/autocomplete[/]?$', 'ajax_autocomplete_equips', name='equipment.autocomplete.ajax',),
    url('^equipment/list[/]?$', 'search_list', name='equipment.search.list',),
    url('^equipment/find[/]?$', 'ajax_list_equips', name='equipment.list.ajax',),
    url('^equipment/form[/]?$', 'equip_form', name='equipment.form',),
    url('^equipment/edit/(?P<id_equip>\d+)[/]?$', 'equip_edit', name='equipment.edit.by.id',),
    url('^equipment/modelo/(?P<id_marca>\d+)[/]?$', 'ajax_modelo_equip', name='equipment.modelo.ajax',),
    url('^equipment/marca[/]?$', 'ajax_marca_equip', name='equipment.modelo.ajax',),
    url('^equipment/modelo-form[/]?$', 'modelo_form', name='equipment.modelo.form',),
    url('^equipment/marca-form[/]?$', 'marca_form', name='equipment.marca.form',),
    url('^equipment/delete[/]?$','delete_all', name='equipment.delete',),
    
)

# URL's Environment
urlpatterns += patterns('CadVlan.Environment.views',
    url('^environment/list[/]?$', 'list_all', name='environment.list',),
    url('^environment/ambiente-logico[/]?$', 'insert_ambiente_logico', name='environment.insert.ambiente.logico',),
    url('^environment/grupo-l3[/]?$', 'insert_grupo_l3', name='environment.insert.grupo.l3',),
    url('^environment/divisao-dc[/]?$', 'insert_divisao_dc', name='environment.insert.divisao.dc',),
    url('^environment/form[/]?$', 'insert_ambiente', name='environment.form',),
    url('^environment/form/(?P<id_environment>\d+)[/]?$', 'edit', name='environment.edit',),
)

# URL's Vlans
urlpatterns += patterns('CadVlan.Vlan.views',
    url('^vlan/autocomplete[/]?$', 'ajax_autocomplete_vlans', name='vlan.autocomplete.ajax',),
    url('^vlan/get/(?P<id_vlan>\d+)[/]?$', 'list_by_id', name='vlan.list.by.id',), 
    url('^vlan/list[/]?$','search_list', name='vlan.search.list',),
    url('^vlan/find[/]?$','ajax_list_vlans', name='vlan.list.ajax',),
    url('^vlan/form[/]?$','vlan_form',name='vlan.form',), 
    url('^vlan/aclfilename[/]?$', 'ajax_acl_name_suggest', name='ajax.vlan.acl.file.name',),
    url('^vlan/edit/(?P<id_vlan>\d+)[/]?$','vlan_edit',name='vlan.edit.by.id',),
    url('^vlan/delete[/]?$','delete_all', name='vlan.delete',),
    url('^vlan/delete/network/(?P<id_vlan>\d+)[/]?$','delete_all_network', name='vlan.network.delete',),
)

# URL's Network
urlpatterns += patterns('CadVlan.Net.views',
    url('^network/form[/]?$', 'add_network_form', name='network.form',),
    url('^network/edit/rede_ipv4/(?P<id_net>\d+)[/]?$', 'edit_network4_form', name='network.edit.by.id.rede.ipv4',),
    url('^network/edit/rede_ipv6/(?P<id_net>\d+)[/]?$', 'edit_network6_form', name='network.edit.by.id.rede.ipv6',),
    url('^network/form/(?P<id_vlan>\d+)[/]?$', 'vlan_add_network_form', name='network.form.vlan',),
    url('^network/get/ip4/(?P<id_net>\d+)[/]?$', 'list_netip4_by_id', name='network.ip4.list.by.id',),
    url('^network/get/ip6/(?P<id_net>\d+)[/]?$', 'list_netip6_by_id', name='network.ip6.list.by.id',),
    url('^network/ip4/(?P<id_net>\d+)[/]?$','insert_ip4',name="network.insert.ip4",),
    url('^network/ip6/(?P<id_net>\d+)[/]?$','insert_ip6',name="network.insert.ip6",),
    url('^network/edit/ip4/(?P<id_net>\d+)/(?P<id_ip4>\d+)[/]?$','edit_ip4',name='network.edit.ip4',),
    url('^network/edit/ip6/(?P<id_net>\d+)/(?P<id_ip6>\d+)[/]?$','edit_ip6',name='network.edit.ip6',),
    url('^network/delete/(?P<id_net>\d+)/ip4[/]?$','delete_ip4',name='network.delete.ip4',),
    url('^network/delete/ip6/(?P<id_net>\d+)[/]?$','delete_ip6',name='network.delete.ip6',),
    url('^network/delete/ip6byequip/(?P<id_ip>\d+)/(?P<id_equip>\d+)[/]?$','delete_ip6_of_equip',name='network.delete.ip6.of.equip',),
    url('^network/delete/ip4byequip/(?P<id_ip>\d+)/(?P<id_equip>\d+)[/]?$','delete_ip4_of_equip',name='network.delete.ip4.of.equip',),
    url('^network/insert/ip4byequip/(?P<id_net>\d+)/(?P<id_equip>\d+)[/]?$','insert_ip4_by_equip',name='network.insert.ip4.of.equip',),
    url('^network/insert/ip6byequip/(?P<id_net>\d+)/(?P<id_equip>\d+)[/]?$','insert_ip6_by_equip',name='network.insert.ip6.of.equip',),
)

# URL's Option Vip
urlpatterns += patterns('CadVlan.OptionVip.views',
    url('^option-vip/list[/]?$', 'list_all', name='option-vip.list',),
    url('^option-vip/delete[/]?$', 'delete_all', name='option-vip.delete',),
    url('^option-vip/form[/]?$', 'add_form', name='option-vip.form',),
    url('^option-vip/form/(?P<id_optionvip>\d+)[/]?$', 'edit_form', name='option-vip.edit',),
    url('^option-vip/associate4/(?P<id_net>\d+)[/]?$','option_vip_associate_net4', name='option-vip.associate.net4',),
    url('^option-vip/associate6/(?P<id_net>\d+)[/]?$','option_vip_associate_net6', name='option-vip.associate.net6',),
)

# URL's Environment Vip
urlpatterns += patterns('CadVlan.EnvironmentVip.views',
    url('^environment-vip/list[/]?$', 'list_all', name='environment-vip.list',),
    url('^environment-vip/delete[/]?$', 'delete_all', name='environment-vip.delete',),
    url('^environment-vip/form[/]?$', 'add_form', name='environment-vip.form',),
    url('^environment-vip/form/(?P<id_environmentvip>\d+)[/]?$', 'edit_form', name='environment-vip.edit',),

)

# URL's Group Equipment
urlpatterns += patterns('CadVlan.GroupEquip.views',
    url('^group-equip/list[/]?$', 'list_all', name='group-equip.list',),
    url('^group-equip/delete[/]?$', 'delete_all', name='group-equip.delete',),
    url('^group-equip/form[/]?$', 'add_form', name='group-equip.form',),
    url('^group-equip/form/(?P<id_group_equipament>\d+)[/]?$', 'edit_form', name='group-equip.edit',),
)

# URL's Equipment Group
urlpatterns += patterns('CadVlan.EquipGroup.views',
    url('^equip-group/list/(?P<id_egroup>\d+)/(?P<tab>\d+)[/]?$', 'list_all', name='equip-group.list',),
    url('^equip-group/delete/(?P<id_egroup>\d+)[/]?$', 'delete_all', name='equip-group.delete',),
    url('^equip-group/form/(?P<id_egroup>\d+)[/]?$', 'add_form', name='equip-group.form',),
    url('^equip-group/form/(?P<id_egroup>\d+)/(?P<id_right>\d+)[/]?$', 'edit_right', name='equip-user-group.edit',),
    url('^equip-user-group/form/(?P<id_egroup>\d+)[/]?$', 'add_right', name='equip-user-group.form',),
    url('^equip-user-group/delete/(?P<id_egroup>\d+)[/]?$', 'delete_right', name='equip-user-group.delete',),
)

# URL's Group User
urlpatterns += patterns('CadVlan.GroupUser.views',
    url('^group-user/list[/]?$', 'list_all', name='group-user.list',),
    url('^group-user/delete[/]?$', 'delete_all', name='group-user.delete',),
    url('^group-user/form[/]?$', 'add_form', name='group-user.form',),
    url('^group-user/form/(?P<id_group_user>\d+)[/]?$', 'edit_form', name='group-user.edit',),    
    
)

# URL's Group User
urlpatterns += patterns('CadVlan.User.views',
    url('^user/list/(?P<id_user>\d+)/(?P<status>\d+)[/]?$', 'list_all', name='user.list',),
    url('^user/form/(?P<id_user>\d+)/(?P<status>\d+)[/]?$', 'list_all', name='user.form',),
    url('^user/edit/(?P<id_user>\d+)/(?P<status>\d+)[/]?$', 'list_all', name='user.edit',),
    url('^user/delete[/]?$', 'delete_all', name='user.delete',),
)

# URL's User Group
urlpatterns += patterns('CadVlan.UserGroup.views',
    url('^user-group/list/(?P<id_ugroup>\d+)/(?P<tab>\d+)[/]?$', 'list_all', name='user-group.list',),
    url('^user-group/delete/(?P<id_ugroup>\d+)[/]?$', 'delete_user', name='user-group.delete',),
    url('^user-group/form/(?P<id_ugroup>\d+)[/]?$', 'add_form_user', name='user-group.form',),
    url('^user-group-perm/form/(?P<id_ugroup>\d+)[/]?$', 'add_form_perm', name='user-group-perm.form',),
    url('^user-group-perm/form/(?P<id_ugroup>\d+)/(?P<id_perm>\d+)[/]?$', 'edit_form_perm', name='user-group-perm.edit',),
    url('^user-group-perm/delete/(?P<id_ugroup>\d+)[/]?$', 'delete_perm', name='user-group-perm.delete',),
)

# URL's ACL
urlpatterns += patterns('CadVlan.Acl.views',
    url('^acl/create/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$', 'create', name='acl.create',),
    url('^acl/remove/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$', 'remove', name='acl.remove',),
    url('^acl/edit/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$', 'edit', name='acl.edit',),
    url('^acl/script/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$', 'script', name='acl.script',),
    url('^acl/apply/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$', 'apply_acl', name='acl.apply',),
    url('^acl/validate/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$','validate',name='acl.validate',),
)

# URL's Vip Requests
urlpatterns += patterns('CadVlan.VipRequest.views',
    url('^vip-request/list[/]?$', 'search_list', name='vip-request.list',),
    url('^vip-request/find[/]?$', 'ajax_list_vips', name='vip-request.list.ajax',),
    url('^vip-request/ajax_view/(?P<id_vip>\d+)[/]?$', 'ajax_view_vip', name='vip.view.ajax',),
    url('^vip-request/operation/(?P<operation>\d+)[/]?$', 'delete_validate_create', name='vip.delete.create.validate',),
    url('^vip-request/form[/]?$', 'add_form', name='vip-request.form',),
    url('^vip-request/form/(?P<id_vip>\d+)[/]?$', 'edit_form', name='vip-request.edit',),
    url('^vip-request/ajax_client[/]?$', 'ajax_popular_client', name='vip-request.client.ajax',),
    url('^vip-request/ajax_environment[/]?$', 'ajax_popular_environment', name='vip-request.environment.ajax',),
    url('^vip-request/ajax_options[/]?$', 'ajax_popular_options', name='vip-request.options.ajax',),
    url('^vip-request/ajax_add_healthcheck[/]?$', 'ajax_add_healthcheck', name='vip-request.add.healthcheck.ajax',),
    url('^vip-request/ajax_modal_real_server[/]?$', 'ajax_model_ip_real_server', name='vip-request.modal.real.server.ajax',),
    url('^vip-request/operation/ajax/(?P<id_vip>\d+)/(?P<operation>\d+)[/]?$', 'ajax_validate_create', name='vip.ajax.create.validate',),
    url('^vip-request/tab/real-server/(?P<id_vip>\d+)[/]?$', 'tab_real_server', name='vip-request.tab.real.server',),
    url('^vip-request/tab/real-server/(?P<id_vip>\d+)/status/(?P<status>enable|disable)[/]?$', 'status_real_server', name='vip-request.tab.real.server.status',),
    
)

# URL's Access Type Requests
urlpatterns += patterns('CadVlan.AccessType.views',
    url('^access-type/form[/]?$', 'access_type_form', name='access-type.form',),
)

# URL's Network Type Requests
urlpatterns += patterns('CadVlan.NetworkType.views',
    url('^network-type/form[/]?$', 'network_type_form', name='network-type.form',),
)

# URL's Equipment Type Requests
urlpatterns += patterns('CadVlan.EquipmentType.views',
    url('^equipment-type/form[/]?$', 'equipment_type_form', name='equipment-type.form',),
)

# URL's HealthcheckExpect Type Requests
urlpatterns += patterns('CadVlan.HealthcheckExpect.views',
    url('^healthcheck-expect/form[/]?$', 'healthcheck_expect_form', name='healthcheck-expect.form',),
)

# URL's LDAP
urlpatterns += patterns('CadVlan.Ldap.views',
    url('^ldap/group-list[/]?$', 'list_all_group', name='ldap.group.list',),
    url('^ldap/group-form[/]?$', 'add_group_form', name='ldap.group.form',),
    url('^ldap/group-form/(?P<cn>[^/]+)[/]?$', 'edit_group_form', name='ldap.group.edit',),
    url('^ldap/group-delete[/]?$', 'delete_group_all', name='ldap.group.delete',),
)