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
from CadVlan.VipRequest.forms import RequestVipFormReal
from django.views.decorators.csrf import csrf_exempt
from CadVlan.templates import POOL_LIST, POOL_FORM, POOL_EDIT, POOL_SPM_DATATABLE, \
    POOL_DATATABLE, AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import loader
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.messages import error_messages, pool_messages
from CadVlan.permissions import POOL_MANAGEMENT, VLAN_MANAGEMENT, \
    POOL_REMOVE_SCRIPT, POOL_CREATE_SCRIPT
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
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}])
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
            5: 'limit',
            6: 'healthcheck',
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
@has_perm([{"permission": POOL_MANAGEMENT, "read": True, "write": True}])
def add_form(request):

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all script_types from NetworkAPI
        ambient_list = client.create_environment_vip().list_all()
        env_list = client.create_ambiente().list_all()
        opvip_list = client.create_option_vip().get_all()
        healthcheck_list = client.create_pool().list_healthchecks()

        choices = []
        choices_opvip = []
        choices_healthcheck = []

        for healthcheck in healthcheck_list['healthchecks']:
            choices_healthcheck.append((healthcheck['id'], healthcheck['identifier']))

        # get environments
        for ambiente in ambient_list['environment_vip']:
            choices.append((ambiente['id'], ambiente['ambiente_p44_txt']))

        env_choices = ([(env['id'], env["divisao_dc_name"] + " - " + env["ambiente_logico_name"] +
                        " - " + env["grupo_l3_name"]) for env in env_list["ambiente"]])
        env_choices.insert(0, (0, "-"))

        # get options_vip
        for opvip in opvip_list['option_vip']:
            # filtering to only Balanceamento
            if opvip['tipo_opcao'] == 'Balanceamento':
                choices_opvip.append((opvip['id'], opvip['nome_opcao_txt']))

        # If form was submited
        if request.method == 'POST':

            form = PoolForm(env_choices, choices_opvip, choices_healthcheck, request.POST)
            realform = RequestVipFormReal(request.POST)

            if form.is_valid() and realform.is_valid():

                id_ips = request.POST.getlist('id_ip')
                ips = request.POST.getlist('ip')

                ip_list_full = list()

                for i in range(len(ips)):
                    ip_list_full.append({'id': id_ips[i], 'ip': ips[i]})

                # Data
                identifier = form.cleaned_data['identifier']
                default_port = form.cleaned_data['default_port']
                environment = form.cleaned_data['environment']
                balancing = form.cleaned_data['balancing']
                healthcheck = form.cleaned_data['healthcheck']
                maxcom = realform.cleaned_data['maxcom']

                id_equips = request.POST.getlist('id_equip')
                priorities = request.POST.getlist('priority')
                ports_reals = request.POST.getlist('ports_real_reals')

                client.create_pool().inserir(
                    identifier, default_port, environment,
                    balancing, healthcheck, maxcom, ip_list_full,
                    id_equips, priorities, ports_reals
                )

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    pool_messages.get('success_insert')
                )

                return redirect('pool.list')
        else:
            # New form
            form = PoolForm(env_choices, choices_opvip, choices_healthcheck)
            form_real = RequestVipFormReal()
            action = reverse('pool.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_FORM, {'form': form, 'form_real': form_real, 'action': action}, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True, "write": True}])
def edit_form(request, id_server_pool):

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get pool infos
        pool = client.create_pool().get_by_pk(id_server_pool)

        env_list = client.create_ambiente().list_all()
        opvip_list = client.create_option_vip().get_all()
        healthcheck_list = client.create_pool().list_healthchecks()

        choices_opvip = []
        choices_healthcheck = []

        for healthcheck in healthcheck_list['healthchecks']:
            choices_healthcheck.append((healthcheck['id'], healthcheck['identifier']))


        env_choices = ([(env['id'], env['divisao_dc_name'] + " - " + env['ambiente_logico_name'] +
                        " - " + env['grupo_l3_name']) for env in env_list['ambiente']])
        env_choices.insert(0, (0, "-"))

        # get options_vip
        for opvip in opvip_list['option_vip']:
            # filtering to only Balanceamento
            if opvip['tipo_opcao'] == 'Balanceamento':
                choices_opvip.append((opvip['id'], opvip['nome_opcao_txt']))

        # If form was submited
        if request.method == 'POST':

            form = PoolForm(env_choices, choices_opvip, choices_healthcheck, request.POST)
            realform = RequestVipFormReal(request.POST)

            if form.is_valid() and realform.is_valid():

                id_ips = request.POST.getlist('id_ip')
                ips = request.POST.getlist('ip')

                ip_list_full = list()

                for i in range(len(ips)):
                    ip_list_full.append({'id': id_ips[i], 'ip': ips[i]})

                # Data
                identifier = form.cleaned_data['identifier']
                default_port = form.cleaned_data['default_port']
                environment = form.cleaned_data['environment']
                balancing = form.cleaned_data['balancing']
                healthcheck = form.cleaned_data['healthcheck']
                maxcom = realform.cleaned_data['maxcom']

                id_equips = request.POST.getlist('id_equip')
                priorities = request.POST.getlist('priority')
                ports_reals = request.POST.getlist('ports_real_reals')

                client.create_pool().update(
                    id_server_pool, identifier, default_port, environment,
                    balancing, healthcheck, maxcom, ip_list_full,
                    id_equips, priorities, ports_reals
                )

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    pool_messages.get('success_update')
                )

                return redirect('pool.list')
        else:
            # New form
            server_pool = dict()
            server_pool_members = dict()
            server_pool = pool['server_pool']
            server_pool_members = pool['server_pool_members']

            for spm in server_pool_members:
                nome_equipamento = client.create_pool().get_equip_by_ip(spm['ip']['id'])
                spm.update({'equipamento': nome_equipamento})

            poolform_initial = {
                'identifier': server_pool.get('identifier'),
                'default_port': server_pool.get('default_port'),
                'environment': server_pool.get('environment')['id'],
                'balancing': '',
                'healthcheck': server_pool.get('healthcheck')['id'],
            }

            form = PoolForm(
                env_choices,
                choices_opvip,
                choices_healthcheck,
                initial=poolform_initial
            )

            form_real = RequestVipFormReal(
                initial={
                    'maxcom': pool['server_pool_members'][0]['limit']
                }
            )

            action = reverse('pool.edit.form', args=[id_server_pool])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    context_attrs = {
        'form': form,
        'form_real': form_real,
        'action': action,
        'reals': server_pool_members,
        'id_server_pool': id_server_pool
    }

    return render_to_response(
        POOL_EDIT,
        context_attrs,
        context_instance=RequestContext(request)
    )


@csrf_exempt
@access_external()
@log
def ajax_modal_ip_real_server_external(request, form_acess, client):
    return modal_ip_list_real(request, client)


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True, "write": True}])
def ajax_modal_ip_real_server(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return modal_ip_list_real(request, client_api)


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
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}])
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
@has_perm([{"permission": POOL_REMOVE_SCRIPT, "read": True}])
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
@has_perm([{"permission": POOL_CREATE_SCRIPT, "read": True}])
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
