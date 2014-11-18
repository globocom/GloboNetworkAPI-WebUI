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

import json
import logging
from django.core.urlresolvers import reverse
from CadVlan.Pool.facade import populate_enviroments_choices, populate_optionsvips_choices, \
    populate_expectstring_choices, populate_optionspool_choices, populate_pool_members_by_lists, \
    populate_pool_members_by_obj
from CadVlan.Util.Decorators import log, login_required, has_perm, access_external
from django.views.decorators.csrf import csrf_exempt
from CadVlan.templates import POOL_LIST, POOL_FORM, POOL_SPM_DATATABLE, \
    POOL_DATATABLE, AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML, POOL_REQVIP_DATATABLE, POOL_MEMBER_ITEMS, POOL_MANAGE_TAB1, \
    POOL_MANAGE_TAB2, POOL_MANAGE_TAB3, POOL_MANAGE_TAB4
from django.shortcuts import render_to_response, redirect, render
from django.http import HttpResponse
from django.template import loader
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.messages import healthcheck_messages
from CadVlan.messages import error_messages, pool_messages
from CadVlan.permissions import POOL_MANAGEMENT, POOL_REMOVE_SCRIPT, POOL_CREATE_SCRIPT, POOL_ALTER_SCRIPT, \
    HEALTH_CHECK_EXPECT
from CadVlan.forms import DeleteForm
from CadVlan.Pool.forms import PoolForm, SearchPoolForm
from networkapiclient.Pagination import Pagination
from CadVlan.Util.utility import DataTablePaginator, get_param_in_request
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.shortcuts import render_message_json

logger = logging.getLogger(__name__)


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
        expectstring_choices = populate_expectstring_choices(client)
        enviroments_choices = populate_enviroments_choices(client)
        optionsvips_choices = populate_optionsvips_choices(client)

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

            # Rebuilding the reals list so we can display it again to the user
                # if it raises an error
                pool_members, ip_list_full = populate_pool_members_by_lists(client, ports_reals, ips, id_ips, id_equips,
                                                                   id_pool_member, priorities, weight)

            optionspool_choices = populate_optionspool_choices(client, environment)

            form = PoolForm(enviroments_choices, optionsvips_choices, optionspool_choices, request.POST)

            if form.is_valid():
                # Data form
                identifier = form.cleaned_data['identifier']
                default_port = form.cleaned_data['default_port']
                environment = form.cleaned_data['environment']
                balancing = form.cleaned_data['balancing']
                max_con = form.cleaned_data['max_con']

                client.create_pool().save(None, identifier, default_port, environment,
                                         balancing, healthcheck_type, healthcheck_expect,
                                         healthcheck_request, max_con, ip_list_full, nome_equips,
                                         id_equips, priorities, weight, ports_reals, id_pool_member)
                messages.add_message(
                        request, messages.SUCCESS, pool_messages.get('success_insert'))

                return redirect('pool.list')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_FORM, {'form': form, 'action': action, 'pool_members': pool_members,
                                          'expect_strings': expectstring_choices, 'healthcheck_expect': healthcheck_expect,
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

        expectstring_choices = populate_expectstring_choices(client)
        enviroments_choices = populate_enviroments_choices(client)
        optionsvips_choices = populate_optionsvips_choices(client)

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


            # Rebuilding the reals list so we can display it again to the user
            # if it raises an error
            pool_members, ip_list_full = populate_pool_members_by_lists(client, ports_reals, ips, id_ips, id_equips,
                                                               id_pool_member, priorities, weight)


            optionspool_choices = populate_optionspool_choices(client, environment)

            form = PoolForm(enviroments_choices, optionsvips_choices, optionspool_choices, request.POST)

            if form.is_valid():
                # Data form
                id = form.cleaned_data['id']
                identifier = form.cleaned_data['identifier']
                default_port = form.cleaned_data['default_port']
                environment = form.cleaned_data['environment']
                balancing = form.cleaned_data['balancing']
                max_con = form.cleaned_data['max_con']

                client.create_pool().save(id, identifier, default_port, environment,
                                         balancing, healthcheck_type, healthcheck_expect,
                                         healthcheck_request, max_con, ip_list_full, nome_equips,
                                         id_equips, priorities, weight, ports_reals, id_pool_member)

                messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))

                return redirect(action)
        else:
            pool = client.create_pool().get_by_pk(id_server_pool)

            pool_created = pool['server_pool']['pool_created']

            optionspool_choices = [('', '-')]
            if pool['server_pool']['environment']:
                optionspool_choices = populate_optionspool_choices(client, pool['server_pool']['environment']['id'])

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

            pool_members = populate_pool_members_by_obj(client, pool['server_pool_members'])

            form = PoolForm(enviroments_choices, optionsvips_choices, optionspool_choices, initial=initial_pool)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    if pool_created:
        return redirect(reverse('pool.manage.tab1', args=[id_server_pool]))

    return render_to_response(POOL_FORM, {'form': form, 'action': action, 'pool_members': pool_members,
                                      'expect_strings': expectstring_choices, 'healthcheck_expect': healthcheck_expect,
                                      'healthcheck_request': healthcheck_request, 'label_tab': label_tab,
                                      'pool_created': pool_created, 'id_server_pool': id_server_pool},
                              context_instance=RequestContext(request))


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

    if ips and ips['list_ipv4'] and type(ips['list_ipv4']) is not type([]):
        ips['list_ipv4'] = [ips['list_ipv4']]

    if ips and ips['list_ipv6'] and type(ips['list_ipv6']) is not type([]):
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

    lists = dict()
    lists['opcoes_pool'] = ''

    try:

        ambiente = get_param_in_request(request, 'id_environment')
        opcoes_pool = client_api.create_pool().get_opcoes_pool_by_ambiente(ambiente)

    except NetworkAPIClientError, e:
        logger.error(e)

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
def enable(request):
    """
        Enable Pool Member Running Script
    """
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        id_server_pool = request.POST.get('id_server_pool')
        ids = request.POST.get('ids')

        if id_server_pool and ids:
            client.create_pool().enable(split_to_array(ids))
            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_enable'))
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one") )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect(reverse('pool.manage.tab2', args=[id_server_pool]))


