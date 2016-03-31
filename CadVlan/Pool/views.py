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
    populate_pool_members_by_obj, populate_servicedownaction_choices, find_servicedownaction_id, \
    find_servicedownaction_object, populate_pool_members_by_obj_
from CadVlan.Util.Decorators import log, login_required, has_perm, has_perm_external
from django.views.decorators.csrf import csrf_exempt
from CadVlan.templates import POOL_LIST, POOL_FORM, POOL_SPM_DATATABLE, \
    POOL_DATATABLE, AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML, POOL_REQVIP_DATATABLE, POOL_MEMBER_ITEMS, POOL_MANAGE_TAB1, \
    POOL_MANAGE_TAB2, POOL_MANAGE_TAB3, POOL_MANAGE_TAB4
from django.shortcuts import render_to_response, redirect, render
from django.http import HttpResponseServerError, HttpResponse
from django.template import loader
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.messages import healthcheck_messages
from CadVlan.messages import error_messages, pool_messages
from CadVlan.permissions import POOL_MANAGEMENT, POOL_REMOVE_SCRIPT, POOL_CREATE_SCRIPT, POOL_ALTER_SCRIPT, \
    HEALTH_CHECK_EXPECT, EQUIPMENT_MANAGEMENT, VIPS_REQUEST, ENVIRONMENT_MANAGEMENT
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

        environments = client.create_pool().list_environments_with_pools()

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
def spm_datatable(request, id_server_pool, checkstatus):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        columnIndexNameMap = {
            0: '',
            1: 'identifier',
            2: 'ip',
            3: 'port_real',
            4: 'priority',
            5: 'member_status',
            6: 'member_status',
            7: 'member_status',
            8: 'last_status_update'
        }

        dtp = DataTablePaginator(request, columnIndexNameMap)
        dtp.build_server_side_list()

        pools = client.create_pool().get_pool_members(id_server_pool, checkstatus)
        members = pools["server_pools"][0]["server_pool_members"]

        return dtp.build_response(members, len(members), POOL_SPM_DATATABLE, request)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return HttpResponseServerError(e, mimetype='application/javascript')


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def reqvip_datatable(request, id_server_pool):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        columnIndexNameMap = {0: '', 1: 'id', 2: 'ip', 3: 'descricao_ipv4',
                              4: 'descricao_ipv6', 5: 'ambiente', 6: 'valido', 7: 'criado', 8: ''}

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
        return HttpResponseServerError(e, mimetype='application/javascript')


