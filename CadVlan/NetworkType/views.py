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
from CadVlan.permissions import NETWORK_TYPE_MANAGEMENT
from CadVlan.messages import type_network_messages
from CadVlan.templates import NETWORKTYPE_FORM
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.NetworkType.forms import TipoRedeForm

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{'permission': NETWORK_TYPE_MANAGEMENT, "write": True}])
def network_type_form(request):

    lists = dict()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        if request.method == 'POST':

            form = TipoRedeForm(request.POST)
            lists['form'] = form

            if form.is_valid():

                name = form.cleaned_data['name']

                client.create_tipo_rede().inserir(name)
                messages.add_message(
                    request, messages.SUCCESS, type_network_messages.get('success_create'))

                lists['form'] = TipoRedeForm()

        # GET METHOD
        else:
            lists['form'] = TipoRedeForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(NETWORKTYPE_FORM, lists, context_instance=RequestContext(request))