@log
@login_required
@has_perm([{"permission": POOL_ALTER_SCRIPT, "write": True}])
def disable(request):
    """
        Disable Pool Member Running Script
    """
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        id_server_pool = request.POST.get('id_server_pool')
        ids = request.POST.get('ids')

        if id_server_pool and ids:
            client.create_pool().disable(split_to_array(ids))
            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_disable'))
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect(reverse('pool.manage.tab2', args=[id_server_pool]))


@log
@login_required
@has_perm([{'permission': HEALTH_CHECK_EXPECT, "write": True}])
def add_healthcheck_expect(request):

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


@log
@login_required
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "write": True}, {"permission": POOL_ALTER_SCRIPT, "write": True}])
def manage_tab1(request, id_server_pool):

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        pool = client.create_pool().get_by_pk(id_server_pool)

        environment_desc = None
        if pool['server_pool']['environment']:
            environment = client.create_ambiente().buscar_por_id(pool['server_pool']['environment']['id'])
            environment_desc = environment['ambiente']['ambiente_rede']

        health_check = pool['server_pool']['healthcheck']['healthcheck_type'] \
            if pool['server_pool']['healthcheck'] else None

        identifier = pool['server_pool']['identifier']
        default_port = pool['server_pool']['default_port']
        balancing = pool['server_pool']['lb_method']
        max_con = pool['server_pool']['default_limit']

        pool_created = pool['server_pool']['pool_created']
        if not pool_created:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        return render_to_response(POOL_MANAGE_TAB1, {'id_server_pool': id_server_pool, 'health_check': health_check,
                                                     'environment': environment_desc, 'identifier': identifier,
                                                     'default_port': default_port, 'balancing': balancing,
                                                     'max_con': max_con},
                                  context_instance=RequestContext(request))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