@log
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True}]
)
def add_form(request):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()

        enviroments_choices = populate_enviroments_choices(client)
        optionsvips_choices = populate_optionsvips_choices(client)
        servicedownaction_choices = populate_servicedownaction_choices(client)
        lists["expect_strings"] = populate_expectstring_choices(client)
        lists["action"] = reverse('pool.add.form')
        lists["label_tab"] = u'Cadastro de Pool'
        lists["pool_created"] = False

        if request.method == 'GET':
            lists["pool_members"] = list()
            lists["healthcheck_expect"] = ''
            lists["healthcheck_request"] = ''
            lists["form"] = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices)

        if request.method == 'POST':

            members = dict()
            members["id_pool_member"] = request.POST.getlist('id_pool_member')
            members["id_equips"] = request.POST.getlist('id_equip')
            members["priorities"] = request.POST.getlist('priority')
            members["ports_reals"] = request.POST.getlist('ports_real_reals')
            members["weight"] = request.POST.getlist('weight')
            members["id_ips"] = request.POST.getlist('id_ip')
            members["ips"] = request.POST.getlist('ip')
            members["environment"] = request.POST.get('environment')
            healthcheck_type = request.POST.get('health_check')

            if healthcheck_type != 'HTTP' and healthcheck_type != 'HTTPS':
                lists["healthcheck_expect"] = ''
                lists["healthcheck_request"] = ''
            else:
                lists["healthcheck_expect"] = request.POST.get('expect')
                lists["healthcheck_request"] = request.POST.get('health_check_request')

            lists["pool_members"], ip_list_full = populate_pool_members_by_lists(client, members)
            optionspool_choices = populate_optionspool_choices(client, members.get("environment"))

            form = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices, optionspool_choices,
                            request.POST)

            if form.is_valid():

                limit = form.cleaned_data['max_con']
                server_pool_members = format_server_pool_members(request, limit)
                healthcheck = format_healthcheck(request)
                servicedownaction = format_servicedownaction(client, form)
                pool = format_pool(client, form, server_pool_members, healthcheck, servicedownaction)
                client.create_pool().save_pool(pool)
                messages.add_message(request, messages.SUCCESS, pool_messages.get('success_insert'))

                return redirect('pool.list')

            lists["form"] = form

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        form = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices, optionspool_choices,
                        request.POST)
        lists["form"] = form

    return render_to_response(POOL_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True, "read": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True}]
)
def edit_form(request, id_server_pool):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()

        enviroments_choices = populate_enviroments_choices(client)
        optionsvips_choices = populate_optionsvips_choices(client)
        servicedownaction_choices = populate_servicedownaction_choices(client)
        lists["expect_strings"] = populate_expectstring_choices(client)
        lists["action"] = reverse('pool.edit.form', args=[id_server_pool])
        lists["label_tab"] = u'Edição de Pool'
        lists["id_server_pool"] = id_server_pool

        pool = client.create_pool().get_pool(id_server_pool)
        server_pools = pool['server_pools'][0]
        pool_created = lists["pool_created"] = server_pools['pool_created']

        if request.method == 'GET':

            optionspool_choices = [('', '-')]

            environment = server_pools['environment']

            if environment:
                optionspool_choices = populate_optionspool_choices(client, environment)

            lists["healthcheck_expect"] = server_pools['healthcheck']['healthcheck_expect'] \
                if server_pools['healthcheck'] else ''

            lists["healthcheck_request"] = server_pools['healthcheck']['healthcheck_request'] \
                if server_pools['healthcheck'] else ''

            health_check = server_pools['healthcheck']['healthcheck_type'] \
                if server_pools['healthcheck'] else None

            initial_pool = {
                'id': server_pools['id'],
                'identifier': server_pools['identifier'],
                'default_port': server_pools['default_port'],
                'environment': environment,
                'balancing': server_pools['lb_method'],
                'health_check': health_check,
                'max_con': server_pools['default_limit'],
                'servicedownaction': server_pools['servicedownaction']['id']
            }

            lists["pool_members"] = populate_pool_members_by_obj_(server_pools['server_pool_members'])

            lists["form"] = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices,
                                     optionspool_choices, initial=initial_pool)

        if request.method == 'POST':

            members = dict()
            members["id_pool_member"] = request.POST.getlist('id_pool_member')
            members["id_equips"] = request.POST.getlist('id_equip')
            members["priorities"] = request.POST.getlist('priority')
            members["ports_reals"] = request.POST.getlist('ports_real_reals')
            members["weight"] = request.POST.getlist('weight')
            members["id_ips"] = request.POST.getlist('id_ip')
            members["ips"] = request.POST.getlist('ip')
            members["environment"] = request.POST.get('environment')
            healthcheck_type = request.POST.get('health_check')

            if healthcheck_type != 'HTTP' and healthcheck_type != 'HTTPS':
                lists["healthcheck_expect"] = ''
                lists["healthcheck_request"] = ''
            else:
                lists["healthcheck_expect"] = request.POST.get('expect')
                lists["healthcheck_request"] = request.POST.get('health_check_request')

            lists["pool_members"], ip_list_full = populate_pool_members_by_lists(client, members)
            optionspool_choices = populate_optionspool_choices(client, members.get("environment"))

            form = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices, optionspool_choices,
                            request.POST)

            if form.is_valid():

                limit = form.cleaned_data['max_con']
                server_pool_members = format_server_pool_members(request, limit)
                healthcheck = format_healthcheck(request)
                servicedownaction = format_servicedownaction(client, form)
                pool = format_pool(client, form, server_pool_members, healthcheck, servicedownaction, int(id_server_pool))
                client.create_pool().update_pool(pool, id_server_pool)
                messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))

                return redirect(lists["action"])

            lists["form"] = form

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        form = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices, optionspool_choices,
                        request.POST)
        lists["form"] = form

    if pool_created:
        return redirect(reverse('pool.manage.tab1', args=[id_server_pool]))

    return render_to_response(POOL_FORM, lists, context_instance=RequestContext(request))


