# -*- coding: utf-8 -*-
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
import yaml

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect

from networkapiclient.exception import AmbienteNaoExisteError
from networkapiclient.exception import InvalidParameterError
from networkapiclient.exception import NetworkAPIClientError

from CadVlan import templates
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Environment.business import cache_environment_list
from CadVlan.Environment.business import cache_environment_dc
from CadVlan.Environment.business import cache_environment_logic
from CadVlan.Environment.business import cache_environment_l3
from CadVlan.Environment.forms import IpConfigForm
from CadVlan.messages import environment_messages
from CadVlan.permissions import ENVIRONMENT_MANAGEMENT
from CadVlan.Util.Decorators import has_perm
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Util.shortcuts import render_to_response_ajax
from networkapiclient.Pagination import Pagination
from CadVlan.Util.utility import DataTablePaginator


logger = logging.getLogger(__name__)


@log
@login_required
def ajax_autocomplete_environment_vlan(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    env_list = dict()

    try:
        data = {
            "start_record": 0,
            "end_record": 30000,
            "asorting_cols": [],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }

        envs = client.create_api_environment().search(
            fields=["id", "name", "min_num_vlan_1", "max_num_vlan_1", "min_num_vlan_2", "max_num_vlan_2"],
            search=data)
        env_list = cache_environment_list(envs.get('environments'))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(templates.AJAX_AUTOCOMPLETE_VLAN_ENVIRONMENT,
                                   env_list,
                                   context_instance=RequestContext(request))


@log
@login_required
def ajax_autocomplete_environment(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    env_list = dict()

    try:
        data = {
            "start_record": 0,
            "end_record": 30000,
            "asorting_cols": ["divisao_dc", "ambiente_logico", "grupo_l3"],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }

        envs = client.create_api_environment().search(fields=["id", "name"], search=data)
        env_list = cache_environment_list(envs.get('environments'))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(templates.AJAX_AUTOCOMPLETE_ENVIRONMENT,
                                   env_list,
                                   context_instance=RequestContext(request))


@log
@login_required
def ajax_autocomplete_environment_dc(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    env_list = dict()

    try:
        data = {
            "start_record": 0,
            "end_record": 1000,
            "asorting_cols": ["nome"],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }
        envs = client.create_api_environment_dc().search(search=data)
        # Desativando cache para ambiente de roteamento
        # env_list = cache_environment_dc(envs.get('environments_dc'))

        env_list = dict(list=envs.get('environments_dc'))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(templates.AJAX_AUTOCOMPLETE_ENVIRONMENT,
                                   env_list,
                                   context_instance=RequestContext(request))


@log
@login_required
def ajax_autocomplete_environment_l3(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    env_list = dict()

    try:
        data = {
            "start_record": 0,
            "end_record": 1000,
            "asorting_cols": ["nome"],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }
        envs = client.create_api_environment_l3().search(search=data)
        #Desativando cache para ambiente físico
        #env_list = cache_environment_l3(envs.get('l3_environments'))

        env_list = dict(list=envs.get('l3_environments'))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(templates.AJAX_AUTOCOMPLETE_ENVIRONMENT,
                                   env_list,
                                   context_instance=RequestContext(request))


@log
@login_required
def ajax_autocomplete_environment_logic(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    env_list = dict()

    try:
        data = {
            "start_record": 0,
            "end_record": 1000,
            "asorting_cols": ["nome"],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }
        envs = client.create_api_environment_logic().search(search=data)
        #Desativando cache para ambiente lógico
        # env_list = cache_environment_logic(envs.get('logic_environments'))

        env_list = dict(list=envs.get('logic_environments'))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(templates.AJAX_AUTOCOMPLETE_ENVIRONMENT,
                                   env_list,
                                   context_instance=RequestContext(request))


@log
@login_required
def add_environment(request):
    """
    Function to create a new environment.
    """

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    lists = list()

    try:
        if request.method == 'POST':
            vlan_range1 = request.POST.get('vlan_range', '')
            # range1 = vlan_range1.split('-')
            vlan_range2 = request.POST.get('vlan_range2', '')
            # range2 = vlan_range2.split('-')

            range1 = vlan_range1.split('-')
            if len(range1) > 1:
                range1_begin = int(range1[0])
                range1_end = int(range1[1])
            else:
                range1_begin = None
                range1_end = None
            range2 = vlan_range2.split('-')
            if len(range2) > 1:
                range2_begin = int(range2[0])
                range2_end = int(range2[1])
            else:
                range2_begin = range1_begin
                range2_end = range1_end
                
            env = {
                "grupo_l3": int(request.POST.get('fisic_env')),
                "ambiente_logico": int(request.POST.get('logic_env')),
                "divisao_dc": int(request.POST.get('router_env')),
                "min_num_vlan_1": range1_begin,
                "max_num_vlan_1": range1_end,
                "min_num_vlan_2": range2_begin,
                "max_num_vlan_2": range2_end,
                "default_vrf": int(request.POST.get('vrf')),
                "father_environment": int(request.POST.get('father_env')) \
                    if request.POST.get('father_env') else None,
                'vxlan': True if request.POST.get('vxlan') else False
            }
            client.create_api_environment().create([env])
            messages.add_message(request, messages.SUCCESS, environment_messages.get("success_insert"))

            return HttpResponseRedirect(reverse("environment.list"))
    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(templates.ADD_ENVIRONMENT,
                              lists,
                              RequestContext(request))


@log
@login_required
def add_dc_environment(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    if request.method == 'POST':
        env = dict(name=request.POST.get('routerName'))

        client.create_api_environment_dc().create([env])
        messages.add_message(request,
                             messages.SUCCESS,
                             environment_messages.get("success_insert"))

    return HttpResponseRedirect(reverse("environment.add"))


@log
@login_required
def add_fisic_environment(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    if request.method == 'POST':
        env = dict(name=request.POST.get('fisicName'))

        client.create_api_environment_l3().create([env])
        messages.add_message(request,
                             messages.SUCCESS,
                             environment_messages.get("success_insert"))

    return HttpResponseRedirect(reverse("environment.add"))


@log
@login_required
def add_logic_environment(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    if request.method == 'POST':
        env = dict(name=request.POST.get('logicName'))

        client.create_api_environment_logic().create([env])
        messages.add_message(request,
                             messages.SUCCESS,
                             environment_messages.get("success_insert"))

    return HttpResponseRedirect(reverse("environment.add"))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True, "write": True}])
def allocate_cidr(request, id_environment):

    context = dict()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        net_type_list = client.create_tipo_rede().listar()
        form = IpConfigForm(net_type_list, request.POST or None)

        environment = client.create_api_environment().get(
            [id_environment]).get('environments')[0]

        context["form"] = form
        context["action"] = reverse('environment.configuration.add',
                                    args=[id_environment])
        context["environment"] = environment

        if request.method == 'POST':
            ip_version = request.POST.get('ip_version')

            if str(ip_version) == 'cidr_auto':
                v4 = request.POST.get('v4_auto')
                v6 = request.POST.get('v6_auto')
                network_type = request.POST.get('net_type')
                cidr = list()

                if int(v4):
                    prefix_v4 = request.POST.get('prefixv4')
                    if not prefix_v4:
                        raise Exception("Informe a máscara da subnet da redev4.")

                    cidrv4 = dict(ip_version='v4',
                                  network_type=network_type,
                                  subnet_mask=prefix_v4,
                                  environment=int(id_environment))
                    cidr.append(cidrv4)
                if int(v6):
                    prefix_v6 = request.POST.get('prefixv6')
                    if not prefix_v6:
                        raise Exception("Informe a máscara da subnet da redev6.")
                    cidrv6 = dict(ip_version='v6',
                                  network_type=network_type,
                                  subnet_mask=str(prefix_v6),
                                  environment=int(id_environment))
                    cidr.append(cidrv6)

                if not cidr:
                    raise Exception("Escolha uma das opções abaixo.")

                client.create_api_environment_cidr().post(cidr)
                messages.add_message(request,
                                     messages.SUCCESS,
                                     environment_messages.get(
                                         "success_configuration_insert"))

            elif form.is_valid():
                network = form.cleaned_data['network_validate']
                network_type = form.cleaned_data['net_type']
                prefix = form.cleaned_data['prefix']

                cidr = dict(ip_version=ip_version,
                            network_type=int(network_type),
                            subnet_mask=str(prefix),
                            network=network,
                            environment=int(id_environment))

                client.create_api_environment_cidr().post([cidr])
                messages.add_message(request,
                                     messages.SUCCESS,
                                     environment_messages.get(
                                         "success_configuration_insert"))

            else:
                messages.add_message(request,
                                 messages.ERROR,
                                 environment_messages.get(
                                     "invalid_parameters"))

            context["form"] = IpConfigForm(net_type_list)

    except AmbienteNaoExisteError as e:
        messages.add_message(request, messages.ERROR, e)
        return redirect('environment.list')

    except InvalidParameterError as e:
        messages.add_message(request, messages.ERROR, e)

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except Exception as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(templates.ENVIRONMENT_CIDR,
                              context,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def search_environment(request):
    """
    Function to list all environments.
    """

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    lists = dict()
    try:
        if request.method == 'GET':
            column_index_name_map = {
                0: '',
                1: 'id',
                2: 'divisao_dc__nome',
                3: 'vrf',
                4: 'dcroom__dc__dcname',
                5: ''
            }

            dtp = DataTablePaginator(request, column_index_name_map)

            dtp.build_server_side_list()

            dtp.searchable_columns = [
                'grupo_l3__nome',
                'ambiente_logico__nome',
                'divisao_dc__nome',
                'vrf',
                'dcroom__dc__dcname',
                'dcroom__name'
            ]

            dtp.end_record = 10000

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
            data["asorting_cols"] = ['divisao_dc__nome',
                                     'ambiente_logico__nome',
                                     'grupo_l3__nome']
            data["searchable_columns"] = pagination.searchable_columns
            data["custom_search"] = pagination.custom_search or ""
            data["extends_search"] = []

            fields = ['id',
                      'children__basic',
                      'vrf',
                      'name',
                      'father_environment',
                      'configs__details']

            envs = client.create_api_environment().search(search=data,
                                                          fields=fields)

            lists["envs"] = yaml.safe_load(json.dumps(envs.get('environments')))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(templates.ENVIRONMENT_LIST_V3,
                              lists,
                              context_instance=RequestContext(request))
