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

logger = logging.getLogger(__name__)


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
        lists['form'] = DeleteForm()

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

        # If form was submited
        if request.method == 'POST':

            # Get all script_types from NetworkAPI
            script_type_list = client.create_tipo_roteiro().listar()
            form = PoolForm(script_type_list, request.POST)

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

            # Get all script_types from NetworkAPI
            script_type_list = client.create_tipo_roteiro().listar()

            # New form
            form = PoolForm(script_type_list)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(POOL_FORM, {'form': form}, context_instance=RequestContext(request))
