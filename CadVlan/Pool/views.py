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
    find_servicedownaction_object
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

        pools = client.create_pool().get_poolmember_state(
            [id_server_pool],
            0
            # int(checkstatus)
        )

        logger.info(pools)

        return dtp.build_response(
            pools["server_pools"][0]["server_pool_members"],
            len(pools["server_pools"][0]["server_pool_members"]),
            POOL_SPM_DATATABLE,
            request
        )

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

        column_index_name_map = {0: '', 1: 'id', 2: 'ip', 3: 'descricao_ipv4',
                              4: 'descricao_ipv6', 5: 'ambiente', 6: 'valido', 7: 'criado', 8: ''}

        dtp = DataTablePaginator(request, column_index_name_map)

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
    """
        New Pool(form and save post)
    """
    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all script_types from NetworkAPI
        expectstring_choices = populate_expectstring_choices(client)
        enviroments_choices = populate_enviroments_choices(client)
        optionsvips_choices = populate_optionsvips_choices(client)
        servicedownaction_choices = populate_servicedownaction_choices(client)

        form = PoolForm(
            enviroments_choices,
            optionsvips_choices,
            servicedownaction_choices)

        action = reverse('pool.add.form')
        label_tab = u'Cadastro de Pool'

        pool_members = list()
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
            default_limit = request.POST.get('id_max_con')

            # Rebuilding the reals list so we can display it again to the user
            # if it raises an error
            pool_members = populate_pool_members_by_lists(
                client,
                nome_equips,
                id_equips,
                priorities,
                weight,
                ports_reals,
                ips,
                id_ips,
                id_pool_member,
                default_limit
            )

            optionspool_choices = populate_optionspool_choices(
                client, environment)

            form = PoolForm(
                enviroments_choices,
                optionsvips_choices,
                servicedownaction_choices,
                optionspool_choices,
                request.POST
            )

            if form.is_valid():
                # Data form

                pool = {
                    "id": None,
                    "identifier": form.cleaned_data['identifier'],
                    "default_port": form.cleaned_data['default_port'],
                    "environment": environment,
                    "servicedownaction": form.cleaned_data['servicedownaction'],
                    "lb_method": form.cleaned_data['balancing'],
                    "healthcheck": {
                        'id': None,
                        'identifier': '',
                        'healthcheck_type': request.POST.get('health_check'),
                        'healthcheck_request': request.POST.get('health_check_request'),
                        'healthcheck_expect': request.POST.get('expect'),
                        'destination': '*:%s' % (request.POST.get('destination') or '*')
                    },
                    "default_limit": default_limit,
                    "server_pool_members": pool_members,
                    "pool_created": False
                }
                if request.POST.get('health_check') in ['HTTP', 'HTTPS']:
                    pool['healthcheck']['healthcheck_request'] = ''
                    pool['healthcheck']['healthcheck_expect'] = ''
                    pool['healthcheck']['destination'] = ''

                client.create_pool().save_pool(pool)

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    pool_messages.get('success_insert'))

                return redirect('pool.list')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(
        POOL_FORM,
        {
            'form': form,
            'action': action,
            'pool_members': pool_members,
            'expect_strings': expectstring_choices,
            'label_tab': label_tab,
            'pool_created': False
        },
        context_instance=RequestContext(request))


