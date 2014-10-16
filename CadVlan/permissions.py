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


ADMINISTRATION = 'administrativa'
USER_ADMINISTRATION = 'administracao_usuarios'
ENVIRONMENT_MANAGEMENT = 'cadastro_de_ambiente'
NETWORK_TYPE_MANAGEMENT = 'cadastro_de_tipo_rede'
SCRIPT_MANAGEMENT = 'cadastro_de_roteiro'
POOL_MANAGEMENT = 'cadastro_de_pool'
BRAND_MANAGEMENT = 'cadastro_de_marca'
EQUIPMENT_MANAGEMENT = 'cadastro_de_equipamentos'
EQUIPMENT_GROUP_MANAGEMENT = 'cadastro_de_grupos_equipamentos'
VM_MANAGEMENT = 'cadastro_de_vm'
VLAN_MANAGEMENT = 'cadastro_de_vlans'
VLAN_CREATE_SCRIPT = 'script_criacao_vlan'
VLAN_ALTER_SCRIPT = 'script_alterar_vlan'
VLAN_ALLOCATION = 'alocar_vlan'
TELCO_CONFIGURATION = 'configuracao_telco'
HEALTH_CHECK_EXPECT = 'healthcheck_expect'
IPS = 'ips'
VIPS_REQUEST = 'requisicao_vips'
VIP_ALTER_SCRIPT = 'script_alterar_vip'
VIP_CREATE_SCRIPT = 'script_criacao_vip'
VIP_REMOVE_SCRIPT = 'script_remover_vip'
VIP_VALIDATION = 'validar_vip'
VIP_ADMINISTRATION = 'administracao_vips'
ACL_VLAN_VALIDATION = 'validar_acl_vlans'
ENVIRONMENT_VIP = 'ambiente_vip'
OPTION_VIP = 'opcao_vip'
AUTHENTICATE = 'authenticate'
ACCESS_TYPE_MANAGEMENT = 'cadastro_de_tipo_acesso'
AUDIT_LOG = 'audit_logs'
ACL_APPLY = 'aplicar_acl'
POOL_MANAGEMENT = 'cadastro_de_pool'
"""
Pool Permissions
"""
POOL_CREATE_SCRIPT = 'script_criacao_pool'
POOL_REMOVE_SCRIPT = 'script_remover_pool'
POOL_ALTER_SCRIPT = 'script_alterar_pool'

PERMISSIONS = {
    'ADMINISTRATION': ADMINISTRATION,
    'USER_ADMINISTRATION': USER_ADMINISTRATION,
    'ENVIRONMENT_MANAGEMENT': ENVIRONMENT_MANAGEMENT,
    'NETWORK_TYPE_MANAGEMENT': NETWORK_TYPE_MANAGEMENT,
    'SCRIPT_MANAGEMENT': SCRIPT_MANAGEMENT,
    'POOL_MANAGEMENT': POOL_MANAGEMENT,
    'POOL_CREATE_SCRIPT': POOL_CREATE_SCRIPT,
    'POOL_REMOVE_SCRIPT': POOL_REMOVE_SCRIPT,
    'POOL_ALTER_SCRIPT': POOL_ALTER_SCRIPT,
    'BRAND_MANAGEMENT': BRAND_MANAGEMENT,
    'EQUIPMENT_MANAGEMENT': EQUIPMENT_MANAGEMENT,
    'EQUIPMENT_GROUP_MANAGEMENT': EQUIPMENT_GROUP_MANAGEMENT,
    'VM_MANAGEMENT': VM_MANAGEMENT,
    'VLAN_MANAGEMENT': VLAN_MANAGEMENT,
    'VLAN_CREATE_SCRIPT': VLAN_CREATE_SCRIPT,
    'VLAN_ALTER_SCRIPT': VLAN_ALTER_SCRIPT,
    'VLAN_ALLOCATION': VLAN_ALLOCATION,
    'TELCO_CONFIGURATION': TELCO_CONFIGURATION,
    'HEALTH_CHECK_EXPECT': HEALTH_CHECK_EXPECT,
    'IPS': IPS,
    'VIPS_REQUEST': VIPS_REQUEST,
    'VIP_ALTER_SCRIPT': VIP_ALTER_SCRIPT,
    'VIP_CREATE_SCRIPT': VIP_CREATE_SCRIPT,
    'VIP_VALIDATION': VIP_VALIDATION,
    'VIP_ADMINISTRATION': VIP_ADMINISTRATION,
    'ACL_VLAN_VALIDATION': ACL_VLAN_VALIDATION,
    'ENVIRONMENT_VIP': ENVIRONMENT_VIP,
    'OPTION_VIP': OPTION_VIP,
    'AUTHENTICATE': AUTHENTICATE,
    'ACCESS_TYPE_MANAGEMENT': ACCESS_TYPE_MANAGEMENT,
    'AUDIT_LOG': AUDIT_LOG,
    'VIP_REMOVE_SCRIPT': VIP_REMOVE_SCRIPT,
    'ACL_APPLY': ACL_APPLY,
}
