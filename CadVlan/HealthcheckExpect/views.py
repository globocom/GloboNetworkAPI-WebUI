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

from CadVlan.permissions import HEALTH_CHECK_EXPECT
from CadVlan.messages import healthcheck_messages
from CadVlan.templates import HEALTHCHECKEXPECT_FORM
import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.HealthcheckExpect.forms import HealthckeckExpectForm

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{'permission': HEALTH_CHECK_EXPECT, "write": True}])
def healthcheck_expect_form(request):

    lists = dict()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        data_env = {
            "start_record": 0,
            "end_record": 5000,
            "asorting_cols": [],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }
        ambientes = client.create_api_environment().search(search=data_env)

        if request.method == 'POST':

            form = HealthckeckExpectForm(ambientes, request.POST)
            lists['form'] = form

            if form.is_valid():

                match_list = form.cleaned_data['match_list']
                expect_string = form.cleaned_data['expect_string']
                environment_id = form.cleaned_data['environment']

                client.create_ambiente().add_healthcheck_expect(
                    environment_id, expect_string, match_list)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    healthcheck_messages.get('success_create'))

                lists['form'] = HealthckeckExpectForm(ambientes)
        else:
            lists['form'] = HealthckeckExpectForm(ambientes)

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(HEALTHCHECKEXPECT_FORM,
                              lists,
                              context_instance=RequestContext(request))
