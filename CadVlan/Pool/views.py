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


import logging
from django.core.urlresolvers import reverse
from CadVlan.Util.Decorators import log, login_required, has_perm, access_external
from django.views.decorators.csrf import csrf_exempt
from CadVlan.templates import POOL_LIST, POOL_FORM, POOL_EDIT, POOL_SPM_DATATABLE, \
    POOL_DATATABLE, AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML, POOL_FORM_EDIT_NOT_CREATED, POOL_REQVIP_DATATABLE, POOL_MEMBER_ITEMS, \
    POOL_FORM_MANAGEMENT
from django.shortcuts import render_to_response, redirect, render
from django.http import HttpResponse
from django.template import loader
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.messages import request_vip_messages, healthcheck_messages
from CadVlan.messages import error_messages, pool_messages
from CadVlan.permissions import POOL_MANAGEMENT, VLAN_MANAGEMENT, \
    POOL_REMOVE_SCRIPT, POOL_CREATE_SCRIPT, POOL_ALTER_SCRIPT, HEALTH_CHECK_EXPECT
from CadVlan.forms import DeleteForm
from CadVlan.Pool.forms import PoolForm, SearchPoolForm, PoolFormEdit
from networkapiclient.Pagination import Pagination
from CadVlan.Util.utility import DataTablePaginator, get_param_in_request
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.shortcuts import render_message_json

logger = logging.getLogger(__name__)


def valid_reals(id_equips, ports, priorities, id_ips, default_port):

    lists = list()
    is_valid = True

    if int(default_port) > 65535:
        lists.append(request_vip_messages.get("invalid_port"))
        is_valid = False

    if id_equips is not None and id_ips is not None:

        invalid_ports_real = [
            i for i in ports if int(i) > 65535 or int(i) < 1]
        invalid_priority = [
            i for i in priorities if int(i) > 4294967295 or int(i) < 0]

        if invalid_priority:
            lists.append(request_vip_messages.get("invalid_priority"))
            is_valid = False

        if invalid_ports_real:
            lists.append(request_vip_messages.get("invalid_port"))
            is_valid = False

        if len(id_equips) != len(id_ips):
            lists.append(pool_messages.get("error_port_missing"))
            is_valid = False

        invalid_ips = 0

        for i in range(0, len(id_ips)):
            for j in range(0, len(id_ips)):
                if i == j:
                    pass
                elif ports[i] == ports[j] and id_ips[i] == id_ips[j]:
                    invalid_ips += 1

        if invalid_ips > 0:
            lists.append(pool_messages.get('error_same_port'))
            is_valid = False

    return is_valid, lists


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def list_all(request):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        environments = client.create_ambiente().list_all()

        delete_form = DeleteForm()

        search_form = SearchPoolForm(environments)

        return render_to_response(
            POOL_LIST,
            {
                'form': delete_form,
                'search_form': search_form
            },
            context_instance=RequestContext(request)
        )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('home')


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def datatable(request):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        environment_id = int(request.GET.get('pEnvironment'))

        columnIndexNameMap = {
            0: '',
            1: 'identifier',
            2: 'default_port',
            3: 'healthcheck__healthcheck_type',
            4: 'environment',
            5: 'pool_created',
            6: ''
        }

        dtp = DataTablePaginator(request, columnIndexNameMap)

        dtp.build_server_side_list()

        dtp.searchable_columns = [
            'identifier',
            'default_port',
            'pool_created',
            'healthcheck__healthcheck_type',
        ]

        pagination = Pagination(
            dtp.start_record,
            dtp.end_record,
            dtp.asorting_cols,
            dtp.searchable_columns,
            dtp.custom_search
        )

        pools = client.create_pool().list_all(environment_id, pagination)

        return dtp.build_response(
            pools["pools"],
            pools["total"],
            POOL_DATATABLE,
            request
        )

    except NetworkAPIClientError, e:
        logger.error(e.error)
        return render_message_json(e.error, messages.ERROR)


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def spm_datatable(request, id_server_pool):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        columnIndexNameMap = {
            0: '',
            1: 'identifier',
            2: 'ip',
            3: 'priority',
            4: 'port_real',
            6: 'pool_enabled',
            7: ''
        }

        dtp = DataTablePaginator(request, columnIndexNameMap)

        dtp.build_server_side_list()

        pagination = Pagination(
            dtp.start_record,
            dtp.end_record,
            dtp.asorting_cols,
            dtp.searchable_columns,
            dtp.custom_search
        )

        pools = client.create_pool().list_all_members_by_pool(
            id_server_pool,
            pagination
        )

        return dtp.build_response(
            pools["server_pool_members"],
            pools["total"],
            POOL_SPM_DATATABLE,
            request
        )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def reqvip_datatable(request, id_server_pool):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        columnIndexNameMap = {0: '', 1: 'id', 2: 'ip', 3: 'descricao_ipv4', 4: 'descricao_ipv6', 5: 'ambiente', 6: 'valido', 7: 'criado', 8: ''}

        dtp = DataTablePaginator(request, columnIndexNameMap)

        dtp.build_server_side_list()

        pagination = Pagination(
            dtp.start_record,
            dtp.end_record,
            dtp.asorting_cols,
            dtp.searchable_columns,
            dtp.custom_search
        )

        requisicoes_vip = client.create_pool().get_requisicoes_vip_by_pool(
            id_server_pool,
            pagination
        )

        return dtp.build_response(
            requisicoes_vip["requisicoes_vip"],
            requisicoes_vip["total"],
            POOL_REQVIP_DATATABLE,
            request
        )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

