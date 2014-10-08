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
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.VipRequest.forms import RequestVipFormReal
from CadVlan.templates import POOL_LIST, POOL_FORM
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, PoolError, NomeRoteiroDuplicadoError
from django.contrib import messages
from CadVlan.messages import error_messages, pool_messages
from CadVlan.Util.converters.util import split_to_array, replace_id_to_name
from CadVlan.permissions import POOL_MANAGEMENT, VLAN_MANAGEMENT
from CadVlan.forms import DeleteForm
from CadVlan.Pool.forms import PoolForm
from django.template.defaultfilters import upper

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def list_by_environment_and_equipment(request, id_equipment):

    if request.method == 'GET':

        try:
            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            # Get all scripts from NetworkAPI
            ip_list = client.create_pool().listar_por_equipamento_e_ambiente(id_equipment)
            data = {'lista': ip_list}
            return Response(data)

        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)

    elif request.method == 'POST':

        data = {'success': 'Post Data Success'}
        return Response(data, status=status.HTTP_201_CREATED)


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}])
def list_all(request):

    try:

        lists = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all scripts from NetworkAPI
        pool_list = client.create_pool().listar()

        # Business
        lists['pools'] = pool_list["pool"]




    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_LIST, lists, context_instance=RequestContext(request))


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

        #get environments
        for ambiente in ambient_list['environment_vip']:
            choices.append((ambiente['id'], ambiente['ambiente_p44_txt']))

        env_choices = ([(env['id'], env["divisao_dc_name"] + " - " + env["ambiente_logico_name"] +
                        " - " + env["grupo_l3_name"]) for env in env_list["ambiente"]])
        env_choices.insert(0, (0, "-"))

        #get options_vip
        for opvip in opvip_list['option_vip']:
            #filtering to only Balanceamento
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