@log
@csrf_exempt
@has_perm_external([
    {"permission": POOL_MANAGEMENT, "read": True, "write": True},
    {"permission": EQUIPMENT_MANAGEMENT, "read": True, }
])
def ajax_modal_ip_real_server_external(request, form_acess, client):
    return __modal_ip_list_real(request, client)


@log
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "read": True, "write": True},
    {"permission": EQUIPMENT_MANAGEMENT, "read": True, }
])
def ajax_modal_ip_real_server(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return __modal_ip_list_real(request, client_api)


def __modal_ip_list_real(request, client_api):

    lists = {'msg': str(), 'ips': []}
    ips = {}
    status_code = 200
    ambiente = get_param_in_request(request, 'id_environment')
    equip_name = get_param_in_request(request, 'equip_name')

    try:
        # Valid Equipament
        equip = client_api.create_equipamento().listar_por_nome(equip_name).get("equipamento")
        ips_list = client_api.create_pool().get_available_ips_to_add_server_pool(equip_name, ambiente)
    except NetworkAPIClientError, e:
        logger.error(e)
        status_code = 500
        return HttpResponse(json.dumps({'message': e.error, 'status': 'error'}), status=status_code,
                            content_type='application/json')

    if not ips_list['list_ipv4'] and not ips_list['list_ipv6']:
        return HttpResponse(json.dumps({'message': u'Esse equipamento não tem nenhum IP que '
                                                   u'possa ser utilizado nos pools desse ambiente.',
                                        'status': 'error'}), status=status_code, content_type='application/json')

    ips['list_ipv4'] = ips_list['list_ipv4']
    ips['list_ipv6'] = ips_list['list_ipv6']
    lists['ips'] = ips
    lists['equip'] = equip

    return HttpResponse(loader.render_to_string(AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML, lists,
                                                context_instance=RequestContext(request)), status=status_code)


@log
@csrf_exempt
@has_perm_external([{"permission": POOL_MANAGEMENT, "read": True}])
def ajax_get_opcoes_pool_by_ambiente_external(request, form_acess, client):
    return __get_opcoes_pool_by_ambiente(request, client)


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def ajax_get_opcoes_pool_by_ambiente(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return __get_opcoes_pool_by_ambiente(request, client_api)


def __get_opcoes_pool_by_ambiente(request, client_api):

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
    """Delete Pool Into Database"""

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = DeleteForm(request.POST)

        if form.is_valid():
            ids = form.cleaned_data['ids']
            client.create_pool().delete_pool(ids)
            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_delete'))
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('pool.list')


@log
@login_required
@has_perm([{"permission": POOL_REMOVE_SCRIPT, "write": True}])
def remove(request):
    """Remove Pool Running Script and Update to Not Created"""

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = DeleteForm(request.POST)

        if form.is_valid():
            ids = form.cleaned_data['ids']
            client.create_pool().deploy_remove_pool(ids)
            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_remove'))
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('pool.list')


@log
@login_required
@has_perm([{"permission": POOL_CREATE_SCRIPT, "write": True}])
def create(request):
    """Remove Pool Running Script and Update to Not Created"""

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = DeleteForm(request.POST)

        if form.is_valid():
            ids = form.cleaned_data['ids']
            client.create_pool().deploy_create_pool(ids)
            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_create'))
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('pool.list')


@log
@login_required
@has_perm([{"permission": POOL_ALTER_SCRIPT, "write": True}])
def status_change(request):
    """Enable Pool Member Running Script"""

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        id_server_pool = request.POST.get('id_server_pool')
        ids = request.POST.get('ids')
        action = request.POST.get('action')

        if id_server_pool and ids:
            pools = client.create_pool().get_pool_members(id_server_pool)
            members = pools["server_pools"][0]["server_pool_members"]

            for member in members:
                member_status = list(bin(member['member_status']))
                if action[-2] != 'x':
                    member_status[-2] = action[-2]
                else:
                    member_status[-1] = action[-1]
                member_status = int(''.join(member_status), 2)
                if member_status != member['member_status'] and str(member['id']) in ids.split(';'):
                    member['member_status'] = member_status

            client.create_pool().deploy_update_pool_members(id_server_pool, pools["server_pools"][0])

            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_status_change'))
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect(reverse('pool.manage.tab2', args=[id_server_pool]))


@log
@login_required
@has_perm([{"permission": POOL_ALTER_SCRIPT, "write": True}])
def enable(request):
    """Enable Pool Member Running Script"""

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        id_server_pool = request.POST.get('id_server_pool')
        ids = request.POST.get('ids')

        if id_server_pool and ids:
            client.create_pool().enable(split_to_array(ids))
            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_enable'))
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

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
            messages.add_message(
                request, messages.SUCCESS, pool_messages.get('success_disable'))
        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect(reverse('pool.manage.tab2', args=[id_server_pool]))


@log
@csrf_exempt
@has_perm_external([{'permission': HEALTH_CHECK_EXPECT, "write": True}])
def add_healthcheck_expect_external(request, form_acess, client):
    return __add_healthcheck_expect_shared(request, client)


@log
@login_required
@has_perm([{'permission': HEALTH_CHECK_EXPECT, "write": True}])
def add_healthcheck_expect(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    return __add_healthcheck_expect_shared(request, client)


def __add_healthcheck_expect_shared(request, client):
    lists = dict()
    try:
        if request.method == 'GET':

            expect_string = request.GET.get("expect_string")
            id_environment = request.GET.get("id_environment")

            if expect_string != '':

                client.create_ambiente().add_healthcheck_expect(id_ambiente=id_environment, expect_string=expect_string,
                                                                match_list=expect_string)

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

        return render(request, POOL_MEMBER_ITEMS, pool_data)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


@log
@login_required
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True, "read": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True},
    {"permission": VIPS_REQUEST, "read": True},
    {"permission": ENVIRONMENT_MANAGEMENT, "read": True}
])
def manage_tab1(request, id_server_pool):

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()
        lists["id_server_pool"] = id_server_pool
        pool = client.create_pool().get_pool(id_server_pool)
        server_pools = pool['server_pools'][0]

        lists["environment"] = None
        if server_pools['environment']:
            environment = client.create_ambiente().buscar_por_id(server_pools['environment'])
            lists["environment"] = environment['ambiente']['ambiente_rede']

        lists["health_check"] = server_pools['healthcheck']['healthcheck_type'] if server_pools['healthcheck'] else None

        lists["identifier"] = server_pools['identifier']
        lists["default_port"] = server_pools['default_port']
        lists["balancing"] = server_pools['lb_method']
        lists["servicedownaction"] = server_pools['servicedownaction']['name']
        lists["max_con"] = server_pools['default_limit']
        lists["pool_created"] = server_pools['pool_created']

        if not lists['pool_created']:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        return render_to_response(POOL_MANAGE_TAB1, lists, context_instance=RequestContext(request))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