@log
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True}]
)
def add_form(request):

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all script_types from NetworkAPI
        enviroments = client.create_ambiente().list_all()
        optionsvips = client.create_option_vip().get_all()
        expect_string = client.create_ambiente().listar_healtchcheck_expect_distinct()

        # Format enviroments
        enviroments_choices = [('', '-')]
        for obj in enviroments['ambiente']:
            enviroments_choices.append((obj['id'], "%s - %s - %s" % (obj['divisao_dc_name'],
                                                                     obj['ambiente_logico_name'],
                                                                     obj['grupo_l3_name'])))

        # Filter options vip
        optionsvips_choices = [('', '-')]
        for obj in optionsvips['option_vip']:
            if obj['tipo_opcao'] == 'Balanceamento':
                optionsvips_choices.append((obj['nome_opcao_txt'], obj['nome_opcao_txt']))

        form = PoolForm(enviroments_choices, optionsvips_choices)
        action = reverse('pool.add.form')
        label_tab = u'Cadastro de Pool'
        pool_members = list()
        healthcheck_expect = ''
        healthcheck_request = ''

        if request.method == 'POST':
            # Data post list
            id_pool_member = request.POST.getlist('id_pool_member')
            id_equips = request.POST.getlist('id_equip')
            nome_equips = request.POST.getlist('equip')
            priorities = request.POST.getlist('priority')
            ports_reals = request.POST.getlist('ports_real_reals')
            weight = request.POST.getlist('weight')
            id_ips = request.POST.getlist('id_ip')
            ips = request.POST.getlist('ip')

            # Data post
            environment = request.POST.get('environment')
            healthcheck_type = request.POST.get('health_check')
            healthcheck_expect = request.POST.get('expect')
            healthcheck_request = request.POST.get('health_check_request')

            if healthcheck_type != 'HTTP' and healthcheck_type != 'HTTPS':
                healthcheck_expect = ''
                healthcheck_request = ''

            ip_list_full = list()

            # Rebuilding the reals list so we can display it again to the user
            # if it raises an error
            if len(ports_reals) > 0 and len(ips) > 0:
                for i in range(0, len(ports_reals)):
                    nome_equipamento = client.create_equipamento().listar_por_id(id_equips[i])
                    pool_members.append({'id': id_pool_member[i],
                                         'id_equip': id_equips[i],
                                         'nome_equipamento': nome_equipamento['equipamento']['nome'],
                                         'priority': priorities[i],
                                         'port_real': ports_reals[i],
                                         'weight': weight[i],
                                         'id_ip': id_ips[i],
                                         'ip': ips[i]
                                         })

                for i in range(len(ips)):
                    ip_list_full.append({'id': id_ips[i], 'ip': ips[i]})


            optionspool_choices = [('', '-')]
            if environment:
                optionspools = client.create_pool().get_opcoes_pool_by_ambiente(environment)
                for obj in optionspools['opcoes_pool']:
                    optionspool_choices.append((obj['opcao_pool']['description'], obj['opcao_pool']['description']))

            form = PoolForm(enviroments_choices, optionsvips_choices, optionspool_choices, request.POST)

            if form.is_valid():
                # Data form
                identifier = form.cleaned_data['identifier']
                default_port = form.cleaned_data['default_port']
                environment = form.cleaned_data['environment']
                balancing = form.cleaned_data['balancing']
                max_con = form.cleaned_data['max_con']

                is_valid, error_list = valid_reals(id_equips, ports_reals, priorities, id_ips, default_port)

                if is_valid:

                    client.create_pool().save(None, identifier, default_port, environment,
                                             balancing, healthcheck_type, healthcheck_expect,
                                             healthcheck_request, max_con, ip_list_full, nome_equips,
                                             id_equips, priorities, weight, ports_reals, id_pool_member)
                    messages.add_message(
                            request, messages.SUCCESS, pool_messages.get('success_insert'))

                    return redirect('pool.list')
                else:
                    messages.add_message(request, messages.ERROR, error_list[0])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_FORM, {'form': form, 'action': action, 'pool_members': pool_members,
                                          'expect_strings': expect_string, 'healthcheck_expect': healthcheck_expect,
                                          'healthcheck_request': healthcheck_request, 'label_tab': label_tab,
                                          'pool_created': False},
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True}]
)
def edit_form(request, id_server_pool):

    try:
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all script_types from NetworkAPI
        enviroments = client.create_ambiente().list_all()
        optionsvips = client.create_option_vip().get_all()
        expect_string = client.create_ambiente().listar_healtchcheck_expect_distinct()

        # Format enviroments
        enviroments_choices = [('', '-')]
        for obj in enviroments['ambiente']:
            enviroments_choices.append((obj['id'], "%s - %s - %s" % (obj['divisao_dc_name'],
                                                                     obj['ambiente_logico_name'],
                                                                     obj['grupo_l3_name'])))

        # Filter options vip
        optionsvips_choices = [('', '-')]
        for obj in optionsvips['option_vip']:
            if obj['tipo_opcao'] == 'Balanceamento':
                optionsvips_choices.append((obj['nome_opcao_txt'], obj['nome_opcao_txt']))

        action = reverse('pool.edit.form', args=[id_server_pool])
        label_tab = u'Edição de Pool'
        pool_members = list()
        healthcheck_expect = ''
        healthcheck_request = ''

        if request.method == 'POST':
                # Data post list
                id_pool_member = request.POST.getlist('id_pool_member')
                id_equips = request.POST.getlist('id_equip')
                nome_equips = request.POST.getlist('equip')
                priorities = request.POST.getlist('priority')
                ports_reals = request.POST.getlist('ports_real_reals')
                weight = request.POST.getlist('weight')
                id_ips = request.POST.getlist('id_ip')
                ips = request.POST.getlist('ip')
                pool_created = request.POST.getlist('pool_created')

                # Data post
                environment = request.POST.get('environment')
                healthcheck_type = request.POST.get('health_check')
                healthcheck_expect = request.POST.get('expect')
                healthcheck_request = request.POST.get('health_check_request')

                if healthcheck_type != 'HTTP' and healthcheck_type != 'HTTPS':
                    healthcheck_expect = ''
                    healthcheck_request = ''

                ip_list_full = list()

                # Rebuilding the reals list so we can display it again to the user
                # if it raises an error
                if len(ports_reals) > 0 and len(ips) > 0:
                    for i in range(0, len(ports_reals)):
                        nome_equipamento = client.create_equipamento().listar_por_id(id_equips[i])
                        pool_members.append({'id': id_pool_member[i],
                                             'id_equip': id_equips[i],
                                             'nome_equipamento': nome_equipamento['equipamento']['nome'],
                                             'priority': priorities[i],
                                             'port_real': ports_reals[i],
                                             'weight': weight[i],
                                             'id_ip': id_ips[i],
                                             'ip': ips[i]
                                             })

                    for i in range(len(ips)):
                        ip_list_full.append({'id': id_ips[i], 'ip': ips[i]})


                optionspool_choices = [('', '-')]
                if environment:
                    optionspools = client.create_pool().get_opcoes_pool_by_ambiente(environment)
                    for obj in optionspools['opcoes_pool']:
                        optionspool_choices.append((obj['opcao_pool']['description'], obj['opcao_pool']['description']))

                form = PoolForm(enviroments_choices, optionsvips_choices, optionspool_choices, request.POST)

                if form.is_valid():
                    # Data form
                    id = form.cleaned_data['id']
                    identifier = form.cleaned_data['identifier']
                    default_port = form.cleaned_data['default_port']
                    environment = form.cleaned_data['environment']
                    balancing = form.cleaned_data['balancing']
                    max_con = form.cleaned_data['max_con']

                    is_valid, error_list = valid_reals(id_equips, ports_reals, priorities, id_ips, default_port)

                    if is_valid:
                        client.create_pool().save(id, identifier, default_port, environment,
                                                 balancing, healthcheck_type, healthcheck_expect,
                                                 healthcheck_request, max_con, ip_list_full, nome_equips,
                                                 id_equips, priorities, weight, ports_reals, id_pool_member)

                        messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))

                        return redirect(action)
                    else:
                        messages.add_message(request, messages.ERROR, error_list[0])
        else:
            pool = client.create_pool().get_by_pk(id_server_pool)

            pool_created = pool['server_pool']['pool_created']

            optionspool_choices = [('', '-')]
            if pool['server_pool']['environment']:
                optionspools = client.create_pool().get_opcoes_pool_by_ambiente(pool['server_pool']['environment']['id'])
                for obj in optionspools['opcoes_pool']:
                    optionspool_choices.append((obj['opcao_pool']['description'], obj['opcao_pool']['description']))

            environment = pool['server_pool']['environment']['id'] if pool['server_pool']['environment'] else None

            healthcheck_expect = pool['server_pool']['healthcheck']['healthcheck_expect'] \
                if pool['server_pool']['healthcheck'] else ''

            healthcheck_request = pool['server_pool']['healthcheck']['healthcheck_request'] \
                if pool['server_pool']['healthcheck'] else ''

            health_check = pool['server_pool']['healthcheck']['healthcheck_type'] \
                if pool['server_pool']['healthcheck'] else None

            initial_pool = {
                'id': pool['server_pool']['id'],
                'identifier': pool['server_pool']['identifier'],
                'default_port': pool['server_pool']['default_port'],
                'environment': environment,
                'balancing': pool['server_pool']['lb_method'],
                'health_check': health_check,
                'max_con': pool['server_pool']['default_limit'],
            }

            if len(pool['server_pool_members']) > 0:
                for obj in pool['server_pool_members']:
                    equip = client.create_pool().get_equip_by_ip(obj['ip']['id'])

                    ip = ''
                    if obj['ip']:
                        ip = obj['ip']['ip_formated']
                    elif obj['ipv6']:
                        ip = obj['ipv6']['ip_formated']

                    pool_members.append({'id': obj['id'], 'id_equip': equip['equipamento']['id'],
                                         'nome_equipamento': equip['equipamento']['nome'], 'priority': obj['priority'],
                                         'port_real': obj['port_real'], 'weight': obj['weight'], 'id_ip': obj['ip']['id'],
                                         'ip': ip})

            form = PoolForm(enviroments_choices, optionsvips_choices, optionspool_choices, initial=initial_pool)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    template = POOL_FORM if not pool_created else POOL_FORM_MANAGEMENT

    return render_to_response(template, {'form': form, 'action': action, 'pool_members': pool_members,
                                      'expect_strings': expect_string, 'healthcheck_expect': healthcheck_expect,
                                      'healthcheck_request': healthcheck_request, 'label_tab': label_tab,
                                      'pool_created': pool_created, 'id_server_pool': id_server_pool},
                              context_instance=RequestContext(request))