@log
@login_required
@has_perm([
    {"permission": POOL_MANAGEMENT, "write": True, "read": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True}]
)
def edit_form(request, id_server_pool):

    try:
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        enviroments_choices = populate_enviroments_choices(client)
        servicedownaction_choices = populate_servicedownaction_choices(client)
        expectstring_choices = populate_expectstring_choices(client)
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

            optionspool_choices = populate_optionspool_choices(
                client, environment)

            form = PoolForm(enviroments_choices, optionsvips_choices,
                            servicedownaction_choices, optionspool_choices, request.POST)

            if form.is_valid():
                # Data form
                id = form.cleaned_data['id']
                identifier = form.cleaned_data['identifier']
                default_port = form.cleaned_data['default_port']
                environment = form.cleaned_data['environment']
                balancing = form.cleaned_data['balancing']
                max_con = form.cleaned_data['max_con']
                servicedownaction = form.cleaned_data['servicedownaction']
                servicedownaction_id = find_servicedownaction_id(
                    client, servicedownaction)

                client.create_pool().save(id, identifier, default_port, environment,
                                          balancing, healthcheck_type, healthcheck_expect,
                                          healthcheck_request, max_con, ip_list_full, nome_equips,
                                          id_equips, priorities, weight, ports_reals, id_pool_member, servicedownaction_id)

                messages.add_message(
                    request, messages.SUCCESS, pool_messages.get('success_update'))

                return redirect(action)

        else:
            pool = client.create_pool().get_pool(id_server_pool)
            pool = pool['server_pool']

            pool_created = pool['pool_created']

            optionspool_choices = [('', '-')]
            if pool['environment']:
                optionspool_choices = populate_optionspool_choices(client, pool['environment'])

            environment = pool['environment'] if pool['environment'] else None

            healthcheck_expect = pool['healthcheck']['healthcheck_expect'] \
                if pool['healthcheck'] else ''

            healthcheck_request = pool['healthcheck']['healthcheck_request'] \
                if pool['healthcheck'] else ''

            health_check = pool['healthcheck']['healthcheck_type'] \
                if pool['healthcheck'] else None

            health_destination = pool['healthcheck']['destination'].split('*')[1] \
                if pool['healthcheck'] else None

            initial_pool = {
                'id': pool['id'],
                'identifier': pool['identifier'],
                'default_port': pool['default_port'],
                'environment': environment,
                'balancing': pool['lb_method'],
                'health_check': health_check,
                'max_con': pool['default_limit'],
                'servicedownaction': pool['servicedownaction']
            }

            pool_members = populate_pool_members_by_obj(
                client, pool['server_pool_members'])

            form = PoolForm(enviroments_choices, optionsvips_choices,
                            servicedownaction_choices, optionspool_choices, initial=initial_pool)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    if pool_created:
        return redirect(reverse('pool.manage.tab1', args=[id_server_pool]))

    return render_to_response(
        POOL_FORM,
        {
            'form': form,
            'action': action,
            'pool_members': pool_members,
            'expect_strings': expectstring_choices,
            'healthcheck_expect': healthcheck_expect,
            'healthcheck_request': healthcheck_request,
            'label_tab': label_tab,
            'pool_created': pool_created,
            'id_server_pool': id_server_pool
        },
        context_instance=RequestContext(request))


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

    lists = {
        'msg': str(),
        'ips': []
    }

    ips = {}
    status_code = 200

    ambiente = get_param_in_request(request, 'id_environment')
    equip_name = get_param_in_request(request, 'equip_name')

    try:
        # Valid Equipament
        equip = client_api.create_equipamento().listar_por_nome(
            equip_name).get("equipamento")
        ips_list = client_api.create_pool().get_available_ips_to_add_server_pool(
            equip_name, ambiente)
    except NetworkAPIClientError, e:
        logger.error(e)
        status_code = 500
        return HttpResponse(json.dumps({'message': e.error, 'status': 'error'}),
                            status=status_code,
                            content_type='application/json')

    if not ips_list['list_ipv4'] and not ips_list['list_ipv6']:
        return HttpResponse(json.dumps({'message': u'Esse equipamento não tem nenhum IP que '
                                                   u'possa ser utilizado nos pools desse ambiente.',
                                        'status': 'error'}),
                            status=status_code,
                            content_type='application/json')

    ips['list_ipv4'] = ips_list['list_ipv4']
    ips['list_ipv6'] = ips_list['list_ipv6']

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
        opcoes_pool = client_api.create_pool().get_opcoes_pool_by_ambiente(
            ambiente)

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

            client.create_pool().delete_pool(ids)

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

            pools = client.create_pool().get_poolmember_state(ids)
            client.create_pool().remove(pools['pools'])

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

            pools = client.create_pool().get_poolmember_state(ids)
            logger.error(pools['pools'])
            client.create_pool().create(pools['pools'])

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
def status_change(request):
    """
        Enable Pool Member Running Script
    """
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        id_server_pool = request.POST.get('id_server_pool')
        ids = request.POST.get('ids')
        action = request.POST.get('action')

        if id_server_pool and ids:

            pools = client.create_pool().get_poolmember_state([id_server_pool])
            for i, pool in enumerate(pools['pools']):
                pl = pool['server_pool_members']
                pools['pools'][i]['server_pool_members'] = []
                for j, p in enumerate(pl):
                    member_status = list(bin(p['member_status']))
                    if action[-2] != 'x':
                        member_status[-2] = action[-2]
                    else:
                        member_status[-1] = action[-1]

                    member_status = int(''.join(member_status), 2)

                    if member_status != p['member_status'] and str(p['id']) in ids.split(';'):
                        p['member_status'] = member_status
                        pools['pools'][i]['server_pool_members'].append(p)

            if len(pools['pools'][i]['server_pool_members']) > 0:
                client.create_pool().poolmember_state(pools['pools'])
            messages.add_message(
                request, messages.SUCCESS, pool_messages.get('success_status_change'))
        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect(reverse('pool.manage.tab2', args=[id_server_pool]))


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
            messages.add_message(
                request, messages.SUCCESS, pool_messages.get('success_enable'))
        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

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

        pool = client.create_pool().get_by_pk(id_server_pool)

        environment_desc = None
        if pool['server_pool']['environment']:
            environment = client.create_ambiente().buscar_por_id(
                pool['server_pool']['environment']['id'])
            environment_desc = environment['ambiente']['ambiente_rede']

        health_check = pool['server_pool']['healthcheck']['healthcheck_type'] \
            if pool['server_pool']['healthcheck'] else None

        identifier = pool['server_pool']['identifier']
        default_port = pool['server_pool']['default_port']
        balancing = pool['server_pool']['lb_method']
        servicedownaction = pool['server_pool']['servicedownaction'][u'name']
        max_con = pool['server_pool']['default_limit']

        pool_created = pool['server_pool']['pool_created']
        if not pool_created:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        return render_to_response(POOL_MANAGE_TAB1, {'id_server_pool': id_server_pool, 'health_check': health_check,
                                                     'environment': environment_desc, 'identifier': identifier,
                                                     'default_port': default_port, 'balancing': balancing,
                                                     'max_con': max_con, 'servicedownaction': servicedownaction},
                                  context_instance=RequestContext(request))

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

        pool = client.create_pool().get_by_pk(id_server_pool)

        environment_desc = None
        if pool['server_pool']['environment']:
            environment = client.create_ambiente().buscar_por_id(
                pool['server_pool']['environment']['id'])
            environment_desc = environment['ambiente']['ambiente_rede']

        health_check = pool['server_pool']['healthcheck']['healthcheck_type'] \
            if pool['server_pool']['healthcheck'] else None

        identifier = pool['server_pool']['identifier']
        default_port = pool['server_pool']['default_port']
        balancing = pool['server_pool']['lb_method']
        servicedownaction = pool['server_pool']['servicedownaction'][u'name']
        max_con = pool['server_pool']['default_limit']

        pool_created = pool['server_pool']['pool_created']
        if not pool_created:
            return redirect(reverse('pool.edit.form', args=[id_server_pool]))

        return render_to_response(POOL_MANAGE_TAB2, {'id_server_pool': id_server_pool, 'health_check': health_check,
                                                     'environment': environment_desc, 'identifier': identifier,
                                                     'default_port': default_port, 'balancing': balancing,
                                                     'max_con': max_con, 'servicedownaction': servicedownaction},
                                  context_instance=RequestContext(request))

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

            optionspool_choices = populate_optionspool_choices(
                client, environment)

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

        # combos
        enviroments_choices = populate_enviroments_choices(client)
        optionsvips_choices = populate_optionsvips_choices(client)
        expectstring_choices = populate_expectstring_choices(client)
        servicedownaction_choices = populate_servicedownaction_choices(client)

        action = reverse('pool.manage.tab3', args=[id_server_pool])

        pool = client.create_pool().get_by_pk(id_server_pool)

        # redirect
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
            healthcheck_destination = '*:%s' % (request.POST.get('destination') or '*')

            if healthcheck_type != 'HTTP' and healthcheck_type != 'HTTPS':
                healthcheck_expect = ''
                healthcheck_request = ''
                healthcheck_destination = ''

            healthcheck_destination

            optionspool_choices = populate_optionspool_choices(
                client, environment)

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
                sv_servicedownaction_obj = find_servicedownaction_object(
                    client, sv_servicedownaction)

                environment = client.create_ambiente().buscar_por_id(sv_environment)

                pool = client.create_pool().get_poolmember_state([sv_id_server_pool])

                pool["server_pools"][0]["identifier"] = sv_identifier
                pool["server_pools"][0]["default_port"] = sv_default_port
                pool["server_pools"][0]["environment"] = environment['ambiente']
                pool["server_pools"][0]["healthcheck"]['healthcheck_type'] = healthcheck_type
                pool["server_pools"][0]["healthcheck"]['healthcheck_request'] = healthcheck_request
                pool["server_pools"][0]["healthcheck"]['healthcheck_expect'] = healthcheck_expect
                pool["server_pools"][0]["healthcheck"]['healthcheck_destination'] = healthcheck_destination
                pool["server_pools"][0]["default_limit"] = sv_max_con
                pool["server_pools"][0]["lb_method"] = sv_balancing
                pool["server_pools"][0]["servicedownaction"] = sv_servicedownaction_obj

                for i, m in enumerate(pool["server_pools"][0]["server_pool_members"]):
                    pool["server_pools"][0]["server_pool_members"][i]['limit'] = sv_max_con

                client.create_pool().save_pool(pool["server_pools"])

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

            optionspool_choices = populate_optionspool_choices(
                client, environment)

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
def manage_tab4_(request, id_server_pool):

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
            environment = client.create_ambiente().buscar_por_id(
                pool['server_pool']['environment']['id'])
            environment_desc = environment['ambiente']['ambiente_rede']

        health_check = pool['server_pool']['healthcheck']['healthcheck_type'] \
            if pool['server_pool']['healthcheck'] else None

        identifier = pool['server_pool']['identifier']
        default_port = pool['server_pool']['default_port']
        balancing = pool['server_pool']['lb_method']
        servicedownaction = pool['server_pool']['servicedownaction'][u'name']
        max_con = pool['server_pool']['default_limit']
        environment = pool['server_pool']['environment'][
            'id'] if pool['server_pool']['environment'] else ''

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

            messages.add_message(
                request, messages.SUCCESS, pool_messages.get('success_update'))

            return redirect(action)
        else:
            pool_members = populate_pool_members_by_obj(
                client, pool['server_pool_members'])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_MANAGE_TAB4, {'id_server_pool': id_server_pool, 'health_check': health_check,
                                                 'environment_desc': environment_desc, 'identifier': identifier,
                                                 'default_port': default_port, 'balancing': balancing,
                                                 'max_con': max_con, 'pool_members': pool_members, 'action': action,
                                                 'environment': environment, 'servicedownaction': servicedownaction},
                              context_instance=RequestContext(request))


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

        action = reverse('pool.manage.tab4', args=[id_server_pool])
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

        identifier = pool['server_pool']['identifier']
        default_port = pool['server_pool']['default_port']
        balancing = pool['server_pool']['lb_method']
        servicedownaction = pool['server_pool']['servicedownaction'][u'name']
        max_con = pool['server_pool']['default_limit']
        environment = pool['server_pool']['environment'][
            'id'] if pool['server_pool']['environment'] else ''

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

            pool = client.create_pool().get_poolmember_state([id_server_pool])

            members = list()
            for idx, spm in enumerate(id_equips):

                members.append({
                    "equipment_id": '',
                    "equipment_name": '',
                    "healthcheck": '',
                    "id": '',
                    "identifier": '',
                    "ip": dict(),
                    "ipv6": '',
                    "last_status_update": '',
                    "last_status_update_formated": '',
                    "limit": '',
                    "member_status": '',
                    "port_real": '',
                    "priority": '',
                    "server_pool": dict(),
                    "weight": ''})

                members[idx]['id'] = id_pool_member[idx]
                members[idx]['equipment_id'] = id_equips[idx]
                members[idx]['identifier'] = nome_equips[idx]
                members[idx]['equipment_name'] = nome_equips[idx]
                members[idx]['priority'] = priorities[idx]
                members[idx]['port_real'] = ports_reals[idx]
                members[idx]['weight'] = weight[idx]
                members[idx]['limit'] = pool["pools"][0]['server_pool']['default_limit']

                if len(ips[idx]) <= 15:
                    ipv4 = client.create_ip().get_ipv4(id_ips[idx])
                    members[idx]['ip']['ip_formated'] = ips[idx]
                    members[idx]['ip']['id'] = ipv4['ipv4']['id']
                    members[idx]['ip']['networkipv4'] = ipv4['ipv4']['networkipv4']
                    members[idx]['ip']['oct4'] = ipv4['ipv4']['oct4']
                    members[idx]['ip']['oct3'] = ipv4['ipv4']['oct3']
                    members[idx]['ip']['oct2'] = ipv4['ipv4']['oct2']
                    members[idx]['ip']['oct1'] = ipv4['ipv4']['oct1']
                    members[idx]['ip']['descricao'] = ipv4['ipv4']['descricao']
                else:
                    ipv6 = client.create_ip().get_ipv6(id_ips[idx])
                    members[idx]['ipv6']['ip_formated'] = ips[idx]
                    members[idx]['ipv6']['id'] = ipv6['id']
                    members[idx]['ipv6']['networkipv6'] = ipv6['networkipv6']
                    members[idx]['ipv6']['block1'] = ipv6['ipv6']['block1']
                    members[idx]['ipv6']['block2'] = ipv6['ipv6']['block2']
                    members[idx]['ipv6']['block3'] = ipv6['ipv6']['block3']
                    members[idx]['ipv6']['block4'] = ipv6['ipv6']['block4']
                    members[idx]['ipv6']['block5'] = ipv6['ipv6']['block5']
                    members[idx]['ipv6']['block6'] = ipv6['ipv6']['block6']
                    members[idx]['ipv6']['block7'] = ipv6['ipv6']['block7']
                    members[idx]['ipv6']['block8'] = ipv6['ipv6']['block8']
                    members[idx]['ipv6']['description'] = ipv6['ipv6']['description']

                members[idx]['server_pool'] = pool["pools"][0]['server_pool']

            pool["pools"][0]['server_pool_members'] = members
            pool_members = populate_pool_members_by_obj(
                client, pool["pools"][0]['server_pool_members'])
            client.create_pool().save_pool(pool["pools"])

            messages.add_message(
                request, messages.SUCCESS, pool_messages.get('success_update'))

            return redirect(action)
        else:
            pool_members = populate_pool_members_by_obj(
                client, pool['server_pool_members'])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_MANAGE_TAB4, {'id_server_pool': id_server_pool, 'health_check': health_check,
                                                 'environment_desc': environment_desc, 'identifier': identifier,
                                                 'default_port': default_port, 'balancing': balancing,
                                                 'max_con': max_con, 'pool_members': pool_members, 'action': action,
                                                 'environment': environment, 'servicedownaction': servicedownaction},
                              context_instance=RequestContext(request))