@log
@login_required
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True, "read": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True},
    {"permission": ENVIRONMENT_MANAGEMENT, "read": True}
])
def manage_tab2(request, id_server_pool):
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()
        lists["id_server_pool"] = id_server_pool
        pool = client.create_pool().get_pool(id_server_pool)
        server_pools = pool['server_pools'][0]

        lists["environment"] = None
        if server_pools['environment']:
            environment = client.create_ambiente().buscar_por_id(server_pools['environment'])
            lists["environment"] = environment['ambiente']['ambiente_rede']

        lists["health_check"] = server_pools['healthcheck']['healthcheck_type'] if server_pools['healthcheck'] else None

        lists["identifier"] = server_pools['identifier']
        lists["default_port"] = server_pools['default_port']
        lists["balancing"] = server_pools['lb_method']
        lists["servicedownaction"] = server_pools['servicedownaction']['name']
        lists["max_con"] = server_pools['default_limit']
        lists["pool_created"] = server_pools['pool_created']

        if not lists['pool_created']:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        return render_to_response(POOL_MANAGE_TAB2, lists, context_instance=RequestContext(request))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


@log
@login_required
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True},
    {"permission": ENVIRONMENT_MANAGEMENT, "read": True}
])
def manage_tab3_(request, id_server_pool):
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        enviroments_choices = populate_enviroments_choices(client)
        optionsvips_choices = populate_optionsvips_choices(client)
        expectstring_choices = populate_expectstring_choices(client)
        servicedownaction_choices = populate_servicedownaction_choices(client)

        action = reverse('pool.manage.tab3', args=[id_server_pool])

        pool = client.create_pool().get_by_pk(id_server_pool)

        pool_created = pool['server_pool']['pool_created']
        if not pool_created:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        environment_desc = None
        if pool['server_pool']['environment']:
            environment = client.create_ambiente().buscar_por_id(
                pool['server_pool']['environment']['id'])
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
        servicedownaction = pool['server_pool']['servicedownaction'][u'name']
        max_con = pool['server_pool']['default_limit']

        environment = pool['server_pool']['environment'][
            'id'] if pool['server_pool']['environment'] else None

        if request.method == 'POST':
                # Data post
            environment = request.POST.get('environment')
            healthcheck_type = request.POST.get('health_check')
            healthcheck_expect = request.POST.get('expect')
            healthcheck_request = request.POST.get('health_check_request')

            optionspool_choices = populate_optionspool_choices(
                client, environment)

            if healthcheck_type != 'HTTP' and healthcheck_type != 'HTTPS':
                healthcheck_expect = ''
                healthcheck_request = ''

            form = PoolForm(enviroments_choices, optionsvips_choices,
                            servicedownaction_choices, optionspool_choices, request.POST)
            if form.is_valid():
                # Data form
                sv_id_server_pool = form.cleaned_data['id']
                sv_identifier = form.cleaned_data['identifier']
                sv_default_port = form.cleaned_data['default_port']
                sv_environment = form.cleaned_data['environment']
                sv_balancing = form.cleaned_data['balancing']
                sv_max_con = form.cleaned_data['max_con']
                sv_servicedownaction = form.cleaned_data['servicedownaction']
                sv_servicedownaction_id = find_servicedownaction_id(
                    client, sv_servicedownaction)

                sv_id_pool_member = []
                sv_ip_list_full = []
                sv_nome_equips = []
                sv_id_equips = []
                sv_priorities = []
                sv_weight = []
                sv_ports_reals = []

                if len(pool['server_pool_members']) > 0:
                    for obj in pool['server_pool_members']:

                        # get_equip_by_ip method can return many equipments related with those Ips,
                        # this is an error, because the equipment returned
                        # cannot be the same

                        # equip = client.create_pool().get_equip_by_ip(obj['ip']['id'])
                        equip = client.create_equipamento().listar_por_nome(
                            obj['equipment_name'])
                        ip = ''
                        if obj['ip']:
                            ip = obj['ip']['ip_formated']
                        elif obj['ipv6']:
                            ip = obj['ipv6']['ip_formated']

                        sv_ip_list_full.append(
                            {'id': obj['ip']['id'], 'ip': ip})
                        sv_nome_equips.append(equip['equipamento']['nome'])
                        sv_id_equips.append(equip['equipamento']['id'])
                        sv_priorities.append(obj['priority'])
                        sv_weight.append(obj['weight'])
                        sv_ports_reals.append(obj['port_real'])
                        sv_id_pool_member.append(obj['id'])

                client.create_pool().save(sv_id_server_pool, sv_identifier, sv_default_port, sv_environment,
                                          sv_balancing, healthcheck_type, healthcheck_expect,
                                          healthcheck_request, sv_max_con, sv_ip_list_full, sv_nome_equips,
                                          sv_id_equips, sv_priorities, sv_weight, sv_ports_reals, sv_id_pool_member, sv_servicedownaction_id)

                messages.add_message(
                    request, messages.SUCCESS, pool_messages.get('success_update'))
                return redirect(reverse('pool.manage.tab3', args=[id_server_pool]))

        else:
            initial_pool = {
                'id': pool['server_pool']['id'],
                'identifier': pool['server_pool']['identifier'],
                'default_port': pool['server_pool']['default_port'],
                'environment': environment,
                'balancing': pool['server_pool']['lb_method'],
                'servicedownaction': pool['server_pool']['servicedownaction'][u'name'],
                'health_check': health_check,
                'max_con': pool['server_pool']['default_limit'],
            }

            optionspool_choices = populate_optionspool_choices(client, environment)

            form = PoolForm(enviroments_choices, optionsvips_choices,
                            servicedownaction_choices, optionspool_choices, initial=initial_pool)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_MANAGE_TAB3, {'id_server_pool': id_server_pool, 'health_check': health_check,
                                                 'environment': environment_desc, 'identifier': identifier,
                                                 'default_port': default_port, 'balancing': balancing,
                                                 'max_con': max_con, 'healthcheck_request': healthcheck_request,
                                                 'form': form, 'healthcheck_expect': healthcheck_expect, 'action': action,
                                                 'expectstring_choices': expectstring_choices, 'servicedownaction': servicedownaction},
                              context_instance=RequestContext(request))


