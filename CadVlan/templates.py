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


LOGIN = 'login.html'
HOME = 'home.html'

MENUBAR = 'modulo/menubar.html'
MENU = 'menu.html'

HEADER = 'header.html'

VERSION_HTML = 'version.html'

# Ajax
AJAX_AUTOCOMPLETE_ENVIRONMENTS = 'ajax/environment-autocomplete-list.txt'
AJAX_AUTOCOMPLETE_LIST = 'ajax/autocomplete-list.json'
AJAX_VLAN_AUTOCOMPLETE = 'ajax/vlan-autocomplete-list.json'
AJAX_VLAN_LIST = 'ajax/vlan-list.json'
AJAX_ENVIRONMENT_LIST = 'ajax/env-list.json'
AJAX_CHILDREN_ENV = 'ajax/children-list.json'
AJAX_EQUIP_LIST = 'ajax/equip-list.json'
AJAX_VIPREQUEST_LIST = 'ajax/vip-list.json'
AJAX_LOG_LIST = 'ajax/log-list.json'
AJAX_NEW_PASS = 'ajax/newpass.html'
AJAX_SUGGEST_NAME = 'ajax/suggest-name.html'
AJAX_CONFIRM_VLAN = 'ajax/confirm-vlan.html'
VIPREQUEST_VIEW = 'ajax/view-vip.html'
AJAX_VIPREQUEST_CLIENT = 'ajax/request-vip-client.html'
AJAX_VIPREQUEST_ENVIRONMENT = 'ajax/request-vip-environment.html'
AJAX_VIPREQUEST_OPTIONS = 'ajax/request-vip-options.json'
AJAX_VIPREQUEST_RULE = 'ajax/request-vip-rule.json'
AJAX_VIPREQUEST_HEALTHCHECK = 'ajax/request-vip-add-healthcheck.json'
AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER = 'ajax/request-vip-model-ip-real-server.json'
AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER_HTML = 'ajax/request-vip-model-ip-real-server.html'
AJAX_LDAP_RESET_PASSWORD = 'ajax/ldap-reset-password.html'
JSON_ERROR = "error.json"
TOKEN_INVALID = "token_invalid.html"

AJAX_LDAP_USERS_BY_GROUP = 'ajax/select-ldap-user.html'
AJAX_LDAP_USER_POP_NAME_MAIL = 'ajax/pop_ldap_user_mail.json'

AJAX_AUTOCOMPLETE_EQUIPMENTS = 'ajax/autocomplete-equipment-ajax.json'
AJAX_AUTOCOMPLETE_ENVIRONMENT = 'ajax/autocomplete-environment-ajax.json'

# Script
SCRIPT_LIST = 'script/list.html'
SCRIPT_FORM = 'script/form.html'
SCRIPT_EDIT = 'script/edit.html'

# Script Type
SCRIPTTYPE_LIST = 'script-type/list.html'
SCRIPTTYPE_FORM = 'script-type/form.html'

# Environment
ENVIRONMENT_LIST = 'environment/list.html'
ENVIRONMENT_FORM = 'environment/form.html'
ENVIRONMENT_CONFIGURATION_FORM = 'environment/configuration.html'

# Equipment Access
EQUIPMENTACESS_SEARCH_LIST = 'equip-access/search-list.html'
EQUIPMENTACESS_FORM = 'equip-access/form.html'
EQUIPMENTACESS_EDIT = 'equip-access/edit.html'

# Equipment Script
EQUIPMENT_SCRIPT_SEARCH_LIST = 'equip-script/search-list.html'
EQUIPMENT_SCRIPT_ADD_FORM = 'ajax/equip-script-form.html'

# Equipment Interface
EQUIPMENT_INTERFACE_SEARCH_LIST = 'equip-interface/search-list.html'
EQUIPMENT_INTERFACE_FORM = 'equip-interface/form.html'
EQUIPMENT_INTERFACE_SEVERAL_FORM = 'equip-interface/several-form.html'
EQUIPMENT_INTERFACE_EDIT_FORM = 'equip-interface/edit-form.html'
EQUIPMENT_INTERFACE_CONNECT_FORM = 'equip-interface/connect-form.html'
EQUIPMENT_INTERFACE_ADD_FORM = 'equip-interface/add-form.html'
EQUIPMENT_INTERFACE_EDIT = 'equip-interface/edit-port.html'
EQUIPMENT_INTERFACE_ADD_CHANNEL = 'equip-interface/add-channel.html'
EQUIPMENT_INTERFACE_EDIT_CHANNEL = 'equip-interface/edit-channel.html'
EQUIPMENT_INTERFACES = 'equip-interface/equipInterfaces.html'