# @log
# @login_required
# @has_perm([
#     {"permission": POOL_MANAGEMENT, "write": True},
#     {"permission": POOL_ALTER_SCRIPT, "write": True}]
# )
# def edit_form(request, id_server_pool):
#
#     try:
#
#         server_pool = dict()
#         server_pool_members = dict()
#         action = reverse('pool.edit.form', args=[id_server_pool])
#         # Get user
#         auth = AuthSession(request.session)
#         client = auth.get_clientFactory()
#
#         # Get pool infos
#         pool = client.create_pool().get_by_pk(id_server_pool)
#         expect_string_list = client.create_ambiente().listar_healtchcheck_expect_distinct()
#
#         server_pool = pool['server_pool']
#         server_pool_members = pool['server_pool_members']
#
#         if server_pool['environment'] is not None:
#             ambiente = client.create_ambiente().buscar_por_id(server_pool['environment']['id'])
#             nome_ambiente = ambiente['ambiente']['nome_divisao'] + " - " + ambiente['ambiente']['nome_ambiente_logico'] + " - " + ambiente['ambiente']['nome_grupo_l3']
#         else:
#             ambiente = None
#             nome_ambiente = '-'
#
#
#         healthcheck = server_pool['healthcheck']
#
#         for spm in server_pool_members:
#             nome_equipamento = client.create_pool().get_equip_by_ip(spm['ip']['id'])
#             spm.update({'equipamento': nome_equipamento})
#             ip_formatado = ""
#
#             if spm['ip'] is not None:
#                 ip_formatado = "{}.{}.{}.{}".format(spm['ip']['oct1'], spm['ip']['oct2'], spm['ip']['oct3'], spm['ip']['oct4'])
#             elif spm['ipv6'] is not None:
#                 ip_formatado = "{}:{}:{}:{}:{}:{}:{}:{}".format(spm['ipv6']['bloco1'],
#                                                                 spm['ipv6']['bloco2'],
#                                                                 spm['ipv6']['bloco3'],
#                                                                 spm['ipv6']['bloco4'],
#                                                                 spm['ipv6']['bloco5'],
#                                                                 spm['ipv6']['bloco6'],
#                                                                 spm['ipv6']['bloco7'],
#                                                                 spm['ipv6']['bloco8'],
#                                                                 )
#             spm.update({'ip_formatado': ip_formatado})
#
#
#         env_list = client.create_ambiente().list_all()
#         opvip_list = client.create_option_vip().get_all()
#
#         env_choices = [('', '-')]
#         for env in env_list['ambiente']:
#             env_choices.append((env['id'],
#                                 "%s - %s - %s" % (env['divisao_dc_name'],
#                                                   env['ambiente_logico_name'],
#                                                   env['grupo_l3_name'])))
#
#         choices_opvip = [('', '-')]
#         for opvip in opvip_list['option_vip']:
#             # filtering to only Balanceamento
#             if opvip['tipo_opcao'] == 'Balanceamento':
#                 choices_opvip.append((opvip['nome_opcao_txt'], opvip['nome_opcao_txt']))
#
#         # If form was submited
#         if request.method == 'POST':
#
#             form = PoolForm(env_choices, choices_opvip, request.POST)
#             formEdit = PoolFormEdit(choices_opvip, request.POST)
#
#             #form_real = RequestVipFormReal(request.POST)
#
#             if formEdit.is_valid():
#
#                 id_ips = request.POST.getlist('id_ip')
#                 ips = request.POST.getlist('ip')
#
#                 ip_list_full = list()
#
#                 for i in range(len(ips)):
#                     ip_list_full.append({'id': id_ips[i], 'ip': ips[i]})
#
#                 # Data
#                 default_port = formEdit.cleaned_data['default_port']
#                 balancing = formEdit.cleaned_data['balancing']
#                 maxcom = formEdit.cleaned_data['maxcom']
#
#                 id_equips = request.POST.getlist('id_equip')
#                 priorities = request.POST.getlist('priority')
#                 nome_equips = request.POST.getlist('equip')
#                 ports_reals = request.POST.getlist('ports_real_reals')
#                 weight = request.POST.getlist('weight')
#
#                 is_valid, error_list = valid_reals(id_equips, ports_reals, priorities, id_ips, default_port)
#
#                 if is_valid:
#
#                     healthcheck_type = request.POST.get('healthcheck')
#                     healthcheck_expect = request.POST.get('expect')
#                     healthcheck_request = request.POST.get('healthcheck_request')
#
#                     if healthcheck_type != 'HTTP' and healthcheck_type != 'HTTPS':
#                         healthcheck_expect = ''
#                         healthcheck_request = ''
#
#                     client.create_pool().update(id_server_pool, default_port,
#                                                  balancing, healthcheck_type, healthcheck_expect,
#                                                  healthcheck_request,
#                                                  server_pool['healthcheck']['id'] if server_pool['healthcheck'] else None,
#                                                  maxcom, ip_list_full, nome_equips,
#                                                  id_equips, priorities, weight, ports_reals)
#                     messages.add_message(
#                             request, messages.SUCCESS, pool_messages.get('success_update'))
#
#                     return redirect('pool.edit.form', id_server_pool)
#                 else:
#                     messages.add_message(
#                             request, messages.ERROR, error_list[0])
#         else:
#
#             for spm in server_pool_members:
#                 nome_equipamento = client.create_pool().get_equip_by_ip(spm['ip']['id'])
#                 spm.update({'equipamento': nome_equipamento})
#
#             poolform_initial = {
#                 'identifier': server_pool.get('identifier'),
#                 'default_port': server_pool.get('default_port'),
#                 'environment': server_pool.get('environment') and server_pool['environment']['id'],
#                 'balancing': server_pool.get('lb_method'),
#             }
#
#             form = PoolForm(
#                 env_choices,
#                 choices_opvip,
#                 initial=poolform_initial
#             )
#
#
#     except NetworkAPIClientError, e:
#         logger.error(e)
#         messages.add_message(request, messages.ERROR, e)
#
#     if server_pool.get('pool_created'):
#         url = POOL_EDIT
#     else:
#         url = POOL_FORM_EDIT_NOT_CREATED
#
#     context_attrs = {
#         'form': form,
#         'form_real': form,
#         'action': action,
#         'reals': server_pool_members,
#         'healthcheck': healthcheck,
#         'id_server_pool': id_server_pool,
#         'expect_strings': expect_string_list,
#         'selection_form': DeleteForm(),
#         'nome_ambiente': nome_ambiente,
#         'id_environment': server_pool.get('environment') and server_pool['environment']['id']
#     }
#
#     return render_to_response(
#         url,
#         context_attrs,
#         context_instance=RequestContext(request)
#     )