@log
@login_required
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True},
    {"permission": ENVIRONMENT_MANAGEMENT, "read": True}
])
def manage_tab3(request, id_server_pool):
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()

        enviroments_choices = populate_enviroments_choices(client)
        optionsvips_choices = populate_optionsvips_choices(client)
        servicedownaction_choices = populate_servicedownaction_choices(client)
        lists["expectstring_choices"] = populate_expectstring_choices(client)

        lists["action"] = reverse('pool.manage.tab3', args=[id_server_pool])
        lists["id_server_pool"] = id_server_pool

        pool = client.create_pool().get_pool(id_server_pool)
        server_pools = pool['server_pools'][0]
        members = server_pools['server_pool_members']

        optionspool_choices = populate_optionspool_choices(client, server_pools['environment'])

        lists["environment"] = None
        if server_pools['environment']:
            environment = client.create_ambiente().buscar_por_id(server_pools['environment'])
            lists["environment"] = environment['ambiente']['ambiente_rede']

        lists["pool_created"] = server_pools['pool_created']
        if not lists['pool_created']:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        lists["health_check"] = server_pools['healthcheck']['healthcheck_type'] \
            if server_pools['healthcheck'] else None
        lists['healthcheck_expect'] = server_pools['healthcheck']['healthcheck_expect'] \
            if server_pools['healthcheck'] else ''
        lists['healthcheck_request'] = server_pools['healthcheck']['healthcheck_request'] \
            if server_pools['healthcheck'] else ''

        lists["identifier"] = server_pools['identifier']
        lists["default_port"] = server_pools['default_port']
        lists["balancing"] = server_pools['lb_method']
        lists["servicedownaction"] = server_pools['servicedownaction']['name']
        lists["max_con"] = server_pools['default_limit']

        if request.method == 'POST':

            environment = request.POST.get('environment')
            optionspool_choices = populate_optionspool_choices(client, environment)

            form = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices, optionspool_choices,
                            request.POST)

            if form.is_valid():

                healthcheck = format_healthcheck(request)
                servicedownaction = format_servicedownaction(client, form)
                pool = format_pool(client, form, members, healthcheck, servicedownaction, int(id_server_pool))
                client.create_pool().deploy_update_pool(pool, id_server_pool)

                messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))
                return redirect(reverse('pool.manage.tab3', args=[id_server_pool]))

        if request.method == 'GET':

            initial_pool = {
                'id': server_pools['id'],
                'identifier': server_pools['identifier'],
                'default_port': server_pools['default_port'],
                'environment': server_pools['environment'],
                'balancing': server_pools['lb_method'],
                'health_check': lists["health_check"],
                'max_con': server_pools['default_limit'],
                'servicedownaction': server_pools['servicedownaction']['id']
            }

            form = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices, optionspool_choices,
                            initial=initial_pool)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        form = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices, optionspool_choices,
                        request.POST)

    lists["form"] = form
    return render_to_response(POOL_MANAGE_TAB3, lists, context_instance=RequestContext(request))


