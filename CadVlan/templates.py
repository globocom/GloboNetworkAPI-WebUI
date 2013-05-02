# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''


LOGIN = 'login.html'
HOME = 'home.html'

VERSION_HTML = 'version.html'

# Ajax
AJAX_AUTOCOMPLETE_LIST = 'ajax/autocomplete-list.json'
AJAX_VLAN_AUTOCOMPLETE = 'ajax/vlan-autocomplete-list.json'
AJAX_VLAN_LIST = 'ajax/vlan-list.json'
AJAX_EQUIP_LIST = 'ajax/equip-list.json'
AJAX_VIPREQUEST_LIST = 'ajax/vip-list.json'
AJAX_LOG_LIST = 'ajax/log-list.json'
AJAX_NEW_PASS = 'ajax/newpass.html'
AJAX_SUGGEST_NAME = 'ajax/suggest-name.html'
VIPREQUEST_VIEW = 'ajax/view-vip.html'
AJAX_VIPREQUEST_CLIENT = 'ajax/request-vip-client.html'
AJAX_VIPREQUEST_ENVIRONMENT = 'ajax/request-vip-environment.html'
AJAX_VIPREQUEST_OPTIONS = 'ajax/request-vip-options.json'
AJAX_VIPREQUEST_HEALTHCHECK = 'ajax/request-vip-add-healthcheck.json'
AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER = 'ajax/request-vip-model-ip-real-server.json'
AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER_HTML = 'ajax/request-vip-model-ip-real-server.html'
AJAX_LDAP_RESET_PASSWORD = 'ajax/ldap-reset-password.html'
JSON_ERROR = "error.json"
TOKEN_INVALID = "token_invalid.html"


AJAX_LDAP_USERS_BY_GROUP = 'ajax/select-ldap-user.html'
AJAX_LDAP_USER_POP_NAME_MAIL = 'ajax/pop_ldap_user_mail.json'


# Script
SCRIPT_LIST = 'script/list.html'
SCRIPT_FORM = 'script/form.html'

# Script Type
SCRIPTTYPE_LIST = 'script-type/list.html'
SCRIPTTYPE_FORM = 'script-type/form.html'

#Environment
ENVIRONMENT_LIST = 'environment/list.html'
ENVIRONMENT_FORM = 'environment/form.html'

#Equipment Access
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

# Equipment
EQUIPMENT_SEARCH_LIST = 'equipment/search-list.html'
EQUIPMENT_FORM = 'equipment/equip-form.html'
EQUIPMENT_MODELO = 'equipment/modelo.html'
EQUIPMENT_MARCA = 'equipment/marca.html'
EQUIPMENT_MODELO_AJAX = 'ajax/select-modelo.html'
EQUIPMENT_EDIT = 'equipment/equip-edit.html'
EQUIPMENT_MARCAMODELO_FORM = 'equipment/marca-modelo-form.html'

#Vlans
VLAN_SEARCH_LIST = 'vlan/search-list.html'
VLANS_DEETAIL = 'vlan/list-id.html'
VLANS_DEETAIL = 'vlan/list-id.html'
VLAN_FORM = 'vlan/vlan-form.html'
VLAN_EDIT = 'vlan/vlan-edit.html'

#Network
NET_FORM = 'net/form.html'
NETIPV4 = 'net/netipv4.html'
NETIPV6 = 'net/netipv6.html'
NET4_EDIT = 'net/edit-net4.html'
NET6_EDIT = 'net/edit-net6.html'

# Option Vip
OPTIONVIP_LIST = 'option-vip/list.html'
OPTIONVIP_FORM = 'option-vip/form.html'

# Environment Vip
ENVIRONMENTVIP_LIST = 'environment-vip/list.html'
ENVIRONMENTVIP_FORM = 'environment-vip/form.html'
ENVIRONMENTVIP_EDIT = 'environment-vip/edit.html'

# Group Equipment
GROUP_EQUIPMENT_LIST = 'group-equip/list.html'
GROUP_EQUIPMENT_FORM = 'group-equip/form.html'

# EQUIPMENT_GROUP
EQUIPMENT_GROUP_LIST = 'equip-group/list.html'
EQUIPMENT_GROUP_FORM = 'equip-group/form.html'
EQUIPMENT_USER_GROUP_FORM = 'equip-group/equip-user-group-form.html'

#Mail
MAIL_NEW_PASS = 'mail/mail.html'
MAIL_NEW_USER = 'mail/user.html'

#Errors
SEARCH_FORM_ERRORS = 'ajax/search-form-errors.html'

#IP
IP4 = 'ip/insert-ip4.html'
IP6 = 'ip/insert-ip6.html'
IP4EDIT = 'ip/edit-ip4.html'
IP6EDIT = 'ip/edit-ip6.html'

IP4ASSOC = 'ip/assoc-ip4.html'
IP6ASSOC = 'ip/assoc-ip6.html'

#Group User
GROUPUSER_LIST = 'group-user/list.html'
GROUPUSER_FORM = 'group-user/form.html'

#User
USER_LIST = 'users/list.html'

# User Group
USERGROUP_LIST = 'user-group/list.html'

# ACL
ACL_FORM = 'acl/form.html'
ACL_APPLY_LIST = 'acl/apply.html'
ACL_APPLY_RESULT = 'acl/result.html'

# VipRequest 
VIPREQUEST_SEARCH_LIST = 'vip-request/search-list.html'
VIPREQUEST_VIEW_AJAX = 'vip-request/view-vip.html'
VIPREQUEST_FORM = 'vip-request/form.html'
VIPREQUEST_FORM_EXTERNAL = 'vip-request/form-external.html'
VIPREQUEST_EDIT = 'vip-request/edit.html'
VIPREQUEST_EDIT_EXTERNAL = 'vip-request/edit-external.html'
VIPREQUEST_TAB_REAL_SERVER = 'vip-request/tab-real-server.html'
VIPREQUEST_TAB_REAL_SERVER_STATUS = 'vip-request/tab-real-server-status.html'
VIPREQUEST_TAB_HEALTHCHECK = 'vip-request/tab-healthcheck.html'
VIPREQUEST_TAB_MAXCON = 'vip-request/tab-maxcon.html'
VIPREQUEST_TOKEN = 'vip-request/token.json'

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
LDAP_USER_FORM = 'ldap/user-form.html'

# Filter
FILTER_LIST = 'filter/list.html'
FILTER_FORM = 'filter/form.html'
FILTER_EDIT = 'filter/edit.html'

# EventLog
LOG_SEARCH_LIST = 'event_log/search-list.html'
