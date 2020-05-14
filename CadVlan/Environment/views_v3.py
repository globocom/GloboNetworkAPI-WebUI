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

import logging

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect

from networkapiclient.exception import NetworkAPIClientError

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Environment.business import cache_environment_list
from CadVlan.Environment.business import cache_environment_dc
from CadVlan.Environment.business import cache_environment_logic
from CadVlan.Environment.business import cache_environment_l3
from CadVlan.messages import environment_messages
from CadVlan.templates import ADD_ENVIRONMENT
from CadVlan.templates import AJAX_AUTOCOMPLETE_ENVIRONMENT
from CadVlan.templates import AJAX_AUTOCOMPLETE_VLAN_ENVIRONMENT
from CadVlan.templates import ENVIRONMENT_LIST_V3
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Util.shortcuts import render_to_response_ajax

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
            fields=["id", "name", "min_num_vlan_1", "max_num_vlan_1"],
            search=data)
        env_list = cache_environment_list(envs.get('environments'))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(AJAX_AUTOCOMPLETE_VLAN_ENVIRONMENT,
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

    return render_to_response_ajax(AJAX_AUTOCOMPLETE_ENVIRONMENT, env_list, context_instance=RequestContext(request))


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
        env_list = cache_environment_dc(envs.get('environments_dc'))
    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(AJAX_AUTOCOMPLETE_ENVIRONMENT, env_list, context_instance=RequestContext(request))


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
        env_list = cache_environment_l3(envs.get('l3_environments'))
    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(AJAX_AUTOCOMPLETE_ENVIRONMENT, env_list, context_instance=RequestContext(request))


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
        env_list = cache_environment_logic(envs.get('logic_environments'))
    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(AJAX_AUTOCOMPLETE_ENVIRONMENT, env_list, context_instance=RequestContext(request))


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
                "father_environment": int(request.POST.get('father_env')) if request.POST.get('father_env') else None,
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

    return render_to_response(ADD_ENVIRONMENT, lists, RequestContext(request))


@log
@login_required
def add_dc_environment(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    if request.method == 'POST':
        env = dict(name=request.POST.get('routerName'))

        client.create_api_environment_dc().create([env])
        messages.add_message(request, messages.SUCCESS, environment_messages.get("success_insert"))

    return HttpResponseRedirect(reverse("environment.add"))


@log
@login_required
def add_fisic_environment(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    if request.method == 'POST':
        env = dict(name=request.POST.get('fisicName'))

        client.create_api_environment_l3().create([env])
        messages.add_message(request, messages.SUCCESS, environment_messages.get("success_insert"))

    return HttpResponseRedirect(reverse("environment.add"))


@log
@login_required
def add_logic_environment(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    if request.method == 'POST':
        env = dict(name=request.POST.get('logicName'))

        client.create_api_environment_logic().create([env])
        messages.add_message(request, messages.SUCCESS, environment_messages.get("success_insert"))

    return HttpResponseRedirect(reverse("environment.add"))


@log
@login_required
def list_environments(request):
    """
    Function to list all environments.
    """

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    lists = dict()

    try:
        if request.method == 'GET':
            data = {
                "start_record": 0,
                "end_record": 30000,
                "asorting_cols": ['divisao_dc__nome',
                                  'ambiente_logico__nome',
                                  'grupo_l3__nome'],
                "searchable_columns": [],
                "custom_search": "",
                "extends_search": []
            }

            fields = ['id',
                      'children__basic',
                      'vrf',
                      'name',
                      'configs__details',
                      'vxlan']

            envs = client.create_api_environment().search(search=data, fields=fields)
            lists["envs"] = envs.get("environments")

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ENVIRONMENT_LIST_V3, lists, context_instance=RequestContext(request))