# Channel
NEW_CHANNEL = 'channels/new_channel.html'
EDIT_CHANNEL = 'channels/edit_channel.html'
AJAX_LIST_INTERFACES = 'ajax/equipments-interface.json'

# Interfaces
LIST_EQUIPMENT_INTERFACES = 'interfaces/list.html'
ADD_EQUIPMENT_INTERFACE = 'interfaces/new_interface.html'
EDIT_EQUIPMENT_INTERFACE = 'interfaces/edit_interface.html'
CONNECTIONS_INTERFACES = 'interfaces/connections.html'
NEW_CONNECTION = 'interfaces/new_connection.html'
NEW_INTERFACE_CONNECT_FORM = 'interfaces/connect-form-new.html'

# Equipment
EQUIPMENT_SEARCH_LIST = 'equipment/search-list.html'
EQUIPMENT_FORM = 'equipment/equip-form.html'
EQUIPMENT_MODELO = 'equipment/modelo.html'
EQUIPMENT_MARCA = 'equipment/marca.html'
EQUIPMENT_MODELO_AJAX = 'ajax/select-modelo.html'
EQUIPMENT_EDIT = 'equipment/equip-edit.html'
EQUIPMENT_MARCAMODELO_FORM = 'equipment/marca-modelo-form.html'
EQUIPMENT_VIEW_AJAX = 'equipment/view-real.html'

# Vlans
VLAN_SEARCH_LIST = 'vlan/search-list.html'
VLANS_DEETAIL = 'vlan/list-id.html'
VLAN_FORM = 'vlan/vlan-form.html'
VLAN_EDIT = 'vlan/vlan-edit.html'

# Network
NET_FORM = 'net/form.html'
NETIPV4 = 'net/netipv4.html'
NETIPV6 = 'net/netipv6.html'
NET4_EDIT = 'net/edit-net4.html'
NET6_EDIT = 'net/edit-net6.html'
NET_EVIP_OPTIONS = 'net/options.html'

# Option Vip
OPTIONVIP_LIST = 'option-vip/list.html'
OPTIONVIP_FORM = 'option-vip/form.html'

# Environment Vip
ENVIRONMENTVIP_LIST = 'environment-vip/list.html'
ENVIRONMENTVIP_FORM = 'environment-vip/form.html'
ENVIRONMENTVIP_EDIT = 'environment-vip/edit.html'
ENVIRONMENTVIP_CONF_FORM = 'environment-vip/conf.html'

# Group Equipment
GROUP_EQUIPMENT_LIST = 'group-equip/list.html'
GROUP_EQUIPMENT_FORM = 'group-equip/form.html'

# EQUIPMENT_GROUP
EQUIPMENT_GROUP_LIST = 'equip-group/list.html'
EQUIPMENT_GROUP_FORM = 'equip-group/form.html'
EQUIPMENT_USER_GROUP_FORM = 'equip-group/equip-user-group-form.html'

# Mail
MAIL_NEW_PASS = 'mail/mail.html'
MAIL_NEW_USER = 'mail/user.html'

# Errors
SEARCH_FORM_ERRORS = 'ajax/search-form-errors.html'

# IP
IP4 = 'ip/insert-ip4.html'
IP6 = 'ip/insert-ip6.html'
IP4EDIT = 'ip/edit-ip4.html'
IP6EDIT = 'ip/edit-ip6.html'

IP4ASSOC = 'ip/assoc-ip4.html'
IP6ASSOC = 'ip/assoc-ip6.html'

# Group User
GROUPUSER_LIST = 'group-user/list.html'
GROUPUSER_FORM = 'group-user/form.html'

# User
USER_LIST = 'users/list.html'

# User Group
USERGROUP_LIST = 'user-group/list.html'
USERGROUP_INDIVIDUAL_PERMS = 'user-group/list-individual-perms.html'
USERGROUP_EDIT_INDIVIDUAL_PERMS = 'user-group/edit-individual-perms.html'
USERGROUP_EDIT_GENERAL_PERMS = 'user-group/edit-general-perms.html'
USERGROUP_CREATE_INDIVIDUAL_PERMS = 'user-group/create-individual-perms.html'
USERGROUP_AJAX_OBJECTS = 'user-group/ajax/objects.json'
USERGROUP_AJAX_INDIVIDUAL_PERMISSIONS = 'user-group/ajax/individual-permissions.json'


# VRF
VRF_CREATE = 'vrf/form.html'
VRF_EDIT = 'vrf/edit.html'
VRF_LIST = 'vrf/list.html'

# ACL
ACL_FORM = 'acl/form.html'
ACL_APPLY_LIST = 'acl/apply.html'
ACL_APPLY_RESULT = 'acl/result.html'
ACL_TEMPLATE = 'acl/template_acl.html'
ACL_TEMPLATE_ADD_FORM = 'acl/template_add_form.html'
ACL_TEMPLATE_EDIT_FORM = 'acl/template_edit_form.html'

