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


def populate_expectstring_choices(client):
    expectstring_choices = client.create_ambiente().listar_healtchcheck_expect_distinct()
    expectstring_choices['healthcheck_expect'].insert(0, ('', '-'))

    return expectstring_choices


def populate_enviroments_choices(client):
    enviroments = client.create_pool().list_all_environment_related_environment_vip()

    enviroments_choices = [('', '-')]

    # Format enviroments
    for obj in enviroments:
        enviroments_choices.append((obj['id'], "%s - %s - %s" % (obj['divisao_dc_name'],
                                                                 obj['ambiente_logico_name'],
                                                                 obj['grupo_l3_name'])))

    return enviroments_choices


def populate_optionsvips_choices(client, tips='Balanceamento'):
    optionsvips = client.create_option_vip().get_all()

    optionsvips_choices = [('', '-')]
    for obj in optionsvips['option_vip']:
        if obj['tipo_opcao'] == tips:
            optionsvips_choices.append((obj['nome_opcao_txt'], obj['nome_opcao_txt']))

    return optionsvips_choices


def populate_servicedownaction_choices(client, tips='ServiceDownAction'):
    optionspool = client.create_option_pool().get_all_option_pool(option_type='ServiceDownAction')

    servicedownaction_choices = [('', '-')]
    for obj in optionspool:
        servicedownaction_choices.append((obj['id'], obj['name']))

    return servicedownaction_choices


def find_servicedownaction_id(client, option_name):
    optionspool = client.create_option_pool().get_all_option_pool(option_type='ServiceDownAction')
    for obj in optionspool:
        if obj['name'] == option_name:
            return obj['id']


def find_servicedownaction_object(client, option_name=None, id=None):
    optionspool = client.create_option_pool().get_all_option_pool(option_type='ServiceDownAction')
    if id:
        for obj in optionspool:
            if obj['id'] == id:
                return obj['name']
    for obj in optionspool:
        if obj['name'] == option_name:
            return obj


def populate_optionspool_choices(client, environment):
    optionspool_choices = [('', '-')]
    if environment:
        optionspools = client.create_pool().get_opcoes_pool_by_ambiente(environment)
        for obj in optionspools['opcoes_pool']:
            optionspool_choices.append((obj['opcao_pool']['description'], obj['opcao_pool']['description']))

    return optionspool_choices


def populate_pool_members_by_lists(client, members):
    pool_members = []
    ip_list_full = []
    if len(members.get("ports_reals")) > 0 and len(members.get("ips")) > 0:
        for i in range(0, len(members.get("ports_reals"))):
            pool_members.append({
                'id': members.get("id_pool_member")[i],
                'id_equip': members.get("id_equips")[i],
                'nome_equipamento': members.get("name_equips")[i],
                'priority': members.get("priorities")[i],
                'port_real': members.get("ports_reals")[i],
                'weight': members.get("weight")[i],
                'id_ip': members.get("id_ips")[i],
                'ip': members.get("ips")[i]
            })

            ip_list_full.append({'id': members.get("id_ips")[i], 'ip': members.get("ips")[i]})

    return pool_members, ip_list_full


def populate_pool_members_by_obj(server_pool_members):
    pool_members = []

    for obj in server_pool_members:

        ip = obj['ip'] if obj['ip'] else obj['ipv6']
        pool_members.append({'id': obj['id'],
                             'id_equip': obj['equipment']['id'],
                             'nome_equipamento': obj['equipment']['name'],
                             'priority': obj['priority'],
                             'port_real': obj['port_real'],
                             'weight': obj['weight'],
                             'id_ip': ip['id'] if ip else '',
                             'ip': ip['ip_formated'] if ip else ''})

    return pool_members


def format_healthcheck(request):

    healthcheck = dict()
    healthcheck["identifier"] = ""
    healthcheck["healthcheck_type"] = str(request.POST.get('healthcheck'))
    if healthcheck["healthcheck_type"] != 'HTTP' and healthcheck["healthcheck_type"] != 'HTTPS':
        healthcheck["healthcheck_expect"] = ''
        healthcheck["healthcheck_request"] = ''
    else:
        healthcheck["healthcheck_request"] = request.POST.get('healthcheck_request')
        healthcheck["healthcheck_expect"] = request.POST.get('healthcheck_expect')
    healthcheck_destination = request.POST.get('healthcheck_destination')
    healthcheck["destination"] = ("*:%s" % healthcheck_destination) if healthcheck_destination else '*:*'

    return healthcheck


def format_servicedownaction(client, form):

    servicedownaction = dict()
    servicedownaction["id"] = int(form.cleaned_data['servicedownaction'])
    servicedownaction["name"] = str(find_servicedownaction_object(client, id=servicedownaction['id']))

    return servicedownaction


def format_server_pool_members(request, limit=0):

    pool_members = []
    equips = request.POST.getlist('id_equip')
    for i in range(0, len(equips)):
        server_pool_members = dict()
        server_pool_members["id"] = int(request.POST.getlist('id_pool_member')[i]) \
            if request.POST.getlist('id_pool_member')[i] else None
        server_pool_members["identifier"] = str(request.POST.getlist('equip')[i])
        server_pool_members["priority"] = int(request.POST.getlist('priority')[i])
        server_pool_members["equipment"] = _format_equipments(request, i)
        server_pool_members["weight"] = int(request.POST.getlist('weight')[i])
        server_pool_members["limit"] = limit
        server_pool_members["port_real"] = int(request.POST.getlist('ports_real_reals')[i])
        server_pool_members["member_status"] = 0
        v4, v6 = _format_ips(request, i)
        server_pool_members["ip"] = v4
        server_pool_members["ipv6"] = v6
        pool_members.append(server_pool_members)

    return pool_members


def _format_equipments(request, i):

    equipments = dict()
    equipments["id"] = int(request.POST.getlist('id_equip')[i])
    equipments["nome"] = str(request.POST.getlist('equip')[i])

    return equipments


def _format_ips(request, i):

    ips = dict()
    ips["id"] = int(request.POST.getlist('id_ip')[i])
    ips["ip_formated"] = str(request.POST.getlist('ip')[i])

    v4 = ips if "." in ips['ip_formated'] else None
    v6 = ips if ":" in ips['ip_formated'] else None

    return v4, v6
