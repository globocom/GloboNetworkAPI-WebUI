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


from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.forms import DeleteForm
from CadVlan.messages import error_messages, healthcheck_messages, pool_messages
from CadVlan.Pool import facade
from CadVlan.Pool.forms import PoolForm, SearchPoolForm, PoolHealthcheckForm, PoolFormV3
from CadVlan.permissions import POOL_MANAGEMENT, POOL_REMOVE_SCRIPT, POOL_CREATE_SCRIPT, POOL_ALTER_SCRIPT, \
    HEALTH_CHECK_EXPECT, EQUIPMENT_MANAGEMENT, VIPS_REQUEST, ENVIRONMENT_MANAGEMENT
from CadVlan.templates import POOL_LIST, POOL_FORM, POOL_SPM_DATATABLE, \
    POOL_DATATABLE, AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML, POOL_REQVIP_DATATABLE, POOL_MEMBER_ITEMS, POOL_MANAGE_TAB1, \
    POOL_MANAGE_TAB2, POOL_MANAGE_TAB3, POOL_MANAGE_TAB4
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.Decorators import has_perm, has_perm_external, log, login_required
from CadVlan.Util.shortcuts import render_message_json
from CadVlan.Util.utility import DataTablePaginator, get_param_in_request
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, render, render_to_response
from django.template import loader
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt

from networkapiclient.exception import NetworkAPIClientError
from networkapiclient.Pagination import Pagination

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def list_all(request):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        environments = client.create_pool().list_environments_with_pools()

        lists = dict()
        lists["delete_form"] = DeleteForm()
        lists["search_form"] = SearchPoolForm(environments)

        return render_to_response(POOL_LIST, lists, context_instance=RequestContext(request))

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

        column_index_name_map = {
            0: '',
            1: 'identifier',
            2: 'default_port',
            3: 'healthcheck__healthcheck_type',
            4: 'environment',
            5: 'pool_created',
            6: ''
        }

        dtp = DataTablePaginator(request, column_index_name_map)

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

        data = dict()
        data["start_record"] = pagination.start_record
        data["end_record"] = pagination.end_record
        data["asorting_cols"] = pagination.asorting_cols
        data["searchable_columns"] = pagination.searchable_columns
        data["custom_search"] = pagination.custom_search or ""
        data["extends_search"] = [{"environment": environment_id}] if environment_id else []

        pools = client.create_pool().list_pool(data)

        return dtp.build_response(
            pools["server_pools"],
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

        column_index_name_map = {
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

        dtp = DataTablePaginator(request, column_index_name_map)
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

        column_index_name_map = {
            0: '',
            1: 'id',
            2: 'Nome(s) do VIP',
            3: 'IPv4',
            4: 'IPv6',
            5: 'Equipamento(s)',
            6: 'Ambiente VIP',
            7: 'criado',
            8: ''
        }

        dtp = DataTablePaginator(request, column_index_name_map)
        dtp.build_server_side_list()

        requisicoes_vip = client.create_pool().get_vip_by_pool(id_server_pool)

        return dtp.build_response(requisicoes_vip["vips"], requisicoes_vip["total"], POOL_REQVIP_DATATABLE, request)

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

        enviroments_choices = facade.populate_enviroments_choices(client)
        optionsvips_choices = facade.populate_optionsvips_choices(client)
        servicedownaction_choices = facade.populate_servicedownaction_choices(client)
        lists["expect_strings"] = facade.populate_expectstring_choices(client)
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
            members["member_status"] = request.POST.getlist('member_status')
            members["name_equips"] = request.POST.getlist('equip')
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

            lists["pool_members"], ip_list_full = facade.populate_pool_members_by_lists(client, members)
            optionspool_choices = facade.populate_optionspool_choices(client, members.get("environment"))

            form = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices, optionspool_choices,
                            request.POST)

            if form.is_valid():

                limit = form.cleaned_data['max_con']
                server_pool_members = facade.format_server_pool_members(request, limit)
                healthcheck = facade.format_healthcheck(request)
                servicedownaction = facade.format_servicedownaction(client, form)
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

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    lists = dict()

    enviroments_choices = facade.populate_enviroments_choices(client)
    optionsvips_choices = facade.populate_optionsvips_choices(client)
    servicedownaction_choices = facade.populate_servicedownaction_choices(client)
    lists["expect_strings"] = facade.populate_expectstring_choices(client)
    lists["action"] = reverse('pool.edit.form', args=[id_server_pool])
    lists["label_tab"] = u'Edição de Pool'
    lists["id_server_pool"] = id_server_pool

    try:

        pool = client.create_api_pool().get_pool_details(id_server_pool)['server_pools'][0]
        pool_created = lists["pool_created"] = pool['pool_created']

        if request.method == 'GET':

            optionspool_choices = [('', '-')]

            environment = pool['environment']

            if environment:
                optionspool_choices = facade.populate_optionspool_choices(client, environment)

            lists["healthcheck_expect"] = pool['healthcheck']['healthcheck_expect'] \
                if pool['healthcheck'] else ''

            lists["healthcheck_request"] = pool['healthcheck']['healthcheck_request'] \
                if pool['healthcheck'] else ''

            health_check = pool['healthcheck']['healthcheck_type'] \
                if pool['healthcheck'] else None

            initial_pool = {
                'id': pool['id'],
                'identifier': pool['identifier'],
                'default_port': pool['default_port'],
                'environment': environment,
                'balancing': pool['lb_method'],
                'health_check': health_check,
                'max_con': pool['default_limit'],
                'servicedownaction': pool['servicedownaction']['id']
            }

            lists["pool_members"] = facade.populate_pool_members_by_obj(pool['server_pool_members'])

            lists["form"] = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices,
                                     optionspool_choices, initial=initial_pool)

        if request.method == 'POST':

            members = dict()
            members["id_pool_member"] = request.POST.getlist('id_pool_member')
            members["id_equips"] = request.POST.getlist('id_equip')
            members["member_status"] = request.POST.getlist('member_status')
            members["name_equips"] = request.POST.getlist('equip')
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

            lists["pool_members"], ip_list_full = facade.populate_pool_members_by_lists(client, members)
            optionspool_choices = facade.populate_optionspool_choices(client, members.get("environment"))

            form = PoolForm(enviroments_choices, optionsvips_choices, servicedownaction_choices, optionspool_choices,
                            request.POST)

            if form.is_valid():

                limit = form.cleaned_data['max_con']
                server_pool_members = facade.format_server_pool_members(request, limit)
                healthcheck = facade.format_healthcheck(request)
                servicedownaction = facade.format_servicedownaction(client, form)
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
    return _modal_ip_list_real(request, client)