@log
@login_required
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True},
    {"permission": ENVIRONMENT_MANAGEMENT, "read": True}
])
def manage_tab4_(request, id_server_pool):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()
        lists["action"] = reverse('pool.manage.tab4', args=[id_server_pool])
        lists["id_server_pool"] = id_server_pool

        pool = client.create_pool().get_pool(id_server_pool)
        server_pools = pool['server_pools'][0]

        pool_created = server_pools['pool_created']
        if not pool_created:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        lists["environment_desc"] = None
        if server_pools['environment']:
            environment = client.create_ambiente().buscar_por_id(server_pools['environment'])
            lists["environment_desc"] = environment['ambiente']['ambiente_rede']

        lists["health_check"] = server_pools['healthcheck']['healthcheck_type'] if server_pools['healthcheck'] else None

        lists["identifier"] = server_pools['identifier']
        lists["default_port"] = server_pools['default_port']
        lists["balancing"] = server_pools['lb_method']
        lists["servicedownaction"] = server_pools['servicedownaction']['name']
        lists["max_con"] = server_pools['default_limit']
        lists["pool_created"] = server_pools['pool_created']

        if request.method == 'POST':

            members = dict()
            members["id_pool_member"] = request.POST.getlist('id_pool_member')
            members["id_equips"] = request.POST.getlist('id_equip')
            members["priorities"] = request.POST.getlist('priority')
            members["ports_reals"] = request.POST.getlist('ports_real_reals')
            members["weight"] = request.POST.getlist('weight')
            members["id_ips"] = request.POST.getlist('id_ip')
            members["ips"] = request.POST.getlist('ip')

            lists["pool_members"], ip_list_full = populate_pool_members_by_lists(client, members)

            client.create_pool().save_reals(id_server_pool, ip_list_full, members.get("nome_equips"), members.get("id_equips"),
                                            members.get("priorities"), members.get("weight"), members.get("ports_reals"),
                                            members.get("id_pool_member"))

            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))

            return redirect(lists['action'])
        else:
            lists["pool_members"] = populate_pool_members_by_obj_(server_pools['server_pool_members'])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_MANAGE_TAB4, lists, context_instance=RequestContext(request))