# VipRequest
VIPREQUEST_SEARCH_LIST = 'vip-request/search-list.html'
VIPREQUEST_VIEW_AJAX = 'vip-request/view-vip.html'
VIPREQUEST_FORM = 'vip-request/form.html'
VIPREQUEST_FORM_EXTERNAL = 'vip-request/form-external.html'
VIPREQUEST_EDIT = 'vip-request/edit.html'
VIPREQUEST_EDIT_EXTERNAL = 'vip-request/edit-external.html'
VIPREQUEST_TAB_POOLS = 'vip-request/tab-pools.html'
VIPREQUEST_TAB_VIP_EDIT = 'vip-request/tab-vip-edit.html'
VIPREQUEST_TOKEN = 'vip-request/token.json'
VIPREQUEST_POOL_FORM = 'vip-request/form_pool.html'
VIPREQUEST_POOL_OPTIONS = 'vip-request/options_pool.html'
VIPREQUEST_POOL_DATATABLE = 'vip-request/pool_datatable.json'

# AccessTypeRequest
ACCESSTYPE_FORM = 'access-type/form.html'

# NetworkTypeRequest
NETWORKTYPE_FORM = 'network-type/form.html'

# EquipementTypeRequest
EQUIPMENTTYPE_FORM = 'equipment-type/form.html'

# HealthCheckRequest
HEALTHCHECKEXPECT_FORM = 'healthcheck-expect/form.html'

# LDAP
LDAP_GROUP_LIST = 'ldap/group-list.html'
LDAP_GROUP_FORM = 'ldap/group-form.html'
LDAP_SUDOER_LIST = 'ldap/sudoer-list.html'
LDAP_SUDOER_FORM = 'ldap/sudoer-form.html'
LDAP_USER_LIST = 'ldap/user-list.html'
LDAP_USER_FORM = 'ldap/user-form.html'

# Filter
FILTER_LIST = 'filter/list.html'
FILTER_FORM = 'filter/form.html'
FILTER_EDIT = 'filter/edit.html'

# EventLog
LOG_SEARCH_LIST = 'event_log/search-list.html'

# Block rules
BLOCK_FORM = 'block-rules/form.html'
RULES_FORM = 'block-rules/rule_form.html'
TAB_BLOCK_FORM = 'block-rules/tab-blocks.html'
TAB_RULES_FORM = 'block-rules/tab-rules-form.html'
TAB_RULES = 'block-rules/tab-rules.html'

# Pool
POOL_LIST = 'pool/list.html'
POOL_LIST_NEW = 'pool/list_new.html'
POOL_FORM = 'pool/form.html'
POOL_MANAGE_TAB1 = 'pool/manage_tab1.html'
POOL_MANAGE_TAB2 = 'pool/manage_tab2.html'
POOL_MANAGE_TAB3 = 'pool/manage_tab3.html'
POOL_MANAGE_TAB4 = 'pool/manage_tab4.html'

AJAX_IPLIST_EQUIPMENT_DHCP_SERVER_HTML = 'ajax/request-ip-list-dhcp-server.html'
AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML = 'ajax/request-ip-list-real-server.html'
AJAX_IPLIST_EQUIPMENT_REAL_SERVER = 'ajax/request-ip-list-real-server.json'
POOL_DATATABLE = 'pool/datatable.json'
POOL_DATATABLE_NEW = 'pool/json/datatable_new.json'
POOL_SPM_DATATABLE = 'pool/spm_datatable.json'
POOL_REQVIP_DATATABLE = 'pool/reqvip_datatable.json'
POOL_MEMBER_ITEMS = 'pool/items.html'

# Rack
RACK_FORM = 'rack/form.html'
RACK_ADD = 'rack/newrack.html'
RACK_VIEW_AJAX = 'rack/view-rack.html'
RACK_EDIT = 'rack/edit.html'
#
RACK_DC_ADD = 'datacenter/newrack.html'
RACK_NEWEDIT = 'datacenter/editrack.html'
LISTDC = 'datacenter/datacenter.html'
DC_FORM = 'datacenter/newdc.html'
FABRIC = 'datacenter/fabric.html'
DCROOM_FORM = 'datacenter/newfabric.html'
DCROOM_ENV_FORM = 'datacenter/ambiente.html'
DCROOM_VLANS_FORM = 'datacenter/vlans.html'
DCROOM_BGP_FORM = 'datacenter/fabricconfig.html'

# System
VARIABLES_FORM = 'system/form.html'
VARIABLES_EDIT = 'system/edit.html'
VARIABLES_LIST = 'system/list.html'