@csrf_exempt
@access_external()
@log
def ajax_modal_ip_real_server_external(request, form_acess, client):
    return modal_ip_list_real(request, client)


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True, "write": True}])
def ajax_modal_ip_real_server(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return modal_ip_list_real(request, client_api)


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True, "write": True}])
def modal_ip_list_real(request, client_api):

    lists = dict()
    lists['msg'] = ''
    lists['ips'] = ''
    ips = None
    equip = None
    status_code = None

    try:

        ambiente = get_param_in_request(request, 'id_environment')
        equip_name = get_param_in_request(request, 'equip_name')

        # Valid Equipament
        equip = client_api.create_equipamento().listar_por_nome(equip_name).get("equipamento")
        ips = client_api.create_equipamento().get_ips_by_equipment_and_environment(equip_name, ambiente)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500

    if ips['list_ipv4'] and type(ips['list_ipv4']) is not type([]):
        ips['list_ipv4'] = [ips['list_ipv4']]

    if ips['list_ipv6'] and type(ips['list_ipv6']) is not type([]):
        ips['list_ipv6'] = [ips['list_ipv6']]

    lists['ips'] = ips
    lists['equip'] = equip

    return HttpResponse(
        loader.render_to_string(
            AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML,
            lists,
            context_instance=RequestContext(request)
        ), status=status_code
    )