@log
@login_required
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True},
    {"permission": ENVIRONMENT_MANAGEMENT, "read": True}
])
def manage_tab4(request, id_server_pool):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()
        lists["action"] = reverse('pool.manage.tab4', args=[id_server_pool])
        lists["id_server_pool"] = id_server_pool

        pool = client.create_pool().get_pool(id_server_pool)
        server_pools = pool['server_pools'][0]

        lists["pool_created"] = pool_created = server_pools['pool_created']
        if not pool_created:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        lists["environment_desc"] = None
        if server_pools['environment']:
            environment = client.create_ambiente().buscar_por_id(server_pools['environment'])
            lists["environment_desc"] = environment['ambiente']['ambiente_rede']
        lists["health_check"] = server_pools['healthcheck']['healthcheck_type'] if server_pools['healthcheck'] else None
        lists["identifier"] = server_pools['identifier']
        lists["default_port"] = server_pools['default_port']
        lists["balancing"] = server_pools['lb_method']
        lists["servicedownaction"] = server_pools['servicedownaction']['name']
        lists["max_con"] = server_pools['default_limit']
        lists["environment_id"] = server_pools['environment']

        if request.method == 'POST':

            server_pool_members = format_server_pool_members(request, lists["max_con"])
            lists["pool_members"] = populate_pool_members_by_obj_(server_pool_members)
            server_pools['server_pool_members'] = server_pool_members
            client.create_pool().deploy_update_pool(server_pools, id_server_pool)
            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))
            return redirect(lists['action'])

        if request.method == 'GET':
            lists["pool_members"] = populate_pool_members_by_obj_(server_pools['server_pool_members'])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_MANAGE_TAB4, lists, context_instance=RequestContext(request))


