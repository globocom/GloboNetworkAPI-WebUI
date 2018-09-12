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
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Environment.business import cache_environment_list
from CadVlan.templates import AJAX_AUTOCOMPLETE_ENVIRONMENT
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Util.shortcuts import render_to_response_ajax


logger = logging.getLogger(__name__)


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
            "asorting_cols": [],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }

        envs = client.create_api_environment().search(fields=["name", "min_num_vlan_1", "max_num_vlan_1"], search=data)
        env_list = cache_environment_list(envs.get('environments'))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(AJAX_AUTOCOMPLETE_ENVIRONMENT, env_list, context_instance=RequestContext(request))