@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def ajax_get_opcoes_pool_by_ambiente(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return get_opcoes_pool_by_ambiente(request, client_api)

@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def get_opcoes_pool_by_ambiente(request, client_api):

    import json

    lists = dict()
    lists['opcoes_pool'] = ''

    try:

        ambiente = get_param_in_request(request, 'id_environment')
        opcoes_pool = client_api.create_pool().get_opcoes_pool_by_ambiente(ambiente)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500


    return HttpResponse(json.dumps(opcoes_pool['opcoes_pool']), content_type='application/json')



@log
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True}]
)
def delete(request):
    """
        Delete Pool Into Database
    """
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = DeleteForm(request.POST)

        if form.is_valid():

            ids = split_to_array(form.cleaned_data['ids'])

            client.create_pool().delete(ids)

            messages.add_message(
                request,
                messages.SUCCESS,
                pool_messages.get('success_delete')
            )

        else:
            messages.add_message(
                request,
                messages.ERROR,
                error_messages.get("select_one")
            )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('pool.list')


@log
@login_required
@has_perm([{"permission": POOL_REMOVE_SCRIPT, "write": True}])
def remove(request):
    """
        Remove Pool Running Script and Update to Not Created
    """
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = DeleteForm(request.POST)

        if form.is_valid():

            ids = split_to_array(form.cleaned_data['ids'])

            client.create_pool().remove(ids)

            messages.add_message(
                request,
                messages.SUCCESS,
                pool_messages.get('success_remove')
            )

        else:
            messages.add_message(
                request,
                messages.ERROR,
                error_messages.get("select_one")
            )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('pool.list')