def format_pool(client, form, server_pool_members, healthcheck, servicedownaction, id=None):

    pool = dict()
    pool["id"] = id
    pool["identifier"] = str(form.cleaned_data['identifier'])
    pool["default_port"] = int(form.cleaned_data['default_port'])
    pool["environment"] = int(form.cleaned_data['environment'])
    pool["servicedownaction"] = servicedownaction
    pool["lb_method"] = str(form.cleaned_data['balancing'])
    pool["healthcheck"] = healthcheck
    pool["default_limit"] = int(form.cleaned_data['max_con'])
    pool["server_pool_members"] = server_pool_members
    for member in server_pool_members:
        member['limit'] = pool['default_limit']

    return pool


def format_server_pool_members(request, limit=0):

    pool_members = []
    equips = request.POST.getlist('id_equip')
    for i in range(0, len(equips)):
        server_pool_members = dict()
        server_pool_members["id"] = int(request.POST.getlist('id_pool_member')[i]) \
            if request.POST.getlist('id_pool_member')[i] else None
        server_pool_members["identifier"] = str(request.POST.getlist('equip')[i])
        server_pool_members["priority"] = int(request.POST.getlist('priority')[i])
        server_pool_members["equipment"] = format_equipments(request, i)
        server_pool_members["weight"] = int(request.POST.getlist('weight')[i])
        server_pool_members["limit"] = limit
        server_pool_members["port_real"] = int(request.POST.getlist('ports_real_reals')[i])
        server_pool_members["member_status"] = 0
        server_pool_members["ip"] = format_ips(request, i)
        server_pool_members["ipv6"] = None
        pool_members.append(server_pool_members)

    return pool_members


def format_equipments(request, i):

    equipments = dict()
    equipments["id"] = int(request.POST.getlist('id_equip')[i])
    equipments["nome"] = str(request.POST.getlist('equip')[i])

    return equipments


def format_ips(request, i):

    ips = dict()
    ips["id"] = int(request.POST.getlist('id_ip')[i])
    ips["ip_formated"] = str(request.POST.getlist('ip')[i])

    return ips


def format_healthcheck(request, id=None):

    healthcheck = dict()
    healthcheck["id"] = id
    healthcheck["identifier"] = ""
    healthcheck["healthcheck_type"] = str(request.POST.get('health_check'))
    if healthcheck["healthcheck_type"] != 'HTTP' and healthcheck["healthcheck_type"] != 'HTTPS':
        healthcheck["healthcheck_expect"] = ''
        healthcheck["healthcheck_request"] = ''
    else:
        healthcheck["healthcheck_request"] = str(request.POST.get('health_check_request'))
        healthcheck["healthcheck_expect"] = str(request.POST.get('expect'))
    healthcheck["destination"] = "*:*"

    return healthcheck


def format_servicedownaction(client, form):

    servicedownaction = dict()
    servicedownaction["id"] = int(form.cleaned_data['servicedownaction'])
    servicedownaction["name"] = str(find_servicedownaction_object(client, id=servicedownaction['id']))

    return servicedownaction