@log
@login_required
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "write": True}, {"permission": POOL_ALTER_SCRIPT, "write": True}])
def manage_tab2(request, id_server_pool):
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        pool = client.create_pool().get_by_pk(id_server_pool)

        environment_desc = None
        if pool['server_pool']['environment']:
            environment = client.create_ambiente().buscar_por_id(pool['server_pool']['environment']['id'])
            environment_desc = environment['ambiente']['ambiente_rede']

        health_check = pool['server_pool']['healthcheck']['healthcheck_type'] \
            if pool['server_pool']['healthcheck'] else None

        identifier = pool['server_pool']['identifier']
        default_port = pool['server_pool']['default_port']
        balancing = pool['server_pool']['lb_method']
        max_con = pool['server_pool']['default_limit']

        pool_created = pool['server_pool']['pool_created']
        if not pool_created:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        return render_to_response(POOL_MANAGE_TAB2, {'id_server_pool': id_server_pool, 'health_check': health_check,
                                                     'environment': environment_desc, 'identifier': identifier,
                                                     'default_port': default_port, 'balancing': balancing,
                                                     'max_con': max_con},
                                  context_instance=RequestContext(request))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


@log
@login_required
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "write": True}, {"permission": POOL_ALTER_SCRIPT, "write": True}])
def manage_tab3(request, id_server_pool):
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        enviroments_choices = populate_enviroments_choices(client)
        optionsvips_choices = populate_optionsvips_choices(client)
        expectstring_choices = populate_expectstring_choices(client)

        action = reverse('pool.manage.tab3', args=[id_server_pool])

        pool = client.create_pool().get_by_pk(id_server_pool)

        pool_created = pool['server_pool']['pool_created']
        if not pool_created:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        environment_desc = None
        if pool['server_pool']['environment']:
            environment = client.create_ambiente().buscar_por_id(pool['server_pool']['environment']['id'])
            environment_desc = environment['ambiente']['ambiente_rede']

        health_check = pool['server_pool']['healthcheck']['healthcheck_type'] \
            if pool['server_pool']['healthcheck'] else None

        healthcheck_expect = pool['server_pool']['healthcheck']['healthcheck_expect'] \
            if pool['server_pool']['healthcheck'] else ''

        healthcheck_request = pool['server_pool']['healthcheck']['healthcheck_request'] \
            if pool['server_pool']['healthcheck'] else ''

        identifier = pool['server_pool']['identifier']
        default_port = pool['server_pool']['default_port']
        balancing = pool['server_pool']['lb_method']
        max_con = pool['server_pool']['default_limit']

        environment = pool['server_pool']['environment']['id'] if pool['server_pool']['environment'] else None

        if request.method == 'POST':
                # Data post
                environment = request.POST.get('environment')
                healthcheck_type = request.POST.get('health_check')
                healthcheck_expect = request.POST.get('expect')
                healthcheck_request = request.POST.get('health_check_request')

                optionspool_choices = populate_optionspool_choices(client, environment)

                if healthcheck_type != 'HTTP' and healthcheck_type != 'HTTPS':
                    healthcheck_expect = ''
                    healthcheck_request = ''

                form = PoolForm(enviroments_choices, optionsvips_choices, optionspool_choices, request.POST)
                if form.is_valid():
                    # Data form
                    sv_id_server_pool = form.cleaned_data['id']
                    sv_identifier = form.cleaned_data['identifier']
                    sv_default_port = form.cleaned_data['default_port']
                    sv_environment = form.cleaned_data['environment']
                    sv_balancing = form.cleaned_data['balancing']
                    sv_max_con = form.cleaned_data['max_con']

                    sv_id_pool_member = []
                    sv_ip_list_full = []
                    sv_nome_equips = []
                    sv_id_equips = []
                    sv_priorities = []
                    sv_weight = []
                    sv_ports_reals = []

                    if len(pool['server_pool_members']) > 0:
                        for obj in pool['server_pool_members']:
                            equip = client.create_pool().get_equip_by_ip(obj['ip']['id'])
                            ip = ''
                            if obj['ip']:
                                ip = obj['ip']['ip_formated']
                            elif obj['ipv6']:
                                ip = obj['ipv6']['ip_formated']

                            sv_ip_list_full.append({'id': obj['ip']['id'], 'ip': ip})
                            sv_nome_equips.append(equip['equipamento']['nome'])
                            sv_id_equips.append(equip['equipamento']['id'])
                            sv_priorities.append(obj['priority'])
                            sv_weight.append(obj['weight'])
                            sv_ports_reals.append(obj['port_real'])
                            sv_id_pool_member.append(obj['id'])

                    client.create_pool().save(sv_id_server_pool, sv_identifier, sv_default_port, sv_environment,
                                              sv_balancing, healthcheck_type, healthcheck_expect,
                                              healthcheck_request, sv_max_con, sv_ip_list_full, sv_nome_equips,
                                              sv_id_equips, sv_priorities, sv_weight, sv_ports_reals, sv_id_pool_member)

                    messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))

                    return redirect(reverse('pool.manage.tab3', args=[id_server_pool]))
        else:
            initial_pool = {
                'id': pool['server_pool']['id'],
                'identifier': pool['server_pool']['identifier'],
                'default_port': pool['server_pool']['default_port'],
                'environment': environment,
                'balancing': pool['server_pool']['lb_method'],
                'health_check': health_check,
                'max_con': pool['server_pool']['default_limit'],
            }

            optionspool_choices = populate_optionspool_choices(client, environment)

            form = PoolForm(enviroments_choices, optionsvips_choices, optionspool_choices, initial=initial_pool)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_MANAGE_TAB3, {'id_server_pool': id_server_pool, 'health_check': health_check,
                                             'environment': environment_desc, 'identifier': identifier,
                                             'default_port': default_port, 'balancing': balancing,
                                             'max_con': max_con, 'healthcheck_request': healthcheck_request,
                                             'form': form, 'healthcheck_expect': healthcheck_expect, 'action': action,
                                             'expectstring_choices': expectstring_choices},
                              context_instance=RequestContext(request))


