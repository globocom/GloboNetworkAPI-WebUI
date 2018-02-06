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

from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.settings import PATCH_PANEL_ID
from CadVlan.templates import LIST_EQUIPMENT_INTERFACES
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required

from networkapiclient.exception import NetworkAPIClientError


logger = logging.getLogger(__name__)


@log
@login_required
def list_equipment_interfaces(request):

    lists = dict()
    interface_list = list()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        if request.method == "GET":

            if request.GET.__contains__('search_equipment'):

                search_form = request.GET.get('search_equipment')

                data = dict()
                data["start_record"] = 0
                data["end_record"] = 25
                data["asorting_cols"] = []
                data["searchable_columns"] = ["nome"]
                data["custom_search"] = search_form
                data["extends_search"] = []

                search_equipment = client.create_api_equipment().search(fields=['id','name'],
                                                                        search=data)

                equipments = search_equipment.get('equipments')

                if not equipments:
                    raise Exception ("Equipment Does Not Exist.")

                if len(equipments)==1:
                    data["searchable_columns"] = ["equipamento__id"]
                    data["custom_search"] = equipments[0].get('id')
                    search_interface = client.create_api_interface_request().search(fields=['id',
                                                                                          'interface',
                                                                                          'equipamento__basic',
                                                                                          'native_vlan',
                                                                                          'tipo__details',
                                                                                          'channel__basic',
                                                                                          'ligacao_front__basic',
                                                                                          'ligacao_back__basic'],
                                                                                  search=data)
                    interface_list = search_interface.get('interfaces')

                lists['equip_interface'] = interface_list
                lists['search_form'] = search_form

        return render_to_response(LIST_EQUIPMENT_INTERFACES, lists, RequestContext(request))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return render_to_response(LIST_EQUIPMENT_INTERFACES, lists, RequestContext(request))
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return render_to_response(LIST_EQUIPMENT_INTERFACES, lists, RequestContext(request))