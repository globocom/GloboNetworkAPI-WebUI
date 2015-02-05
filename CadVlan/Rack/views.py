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
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from networkapiclient.exception import NetworkAPIClientError, UserNotAuthorizedError #, RackError
from django.contrib import messages
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.templates import RACK_FORM
from django.template.context import RequestContext
from CadVlan.Rack.forms import RackForm
from CadVlan.Util.utility import DataTablePaginator, validates_dict
from networkapiclient.Pagination import Pagination
from django.http import HttpResponseServerError, HttpResponse
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.core.context_processors import request
from django.template.context import Context, RequestContext
from CadVlan.messages import equip_messages, error_messages,\
    request_vip_messages
from CadVlan.Util.converters.util import split_to_array
import json


logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
def rack_form(request):
   
    lists = dict()
    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        if request.method == 'POST':

            form = RackForm(request.POST)
            lists['form'] = form

            if form.is_valid():
                rack_number = form.cleaned_data['rack_number']

            rack_number = '33'
            rack = client.create_rack().insert_rack(rack_number)
            messages.add_message(request, messages.SUCCESS, script_type_messages.get("success_insert"))

        else:

            form = RackForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    return render_to_response(RACK_FORM, lists, context_instance=RequestContext(request))

