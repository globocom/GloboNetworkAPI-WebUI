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
from CadVlan.Util.Decorators import log, login_required, has_perm, access_external
from CadVlan.VipRequest.forms import RequestVipFormReal
from django.views.decorators.csrf import csrf_exempt
from CadVlan.templates import POOL_LIST, POOL_FORM, AJAX_IPLIST_EQUIPMENT_REAL_SERVER, AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML,POOL_DATATABLE
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import loader
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, NomeRoteiroDuplicadoError
from django.contrib import messages
from CadVlan.messages import error_messages, pool_messages
from CadVlan.permissions import POOL_MANAGEMENT, VLAN_MANAGEMENT
from CadVlan.forms import DeleteForm
from CadVlan.Pool.forms import PoolForm
from django.template.defaultfilters import upper
from CadVlan.Util.utility import DataTablePaginator
from networkapiclient.Pagination import Pagination
from CadVlan.Util.utility import DataTablePaginator, validates_dict, clone, \
    get_param_in_request, IP_VERSION, is_valid_int_param

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}])
def list_all(request):

    return render_to_response(
        POOL_LIST,
        {'form': DeleteForm()},
        context_instance=RequestContext(request)
    )


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}])
def datatable(request):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        columnIndexNameMap = {
            0: '',
            1: 'identifier',
            2: 'default_port',
            3: 'healthcheck',
            4: ''
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

        pools = client.create_pool().list_all(pagination)

        return dtp.build_response(pools["pools"], pools["total"], POOL_DATATABLE, request)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True, "write": True}])
def add_form(request):

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all script_types from NetworkAPI
        ambient_list = client.create_environment_vip().list_all()
        env_list = client.create_ambiente().list_all()
        opvip_list = client.create_option_vip().get_all()

        choices = []
        choices_opvip = []
        choices_healthcheck = []

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
            elif opvip['tipo_opcao'] == 'HealthCheck':
                choices_healthcheck.append((opvip['id'], opvip['nome_opcao_txt']))

        # If form was submited
        if request.method == 'POST':

            form = PoolForm(choices, request.POST)

            if form.is_valid():

                # Data
                name = upper(form.cleaned_data['name'])
                script_type = form.cleaned_data['script_type']
                description = form.cleaned_data['description']

                try:
                    # Business
                    client.create_roteiro().inserir(
                        script_type, name, description)
                    messages.add_message(
                        request, messages.SUCCESS, pool_messages.get("success_insert"))

                    return redirect('script.list')
                except NomeRoteiroDuplicadoError, e:
                    messages.add_message(request, messages.ERROR, e)

        else:
            # New form
            form = PoolForm(env_choices, choices_opvip, choices_healthcheck)
            form_real = RequestVipFormReal()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_FORM, {'form': form, 'form_real': form_real}, context_instance=RequestContext(request))


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

    # Returns Json
    return HttpResponse(loader.render_to_string(AJAX_IPLIST_EQUIPMENT_REAL_SERVER_HTML,
                        lists, context_instance=RequestContext(request)), status=status_code)