@log
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "read": True, "write": True},
    {"permission": EQUIPMENT_MANAGEMENT, "read": True, }
])
def ajax_modal_ip_real_server(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return _modal_ip_list_real(request, client_api)


def _modal_ip_list_real(request, client_api):

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

    return HttpResponse(
        loader.render_to_string(
            AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML,
            lists,
            context_instance=RequestContext(request)
        ), status=status_code)


@log
@csrf_exempt
@has_perm_external([{"permission": POOL_MANAGEMENT, "read": True}])
def ajax_get_opcoes_pool_by_ambiente_external(request, form_acess, client):
    return _get_opcoes_pool_by_ambiente(request, client)


@log
@login_required
@has_perm([{"permission": POOL_MANAGEMENT, "read": True}])
def ajax_get_opcoes_pool_by_ambiente(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return _get_opcoes_pool_by_ambiente(request, client_api)


def _get_opcoes_pool_by_ambiente(request, client_api):

    opcoes_pool = dict()
    opcoes_pool['options_pool'] = []

    try:
        ambiente = get_param_in_request(request, 'id_environment')
        opcoes_pool = client_api.create_pool().get_opcoes_pool_by_environment(ambiente)
    except NetworkAPIClientError, e:
        logger.error(e)

    return HttpResponse(json.dumps(opcoes_pool['options_pool']), content_type='application/json')


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
    return _add_healthcheck_expect_shared(request, client)


@log
@login_required
@has_perm([{'permission': HEALTH_CHECK_EXPECT, "write": True}])
def add_healthcheck_expect(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    return _add_healthcheck_expect_shared(request, client)


def _add_healthcheck_expect_shared(request, client):
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
        pool = client.create_api_pool().get_pool_details(id_server_pool)['server_pools'][0]

        lists["environment"] = pool['environment']['name']
        lists["identifier"] = pool['identifier']
        lists["default_port"] = pool['default_port']
        lists["balancing"] = pool['lb_method']
        lists["servicedownaction"] = pool['servicedownaction']['name']
        lists["max_con"] = pool['default_limit']
        lists["pool_created"] = pool['pool_created']
        lists["health_check"] = pool['healthcheck']['healthcheck_type'] if pool['healthcheck'] else None

        if not pool['pool_created']:
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

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    lists = dict()
    lists["id_server_pool"] = id_server_pool
    try:
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
        return render_to_response(POOL_MANAGE_TAB2, lists, context_instance=RequestContext(request))


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

        lb_method_choices = facade.populate_optionsvips_choices(client)
        servicedownaction_choices = facade.populate_servicedownaction_choices(client)

        pool = client.create_api_pool().get_pool_details(id_server_pool)['server_pools'][0]
        environment_id = pool['environment']['id']

        members = pool['server_pool_members']

        healthcheck_choices = facade.populate_healthcheck_choices(client)
        environment_choices = [(pool.get('environment').get('id'), pool.get('environment').get('name'))]

        if not pool['pool_created']:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        healthcheck = pool['healthcheck']['healthcheck_type']
        healthcheck_expect = pool['healthcheck']['healthcheck_expect']
        healthcheck_request = pool['healthcheck']['healthcheck_request']
        healthcheck_destination = pool['healthcheck']['destination'].split(':')[1]
        healthcheck_destination = healthcheck_destination if healthcheck_destination != '*' else ''

        lists["action"] = reverse('pool.manage.tab3', args=[id_server_pool])
        lists["id_server_pool"] = id_server_pool
        lists["identifier"] = pool['identifier']
        lists["default_port"] = pool['default_port']
        lists["balancing"] = pool['lb_method']
        lists["servicedownaction"] = pool['servicedownaction']['name']
        lists["max_con"] = pool['default_limit']
        lists["healthcheck"] = healthcheck
        lists["environment"] = pool['environment']['name']

        if request.method == 'POST':

            form = PoolFormV3(
                environment_choices,
                lb_method_choices,
                servicedownaction_choices,
                healthcheck_choices,
                request.POST)

            form_healthcheck = PoolHealthcheckForm(request.POST)

            if form.is_valid() and form_healthcheck.is_valid():
                healthcheck = facade.format_healthcheck(request)
                servicedownaction = facade.format_servicedownaction(client, form)
                pool = format_pool(client, form, members, healthcheck, servicedownaction, int(id_server_pool))
                client.create_pool().deploy_update_pool(pool, id_server_pool)

                messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))
                return redirect(reverse('pool.manage.tab3', args=[id_server_pool]))

        if request.method == 'GET':

            form_initial = {
                'id': id_server_pool,
                'pool_created': pool['pool_created'],
                'environment': environment_id,
                'default_port': pool.get('default_port'),
                'balancing': pool.get('lb_method'),
                'servicedownaction': pool.get('servicedownaction').get('id'),
                'healthcheck': healthcheck,
                'maxcon': pool.get('default_limit'),
                'identifier': pool.get('identifier')
            }
            form = PoolFormV3(
                environment_choices,
                lb_method_choices,
                servicedownaction_choices,
                healthcheck_choices,
                initial=form_initial
            )

            form_initial_hc = {
                'healthcheck_request': healthcheck_request,
                'healthcheck_expect': healthcheck_expect,
                'healthcheck_destination': healthcheck_destination
            }
            form_healthcheck = PoolHealthcheckForm(initial=form_initial_hc)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        form = PoolFormV3(
                environment_choices,
                lb_method_choices,
                servicedownaction_choices,
                healthcheck_choices,
                request.POST)

    lists["form_pool"] = form
    lists["form_healthcheck"] = form_healthcheck
    return render_to_response(POOL_MANAGE_TAB3, lists, context_instance=RequestContext(request))


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

            server_pool_members = facade.format_server_pool_members(request, lists["max_con"])
            server_pools['server_pool_members'] = server_pool_members
            client.create_pool().deploy_update_pool(server_pools, id_server_pool)
            messages.add_message(request, messages.SUCCESS, pool_messages.get('success_update'))
            return redirect(lists['action'])

        if request.method == 'GET':
            lists["pool_members"] = facade.populate_pool_members_by_obj(server_pools['server_pool_members'])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_MANAGE_TAB4, lists, context_instance=RequestContext(request))


def format_pool(client, form, server_pool_members, healthcheck, servicedownaction, pool_id=None):

    pool = dict()
    pool["id"] = pool_id
    pool["identifier"] = str(form.cleaned_data['identifier'])
    pool["default_port"] = int(form.cleaned_data['default_port'])
    pool["environment"] = int(form.cleaned_data['environment'])
    pool["servicedownaction"] = servicedownaction
    pool["lb_method"] = str(form.cleaned_data['balancing'])
    pool["healthcheck"] = healthcheck
    pool["default_limit"] = int(form.cleaned_data['maxcon'])
    pool["server_pool_members"] = server_pool_members
    for member in server_pool_members:
        member['limit'] = pool['default_limit']

    return pool