@log
@login_required
@has_perm([{"permission": POOL_CREATE_SCRIPT, "write": True}])
def create(request):
    """
        Remove Pool Running Script and Update to Not Created
    """
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = DeleteForm(request.POST)

        if form.is_valid():

            ids = split_to_array(form.cleaned_data['ids'])

            client.create_pool().create(ids)

            messages.add_message(
                request,
                messages.SUCCESS,
                pool_messages.get('success_create')
            )

        else:
            messages.add_message(
                request,
                messages.ERROR,
                error_messages.get("select_one")
            )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('pool.list')


@log
@login_required
@has_perm([{"permission": POOL_ALTER_SCRIPT, "write": True}])
def enable(request, id_server_pool):
    """
        Enable Pool Member Running Script
    """
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = DeleteForm(request.POST)

        if form.is_valid():

            ids = split_to_array(form.cleaned_data['ids'])

            client.create_pool().enable(ids)

            messages.add_message(
                request,
                messages.SUCCESS,
                pool_messages.get('success_enable')
            )

        else:
            messages.add_message(
                request,
                messages.ERROR,
                error_messages.get("select_one")
            )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('pool.edit.form', id_server_pool)


@log
@login_required
@has_perm([{"permission": POOL_ALTER_SCRIPT, "write": True}])
def disable(request, id_server_pool):
    """
        Disable Pool Member Running Script
    """
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = DeleteForm(request.POST)

        if form.is_valid():

            ids = split_to_array(form.cleaned_data['ids'])

            client.create_pool().disable(ids)

            messages.add_message(
                request,
                messages.SUCCESS,
                pool_messages.get('success_disable')
            )

        else:
            messages.add_message(
                request,
                messages.ERROR,
                error_messages.get("select_one")
            )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('pool.edit.form', id_server_pool)


@log
@login_required
@has_perm([{'permission': HEALTH_CHECK_EXPECT, "write": True}])
def add_healthcheck_expect(request):

    import json

    lists = dict()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        if request.method == 'GET':

            expect_string = request.GET.get("expect_string")
            id_environment = request.GET.get("id_environment")

            if expect_string != '':

                client.create_ambiente().add_healthcheck_expect(
                    id_ambiente=id_environment, expect_string=expect_string, match_list=expect_string)

                lists['expect_string'] = expect_string
                lists['mensagem'] = healthcheck_messages.get('success_create')

    except NetworkAPIClientError, e:
        logger.error(e)
        lists['mensagem'] = healthcheck_messages.get('error_create')
        messages.add_message(request, messages.ERROR, e)

    return HttpResponse(json.dumps(lists), content_type='application/json')


@log
@login_required
@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "write": True}, ])
def pool_member_items(request):

    try:

        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()

        pool_id = request.GET.get('pool_id')
        pool_data = client_api.create_pool().get_by_pk(pool_id)

        return render(
            request,
            POOL_MEMBER_ITEMS,
            pool_data
        )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