@log
@login_required
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "write": True}, {"permission": POOL_ALTER_SCRIPT, "write": True}])
def manage_tab4(request, id_server_pool):

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        action = reverse('pool.manage.tab4', args=[id_server_pool])
        pool = client.create_pool().get_by_pk(id_server_pool)

        pool_created = pool['server_pool']['pool_created']
        if not pool_created:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        environment_desc = None
        if pool['server_pool']['environment']:
            environment = client.create_ambiente().buscar_por_id(pool['server_pool']['environment']['id'])
            environment_desc = environment['ambiente']['ambiente_rede']

        health_check = pool['server_pool']['healthcheck']['healthcheck_type'] \
            if pool['server_pool']['healthcheck'] else None

        identifier = pool['server_pool']['identifier']
        default_port = pool['server_pool']['default_port']
        balancing = pool['server_pool']['lb_method']
        max_con = pool['server_pool']['default_limit']
        environment = pool['server_pool']['environment']['id'] if pool['server_pool']['environment'] else ''

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

            # Rebuilding the reals list so we can display it again to the user
            # if it raises an error
            pool_members, ip_list_full = populate_pool_members_by_lists(client, ports_reals, ips, id_ips, id_equips,
                                                               id_pool_member, priorities, weight)

            client.create_pool().save_reals(id_server_pool, ip_list_full, nome_equips, id_equips, priorities,
                                            weight, ports_reals, id_pool_member)

            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))

            return redirect(action)
        else:
            pool_members = populate_pool_members_by_obj(client, pool['server_pool_members'])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_MANAGE_TAB4, {'id_server_pool': id_server_pool, 'health_check': health_check,
                                                 'environment_desc': environment_desc, 'identifier': identifier,
                                                 'default_port': default_port, 'balancing': balancing,
                                                 'max_con': max_con, 'pool_members': pool_members, 'action': action,
                                                 'environment': environment},
                          context_instance=RequestContext(request))
