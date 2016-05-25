# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
import settings

handler404 = 'CadVlan.Auth.views.handler404'
handler500 = 'CadVlan.Auth.views.handler500'

urlpatterns = patterns(
    '',
    # CSS - JS
    (r'^media/(.*)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT})
)

# Healthcheck
urlpatterns += patterns(
    '',
    url(r'^healthcheck$',
        lambda _: HttpResponse("WORKING")),
)

# URL's Auth
urlpatterns += patterns(
    'CadVlan.Auth.views',
    url('^[/]?$', 'login', name='',),
    url('^login[/]?$', 'login', name='login',),
    url('^logout[/]?$', 'logout', name='logout',),
    url('^home[/]?$', 'home', name='home',),
    url('^lost-pass[/]?$', 'lost_pass',
        name="home.lost.pass",),
    url('^change-pass[/]?$', 'change_password',
        name="home.change.pass",),
)

# URL's Script
urlpatterns += patterns(
    'CadVlan.Script.views',
    url('^script/list[/]?$', 'list_all', name='script.list',),
    url('^script/delete[/]?$', 'delete_all', name='script.delete',),
    url('^script/form[/]?$', 'add_form', name='script.form',),
    url('^script/edit/(?P<id_script>\d+)[/]?$', 'edit_form', name='script.edit.form',),
)

# URL's ScriptType
urlpatterns += patterns(
    'CadVlan.ScriptType.views',
    url('^script-type/list[/]?$',
        'list_all', name='script.type.list',),
    url('^script-type/delete[/]?$',
        'delete_all', name='script.type.delete',),
    url('^script-type/form[/]?$',
        'show_form', name='script.type.form',)
)

# URL's EquipAccess
urlpatterns += patterns(
    'CadVlan.EquipAccess.views',
    url('^equip-access/search-list[/]?$',
        'search_list', name='equip.access.search.list',),
    url('^equip-access/search-list/(?P<id_equip>\d+)[/]?$',
        'search_list_param', name='equip.access.search.list.param',),
    url('^equip-access/form[/]?$',
        'add_form', name='equip.access.form',),
    url('^equip-access/form/(?P<id_access>\d+)[/]?$',
        'edit', name='equip.access.edit',),
    url('^equip-access/delete[/]?$',
        'delete', name='equip.access.delete',),
)

# URL's Equipment Script
urlpatterns += patterns(
    'CadVlan.EquipScript.views',
    url('^equip-script/list[/]?$', 'search_list',
        name='equip.script.search.list',),
    url('^equip-script/delete[/]?$', 'delete_all',
        name='equip.script.delete',),
    url('^equip-script/add[/]?$', 'ajax_add_form',
        name='equip.script.add.ajax',),
)

# URL's Equipment Interface
urlpatterns += patterns(
    'CadVlan.EquipInterface.views',
    url('^equip-interface/list[/]?$', 'search_list',
        name='equip.interface.search.list',),
    url('^equip-interface/config-sync/(?P<equip_name>[^/]+)/(?P<is_channel>\d+)/(?P<ids>\d+)[/]?$',
        'config_sync_all', name='equip.interface.config.sync',),
    url('^equip-interface/delete[/]?$',
        'delete_all', name='equip.interface.delete',),
    url('^equip-interface/add/(?P<equip_name>[^/]+)[/]?$',
        'add_form', name='equip.interface.form',),
    url('^equip-interface/edit/(?P<equip_name>[^/]+)/(?P<id_interface>\d+)[/]?$',
        'edit_form', name='equip.interface.edit.form',),
    url('^equip-interface/edit-interface/(?P<id_interface>[^/]+)[/]?$',
        'edit', name='equip.interface.edit',),
    url('^equip-interface/addseveral/(?P<equip_name>[^/]+)[/]?$',
        'add_several_forms', name='equip.interface.several.form',),
    url('^equip-interface/disconnect/(?P<id_interface>\d+)/(?P<back_or_front>\d+)/(?P<equip_name>[^/]+)/(?P<id_interf_edit>\d+)[/]?$',
        'disconnect', name='equip.interface.disconnect',),
    url('^equip-interface/connect/(?P<id_interface>\d+)/(?P<front_or_back>\d+)[/]?$',
        'connect', name='equip.interface.connect',),
    url('^equip-interface/new-channel[/]?$', 'channel',
        name='inserir.channel',),
    url('^equip-interface/new-channel/interfaces/(?P<equip_name>[^/]+)[/]?$', 'add_channel',
        name='equip.interface.add.channel',),
    url('^equip-interface/edit-channel/(?P<channel_name>[^/]+)/(?P<equip_name>[^/]+)[/]?$', 'edit_channel',
        name='equip.interface.edit.channel',),
    url('^equip-interface/channel/delete[/]?$', 'channel_delete',
        name='delete.channel',),
    url('^equip-interface/insert-interface[/]?$', 'channel_insert_interface',
        name='insert.interface.channel',),
)

# URL's Equipment
urlpatterns += patterns(
    'CadVlan.Equipment.views',
    url('^equipment/autocomplete[/]?$', 'ajax_autocomplete_equips',
        name='equipment.autocomplete.ajax',),
    url('^equipment/autocomplete/external[/]?$', 'ajax_autocomplete_equips_external',
        name='equipment.autocomplete.ajax.external',),
    url('^equipment/list[/]?$', 'search_list',
        name='equipment.search.list',),
    url('^equipment/find[/]?$', 'ajax_list_equips',
        name='equipment.list.ajax',),
    url('^equipment/form[/]?$',
        'equip_form', name='equipment.form',),
    url('^equipment/edit/(?P<id_equip>\d+)[/]?$',
        'equip_edit', name='equipment.edit.by.id',),
    url('^equipment/modelo/(?P<id_marca>\d+)[/]?$',
        'ajax_modelo_equip', name='equipment.modelo.ajax',),
    url('^equipment/marca[/]?$', 'ajax_marca_equip',
        name='equipment.modelo.ajax',),
    url('^equipment/modelo-form[/]?$',
        'modelo_form', name='equipment.modelo.form',),
    url('^equipment/marca-form[/]?$', 'marca_form',
        name='equipment.marca.form',),
    url('^equipment/delete[/]?$',
        'delete_all', name='equipment.delete',),
    url('^equipment/ajax_view/(?P<id_equip>\d+)[/]?$',
        'ajax_view_real', name='equip.view.real',),
    url('^equipment/ajax_remove_real/(?P<id_vip>\d+)[/]?$',
        'ajax_remove_real', name='equip.remove.real',),
    url('^equipment/delete_equipment/(?P<id_equip>\d+)[/]?$',
        'delete_equipment', name='equip.delete.id',),
    url('^equipment/ajax_check_real/(?P<id_vip>\d+)[/]?$',
        'ajax_check_real', name='equip.check.real',),

)

# URL's Environment
urlpatterns += patterns(
    'CadVlan.Environment.views',
    url('^environment/list[/]?$',
        'list_all', name='environment.list',),
    url('^environment/remove[/]?$',
        'remove_environment', name='environment.remove',),
    url('^environment/ambiente-logico[/]?$', 'insert_ambiente_logico',
        name='environment.insert.ambiente.logico',),
    url('^environment/grupo-l3[/]?$', 'insert_grupo_l3',
        name='environment.insert.grupo.l3',),
    url('^environment/divisao-dc[/]?$', 'insert_divisao_dc',
        name='environment.insert.divisao.dc',),
    url('^environment/form[/]?$',
        'insert_ambiente', name='environment.form',),
    url('^environment/form/(?P<id_environment>\d+)[/]?$',
        'edit', name='environment.edit',),
    url('^environment/acl_paths[/]$',
        'ajax_autocomplete_acl_path', name='acl_path.autocomplete',),
    url('^environment/configuration/form/(?P<id_environment>\d+)[/]?$',
        'add_configuration', name='environment.configuration.add',),
    url('^environment/configuration/remove/(?P<environment_id>\d+)/(?P<configuration_id>\d+)/',
        'remove_configuration', name='environment.configuration.remove',),
)

# URL's Vlans
urlpatterns += patterns(
    'CadVlan.Vlan.views',
    url('^vlan/autocomplete[/]?$', 'ajax_autocomplete_vlans',
        name='vlan.autocomplete.ajax',),
    url('^vlan/get/(?P<id_vlan>\d+)[/]?$',
        'list_by_id', name='vlan.list.by.id',),
    url('^vlan/get/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'list_by_id', name='vlan.list.by.id',),
    url('^vlan/list[/]?$',
        'search_list', name='vlan.search.list',),
    url('^vlan/list/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$', 'search_list',
        name='vlan.search.list',),
    url('^vlan/find/(?P<id_vlan>\d+)[/]?$', 'ajax_list_vlans',
        name='vlan.list.ajax',),
    url('^vlan/find/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$', 'ajax_list_vlans',
        name='vlan.list.ajax',),
    url('^vlan/form[/]?$', 'vlan_form', name='vlan.form',),
    url('^vlan/aclfilename[/]?$', 'ajax_acl_name_suggest',
        name='ajax.vlan.acl.file.name',),
    url('^vlan/confirmvlan[/]?$', 'ajax_confirm_vlan',
        name='ajax.vlan.confirm',),
    url('^vlan/edit/(?P<id_vlan>\d+)[/]?$',
        'vlan_edit', name='vlan.edit.by.id',),
    url('^vlan/edit/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'vlan_edit', name='vlan.edit.by.id',),
    url('^vlan/delete[/]?$',
        'delete_all', name='vlan.delete',),
    url('^vlan/delete/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'delete_all', name='vlan.delete',),
    url('^vlan/delete/network/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'delete_all_network', name='vlan.network.delete',),
    url('^vlan/create/(?P<id_vlan>\d+)[/]?$',
        'create', name='vlan.create'),
    url('^vlan/create/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'create', name='vlan.create'),
    url('^vlan/create/network/(?P<id_vlan>\d+)[/]?$',
        'create_network', name='vlan.create.network'),
    url('^vlan/create/network/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'create_network', name='vlan.create.network'),
    url('^vlan/remove/network/(?P<id_vlan>\d+)[/]?$',
        'remove_network', name='vlan.remove.network'),
    url('^vlan/remove/network/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'remove_network', name='vlan.remove.network'),
    url('^vlan/form/get/available/environment/configuration/by/environment/id[/]?$',
        'ajax_get_available_ip_config_by_environment_id', name='vlan.get.available.environment.configuration'),
)

# URL's Network
urlpatterns += patterns(
    'CadVlan.Net.views',
    url('^network/form[/]?$',
        'add_network_form', name='network.form',),
    url('^network/edit/rede_ipv4/(?P<id_net>\d+)[/]?$',
        'edit_network4_form', name='network.edit.by.id.rede.ipv4',),
    url('^network/edit/rede_ipv4/(?P<id_net>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'edit_network4_form', name='network.edit.by.id.rede.ipv4',),
    url('^network/edit/rede_ipv6/(?P<id_net>\d+)[/]?$',
        'edit_network6_form', name='network.edit.by.id.rede.ipv6',),
    url('^network/edit/rede_ipv6/(?P<id_net>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'edit_network6_form', name='network.edit.by.id.rede.ipv6',),
    url('^network/form/(?P<id_vlan>\d+)[/]?$',
        'vlan_add_network_form', name='network.form.vlan',),
    url('^network/form/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'vlan_add_network_form', name='network.form.vlan',),
    url('^network/ajax_modal_ips[/]?$', 'ajax_modal_ip_dhcp_server',
        name='network.modal.ips.ajax',),
    url('^network/get/ip4/(?P<id_net>\d+)[/]?$',
        'list_netip4_by_id', name='network.ip4.list.by.id',),
    url('^network/get/ip4/(?P<id_net>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'list_netip4_by_id', name='network.ip4.list.by.id',),
    url('^network/get/ip6/(?P<id_net>\d+)[/]?$',
        'list_netip6_by_id', name='network.ip6.list.by.id',),
    url('^network/get/ip6/(?P<id_net>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'list_netip6_by_id', name='network.ip6.list.by.id',),
    url('^network/ip4/(?P<id_net>\d+)[/]?$',
        'insert_ip4', name="network.insert.ip4",),
    url('^network/ip4/(?P<id_net>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'insert_ip4', name="network.insert.ip4",),
    url('^network/ip6/(?P<id_net>\d+)[/]?$',
        'insert_ip6', name="network.insert.ip6",),
    url('^network/ip6/(?P<id_net>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'insert_ip6', name="network.insert.ip6",),
    url('^network/edit/ip4/(?P<id_net>\d+)/(?P<id_ip4>\d+)[/]?$',
        'edit_ip4', name='network.edit.ip4',),
    url('^network/edit/ip4/(?P<id_net>\d+)/(?P<id_ip4>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'edit_ip4', name='network.edit.ip4',),
    url('^network/edit/ip6/(?P<id_net>\d+)/(?P<id_ip6>\d+)[/]?$',
        'edit_ip6', name='network.edit.ip6',),
    url('^network/edit/ip6/(?P<id_net>\d+)/(?P<id_ip6>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'edit_ip6', name='network.edit.ip6',),
    url('^network/delete/(?P<id_net>\d+)/ip4[/]?$',
        'delete_ip4', name='network.delete.ip4',),
    url('^network/delete/(?P<id_net>\d+)/ip4/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'delete_ip4', name='network.delete.ip4',),
    url('^network/delete/ip6/(?P<id_net>\d+)[/]?$',
        'delete_ip6', name='network.delete.ip6',),
    url('^network/delete/ip6byequip/(?P<id_ip>\d+)/(?P<id_equip>\d+)[/]?$',
        'delete_ip6_of_equip', name='network.delete.ip6.of.equip',),
    url('^network/delete/ip4byequip/(?P<id_ip>\d+)/(?P<id_equip>\d+)[/]?$',
        'delete_ip4_of_equip', name='network.delete.ip4.of.equip',),
    url('^network/insert/ip4byequip/(?P<id_net>\d+)/(?P<id_equip>\d+)[/]?$',
        'insert_ip4_by_equip', name='network.insert.ip4.of.equip',),
    url('^network/insert/ip6byequip/(?P<id_net>\d+)/(?P<id_equip>\d+)[/]?$',
        'insert_ip6_by_equip', name='network.insert.ip6.of.equip',),
    url('^network/assoc/ip4/(?P<id_net>\d+)/(?P<id_ip4>\d+)[/]?$',
        'assoc_ip4', name='network.assoc.ip4',),
    url('^network/assoc/ip4/(?P<id_net>\d+)/(?P<id_ip4>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'assoc_ip4', name='network.assoc.ip4',),
    url('^network/assoc/ip6/(?P<id_net>\d+)/(?P<id_ip6>\d+)[/]?$',
        'assoc_ip6', name='network.assoc.ip6',),
    url('^network/assoc/ip6/(?P<id_net>\d+)/(?P<id_ip6>\d+)/(?P<id_vlan>\d+)/(?P<sf_number>\d+)/(?P<sf_name>\w+)/(?P<sf_environment>\d+)/(?P<sf_nettype>\d+)/(?P<sf_subnet>\d+)/(?P<sf_ipversion>\d+)/(?P<sf_network>\w+)/(?P<sf_iexact>\d+)/(?P<sf_acl>\d+)[/]?$',
        'assoc_ip6', name='network.assoc.ip6',),
    url('^network/get-available-vip-environment[/]?$',
        'available_evip', name='network.available.evips'),
)

# URL's Option Vip
urlpatterns += patterns(
    'CadVlan.OptionVip.views',
    url('^option-vip/list[/]?$',
        'list_all', name='option-vip.list',),
    url('^option-vip/delete[/]?$',
        'delete_all', name='option-vip.delete',),
    url('^option-vip/form[/]?$',
        'add_form', name='option-vip.form',),
    url('^option-vip/form/(?P<id_optionvip>\d+)[/]?$',
        'edit_form', name='option-vip.edit',),
    url('^option-vip/associate4/(?P<id_net>\d+)[/]?$',
        'option_vip_associate_net4', name='option-vip.associate.net4',),
    url('^option-vip/associate6/(?P<id_net>\d+)[/]?$',
        'option_vip_associate_net6', name='option-vip.associate.net6',),
)

# URL's Environment Vip
urlpatterns += patterns(
    'CadVlan.EnvironmentVip.views',
    url('^environment-vip/list[/]?$',
        'list_all', name='environment-vip.list',),
    url('^environment-vip/delete[/]?$',
        'delete_all', name='environment-vip.delete',),
    url('^environment-vip/form[/]?$', 'add_form',
        name='environment-vip.form',),
    url('^environment-vip/form/(?P<id_environmentvip>\d+)[/]?$',
        'edit_form', name='environment-vip.edit',),

)

# URL's Group Equipment
urlpatterns += patterns(
    'CadVlan.GroupEquip.views',
    url('^group-equip/list[/]?$',
        'list_all', name='group-equip.list',),
    url('^group-equip/delete[/]?$',
        'delete_all', name='group-equip.delete',),
    url('^group-equip/form[/]?$',
        'add_form', name='group-equip.form',),
    url('^group-equip/form/(?P<id_group_equipament>\d+)[/]?$',
        'edit_form', name='group-equip.edit',),
)

# URL's Equipment Group
urlpatterns += patterns(
    'CadVlan.EquipGroup.views',
    url(
        '^equip-group/list/(?P<id_egroup>\d+)/(?P<tab>\d+)[/]?$', 'list_all', name='equip-group.list',),
    url('^equip-group/delete/(?P<id_egroup>\d+)[/]?$',
        'delete_all', name='equip-group.delete',),
    url('^equip-group/form/(?P<id_egroup>\d+)[/]?$',
        'add_form', name='equip-group.form',),
    url('^equip-group/form/(?P<id_egroup>\d+)/(?P<id_right>\d+)[/]?$',
        'edit_right', name='equip-user-group.edit',),
    url('^equip-user-group/form/(?P<id_egroup>\d+)[/]?$',
        'add_right', name='equip-user-group.form',),
    url('^equip-user-group/delete/(?P<id_egroup>\d+)[/]?$',
        'delete_right', name='equip-user-group.delete',),
)

# URL's Group User
urlpatterns += patterns(
    'CadVlan.GroupUser.views',
    url('^group-user/list[/]?$',
        'list_all', name='group-user.list',),
    url('^group-user/delete[/]?$',
        'delete_all', name='group-user.delete',),
    url('^group-user/form[/]?$',
        'add_form', name='group-user.form',),
    url('^group-user/form/(?P<id_group_user>\d+)[/]?$',
        'edit_form', name='group-user.edit',),

)

# URL's User
urlpatterns += patterns(
    'CadVlan.User.views',
    url(
        '^user/list/(?P<id_user>\d+)/(?P<status>\d+)[/]?$', 'list_all', name='user.list',),
    url('^user/form/(?P<id_user>\d+)/(?P<status>\d+)[/]?$',
        'list_all', name='user.form',),
    url('^user/edit/(?P<id_user>\d+)/(?P<status>\d+)[/]?$',
        'list_all', name='user.edit',),
    url('^user/delete[/]?$',
        'delete_all', name='user.delete',),
    # Ajax for ldap users selection
    url('ldap/usersbygroup/(?P<ldap_group>[^/]+)/(?P<id_user>[^/]+)[/]',
        'ajax_ldap_users_by_group', name='ldap.userbygroup.ajax'),
    url('ldap/pop_ldap_user_mail/(?P<cn>[^/]+)[/]',
        'ajax_ldap_pop_name_mail', name='ldap.pop_name_mail.ajax'),

    # Auto complete users in Logs
    url('^user/autocomplete[/]?$', 'ajax_autocomplete_users',
        name='user.autocomplete.ajax')

)

# URL's User Group
urlpatterns += patterns(
    'CadVlan.UserGroup.views',
    url(
        '^user-group/list/(?P<id_ugroup>\d+)/(?P<tab>\d+)[/]?$', 'list_all', name='user-group.list',),
    url('^user-group/delete/(?P<id_ugroup>\d+)[/]?$',
        'delete_user', name='user-group.delete',),
    url('^user-group/form/(?P<id_ugroup>\d+)[/]?$',
        'add_form_user', name='user-group.form',),
    url('^user-group-perm/form/(?P<id_ugroup>\d+)[/]?$',
        'add_form_perm', name='user-group-perm.form',),
    url('^user-group-perm/form/(?P<id_ugroup>\d+)/(?P<id_perm>\d+)[/]?$',
        'edit_form_perm', name='user-group-perm.edit',),
    url('^user-group-perm/delete/(?P<id_ugroup>\d+)[/]?$',
        'delete_perm', name='user-group-perm.delete',),
)

# URL's ACL
urlpatterns += patterns(
    'CadVlan.Acl.views',
    url(
        '^acl/create/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$', 'create', name='acl.create',),
    url(
        '^acl/remove/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$', 'remove', name='acl.remove',),
    url(
        '^acl/edit/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$', 'edit', name='acl.edit',),
    url(
        '^acl/script/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$', 'script', name='acl.script',),
    url('^acl/apply/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$',
        'apply_acl', name='acl.apply',),
    url('^acl/validate/(?P<id_vlan>\d+)/(?P<network>v4|v6)[/]?$',
        'validate', name='acl.validate',),
    url('^acl/template[/]?$', 'template_list',
        name='acl.template.list',),
    url('^acl/template/add/[/]?$',
        'template_add', name='acl.template.add',),
    url(
        '^acl/template/edit/(?P<template_name>.+)/(?P<network>IPv4|IPv6)[/]?$', 'template_edit', name='acl.template.edit',),
    url('^acl/template/delete[/]?$',
        'template_delete', name='acl.template.delete',),

    url('^acl/save/draft$', 'save_draft', name='acl.save.draft',),
    url('^acl/remove/draft$', 'remove_draft', name='acl.remove.draft',),

)

# URL's Vip Requests
urlpatterns += patterns(
    'CadVlan.VipRequest.views',
    url('^vip-request/token[/]?$',
        'generate_token', name='vip-request.token',),
    url('^vip-request/list[/]?$',
        'search_list', name='vip-request.list',),
    url('^vip-request/find[/]?$', 'ajax_list_vips',
        name='vip-request.list.ajax',),
    url('^vip-request/ajax_view/(?P<id_vip>\d+)[/]?$',
        'ajax_view_vip', name='vip.view.ajax',),


    url('^vip-request/operation/delete?$',
        'delete_vip', name='vip.delete',),
    url('^vip-request/operation/valid?$',
        'validate_vip', name='vip.valid',),
    url('^vip-request/operation/create?$',
        'create_vip', name='vip.create',),
    url('^vip-request/operation/remove?$',
        'remove_vip', name='vip.remove',),


    # url('^vip-request/l7/operation/valid?$',
    #     'validate_l7', name='l7.valid'),
    # url('^vip-request/l7/operation/apply?$',
    #     'apply_l7', name='l7.apply'),
    # url('^vip-request/l7/operation/rollback?$',
    #     'apply_rollback_l7', name='l7.rollback'),


    url('^vip-request/form[/]?$',
        'add_form', name='vip-request.form',),
    url('^vip-request/form/external[/]?$',
        'add_form_external', name='vip-request.form.external',),
    url('^vip-request/form/(?P<id_vip>\d+)[/]?$',
        'edit_form', name='vip-request.edit',),
    url('^vip-request/form/external/(?P<id_vip>\d+)[/]?$',
        'edit_form_external', name='vip-request.edit.external',),
    url('^vip-request/ajax_client/external[/]?$',
        'ajax_popular_client_external', name='vip-request.client.ajax.external',),
    url('^vip-request/ajax_client[/]?$',
        'ajax_popular_client', name='vip-request.client.ajax',),
    url('^vip-request/ajax_environment[/]?$',
        'ajax_popular_environment', name='vip-request.environment.ajax',),
    url('^vip-request/ajax_environment/external[/]?$',
        'ajax_popular_environment_external', name='vip-request.environment.ajax.external',),
    url('^vip-request/ajax_options[/]?$',
        'ajax_popular_options', name='vip-request.options.ajax',),
    url('^vip-request/ajax_options/external[/]?$',
        'ajax_popular_options_external', name='vip-request.options.ajax.external',),
    url('^vip-request/ajax_add_healthcheck[/]?$',
        'ajax_add_healthcheck', name='vip-request.add.healthcheck.ajax',),
    url('^vip-request/ajax_add_healthcheck/external[/]?$',
        'ajax_add_healthcheck_external', name='vip-request.add.healthcheck.ajax.external',),
    url('^vip-request/ajax_modal_real_server[/]?$',
        'ajax_model_ip_real_server', name='vip-request.modal.real.server.ajax',),
    url('^vip-request/ajax_modal_real_server/external[/]?$',
        'ajax_model_ip_real_server_external', name='vip-request.modal.real.server.ajax.external',),
    url('^vip-request/operation/ajax/(?P<id_vip>\d+)/(?P<operation>\d+)[/]?$',
        'ajax_validate_create_remove', name='vip.ajax.create.validate.remove',),
    url('^vip-request/tab/real-server/(?P<id_vip>\d+)[/]?$',
        'tab_real_server', name='vip-request.tab.real.server',),
    url('^vip-request/tab/real-server/(?P<id_vip>\d+)/status[/]?$',
        'tab_real_server_status', name='vip-request.tab.real.server.status.edit',),
    url('^vip-request/tab/real-server/(?P<id_vip>\d+)/status/(?P<status>enable|disable)[/]?$',
        'status_real_server', name='vip-request.tab.real.server.status',),
    url('^vip-request/tab/healthcheck/(?P<id_vip>\d+)[/]?$',
        'tab_healthcheck', name='vip-request.tab.healthcheck',),
    url('^vip-request/tab/maxcon/(?P<id_vip>\d+)[/]?$',
        'tab_maxcon', name='vip-request.tab.maxcon',),
    # url('^vip-request/tab/l7filter/(?P<id_vip>\d+)[/]?$',
    #     'tab_l7filter', name='vip-request.tab.l7filter',),
    url('^vip-request/tab/pools/(?P<id_vip>\d+)[/]?$',
        'tab_pools', name='vip-request.tab.pools',),
    url('^vip-request/pool_datatable/(?P<id_vip>\d+)[/]?$', 'pool_datatable', name='vip-request.pool_datatable',),
    url('^vip-request/ajax_rule[/]?$',
        'ajax_popular_rule', name='vip-request.rule.ajax',),
    url('^vip-request/ajax_rule/external[/]?$',
        'ajax_popular_rule_external', name='vip-request.rule.ajax.external',),

    url('^vip-request/load/pool[/]?$',
        'load_pool_for_copy', name='vip-request.load.pool',),
    url('^vip-request/save/pool[/]?$',
        'save_pool', name='save.pool',),
    url('^vip-request/load/new/pool[/]?$',
        'load_new_pool', name='vip-request.load.new.pool',),
    url('^vip-request/load/options/pool[/]?$',
        'load_options_pool', name='vip-request.load.options.pool',),
    url('^vip-request/list/pool/members/items/$',
        'pool_member_items', name='vip-request.members.items',),

    # External Access
    url('^vip-request/external/load/pool[/]?$',
        'external_load_pool_for_copy', name='vip-request.external.load.pool',),
    url('^vip-request/external/save/pool[/]?$',
        'external_save_pool', name='external.save.pool',),
    url('^vip-request/external/load/new/pool[/]?$',
        'external_load_new_pool', name='vip-request.external.load.new.pool',),
    url('^vip-request/external/load/options/pool[/]?$',
        'external_load_options_pool',
        name='vip-request.external.load.options.pool',),
    url('^vip-request/external/list/pool/members/items/$',
        'external_pool_member_items', name='vip-request.external.members.items',
        ),

)

# URL's Event Log
urlpatterns += patterns(
    'CadVlan.EventLog.views',
    url('^event-log/list[/]?$',
        'search_list', name='event-log.list',),
    url('^event-log/find[/]?$', 'ajax_list_logs',
        name='event-log.list.ajax',),
    url('^version?$', 'version_checks',
        name='version.check',),
)

# URL's Access Type Requests
urlpatterns += patterns(
    'CadVlan.AccessType.views',
    url('^access-type/form[/]?$',
        'access_type_form', name='access-type.form',),
)

# URL's Network Type Requests
urlpatterns += patterns(
    'CadVlan.NetworkType.views',
    url('^network-type/form[/]?$',
        'network_type_form', name='network-type.form',),
)

# URL's Equipment Type Requests
urlpatterns += patterns(
    'CadVlan.EquipmentType.views',
    url('^equipment-type/form[/]?$',
        'equipment_type_form', name='equipment-type.form',),
)

# URL's HealthcheckExpect Type Requests
urlpatterns += patterns(
    'CadVlan.HealthcheckExpect.views',
    url('^healthcheck-expect/form[/]?$',
        'healthcheck_expect_form', name='healthcheck-expect.form',),
)

# URL's LDAP
urlpatterns += patterns(
    'CadVlan.Ldap.views',
    url('^ldap/group/list[/]?$',
        'list_all_group', name='ldap.group.list',),
    url('^ldap/group/form[/]?$',
        'add_group_form', name='ldap.group.form',),
    url('^ldap/group/form/(?P<cn>[^/]+)[/]?$',
        'edit_group_form', name='ldap.group.edit',),
    url('^ldap/group/delete[/]?$', 'delete_group_all',
        name='ldap.group.delete',),
    url('^ldap/sudoer/list[/]?$',
        'list_all_sudoer', name='ldap.sudoer.list',),
    url('^ldap/sudoer/form[/]?$',
        'add_sudoer_form', name='ldap.sudoer.form',),
    url('^ldap/sudoer/form/(?P<cn>[^/]+)[/]?$',
        'edit_sudoer_form', name='ldap.sudoer.edit',),
    url('^ldap/sudoer/delete[/]?$',
        'delete_sudoer_all', name='ldap.sudoer.delete',),
    url('^ldap/user/list/(?P<pattern>interno|externo)[/]?$',
        'list_all_user', name='ldap.user.list',),
    url('^ldap/user/form/(?P<pattern>interno|externo)[/]?$',
        'add_user_form', name='ldap.user.form',),
    url('^ldap/user/form/(?P<cn>[^/]+)/(?P<pattern>interno|externo)[/]?$',
        'edit_user_form', name='ldap.user.edit',),
    url('^ldap/user/delete/(?P<pattern>interno|externo)[/]?$',
        'delete_user_all', name='ldap.user.delete',),
    url('^ldap/user/reset/password[/]?$',
        'ajax_reset_password_user', name='ldap.user.reset.pwd.ajax',),
    url('^ldap/user/lock[/]?$', 'ajax_lock_user',
        name='ldap.user.lock.ajax',),
    url('^ldap/user/unlock[/]?$', 'ajax_unlock_user',
        name='ldap.user.unlock.ajax',),
)

# URL's Filter
urlpatterns += patterns(
    'CadVlan.Filter.views',
    url('^filter/list[/]?$', 'list_all',
        name='filter.list',),
    url('^filter/delete[/]?$',
        'delete_all', name='filter.delete',),
    url('^filter/form[/]?$', 'add_form',
        name='filter.form',),
    url('^filter/form/(?P<id_filter>\d+)[/]?$',
        'edit_form', name='filter.edit',),

)

# URL's Block Rules'
urlpatterns += patterns(
    'CadVlan.BlockRules.views',
    url('^block/form[/]?$', 'add_form',
                            name='block.form',),
    url('^block/edit/(?P<id_env>\d+)[/]?$',
        'edit_form', name='block.edit.form',),
    url('^rules/list/(?P<id_env>\d+)[/]?$',
        'rules_list', name='block.rules.list',),
    url('^rules/form[/]?$',
        'rule_form', name='rule.form',),
    url('^rules/form/(?P<id_env>\d+)[/]?$',
        'rule_add_form', name='block.rules.form',),
    url('^rules/edit/(?P<id_env>\d+)/(?P<id_rule>\d+)[/]?$',
        'rule_edit_form', name='block.rules.edit',),
    url('^rules/remove/(?P<id_env>\d+)[/]?$',
        'rule_remove', name='block.rules.remove',),
    url('^block/ajax', 'block_ajax', name='block.ajax',),
)

# URL's Pool
urlpatterns += patterns(
    'CadVlan.Pool.views',
    url('^pool/list[/]?$', 'list_all', name='pool.list',),
    url('^pool/form[/]?$', 'add_form', name='pool.add.form',),
    url('^pool/edit/(?P<id_server_pool>\d+)[/]?$', 'edit_form', name='pool.edit.form',),

    url('^pool/delete[/]?$', 'delete', name='pool.delete',),
    url('^pool/remove[/]?$', 'remove', name='pool.remove',),
    url('^pool/create[/]?$', 'create', name='pool.create',),
    url('^pool/enable/[/]?$', 'enable', name='pool.enable',),
    url('^pool/disable/[/]?$', 'disable', name='pool.disable',),
    url('^pool/status_change/[/]?$', 'status_change', name='pool.status_change',),

    url('^pool/manage/tab1/(?P<id_server_pool>\d+)[/]?$', 'manage_tab1', name='pool.manage.tab1',),
    url('^pool/manage/tab2/(?P<id_server_pool>\d+)[/]?$', 'manage_tab2', name='pool.manage.tab2',),
    url('^pool/manage/tab3/(?P<id_server_pool>\d+)[/]?$', 'manage_tab3', name='pool.manage.tab3',),
    url('^pool/manage/tab4/(?P<id_server_pool>\d+)[/]?$', 'manage_tab4', name='pool.manage.tab4',),
    url('^pool/datatable[/]?$', 'datatable', name='pool.datatable',),
    url('^pool/spm_datatable/(?P<id_server_pool>\d+)/(?P<checkstatus>\d+)[/]?$', 'spm_datatable', name='pool.spm_datatable',),
    url('^pool/reqvip_datatable/(?P<id_server_pool>\d+)[/]?$', 'reqvip_datatable', name='pool.reqvip_datatable',),
    url('^pool/ajax_modal_ips[/]?$', 'ajax_modal_ip_real_server', name='pool.modal.ips.ajax',),
    url('^pool/ajax_modal_ips/external[/]?$', 'ajax_modal_ip_real_server_external', name='pool.modal.ips.ajax.external',),
    url('^pool/ajax_get_opcoes_pool_by_ambiente[/]?$', 'ajax_get_opcoes_pool_by_ambiente', name='pool.ajax.get.opcoes.pool.by.ambiente',),
    url('^pool/ajax_get_opcoes_pool_by_ambiente/external[/]?$', 'ajax_get_opcoes_pool_by_ambiente_external', name='pool.ajax.get.opcoes.pool.by.ambiente.external',),
    url('^pool/add_healthcheck_expect[/]?$', 'add_healthcheck_expect', name='pool.add.healthcheck.expect',),
    url('^pool/add_healthcheck_expect/external[/]?$', 'add_healthcheck_expect_external', name='pool.add.healthcheck.expect.external',),
)

# URL's Rack
urlpatterns += patterns(
    'CadVlan.Rack.views',
    url('^rack/form[/]?$', 'rack_form', name='rack.form',),
    url('^rack/ajax-view[/]?$', 'ajax_view', name='ajax.view.rack',),
    url('^rack/edit/(?P<id_rack>\d+)[/]?$', 'rack_edit', name='rack.edit',),
    url('^rack/delete[/]?$', 'rack_delete', name='rack.delete',),
    url('^rack/gerar-configuracao[/]?$', 'rack_config', name='rack.config',),
    url('^rack/alocar[/]?$', 'rack_alocar', name='rack.alocar',),
    url('^rack/save/deploy[/]?$', 'rack_deploy', name='rack.deploy',),
)

# URL's System
urlpatterns += patterns(
    'CadVlan.System.views',
    url('^system/variables/form[/]?$', 'add_variable', name='variables.form'),
    url('^system/variables/edit/(?P<variable_id>\d+)[/]?$', 'edit_variable', name='variables.edit'),
    url('^system/variables/list[/]?$', 'list_variables', name='variables.list'),
    url('^system/variables/delete[/]?$', 'delete_all', name='variables.delete'),
)
