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
    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()

        if request.method == "GET":

            if request.GET.__contains__('search_equipment'):

                search_form = request.GET.get('search_equipment')
                equipment = client.create_equipamento().listar_por_nome(search_form)['equipamento']
                init_map = {'equip_name': equipment['nome'], 'equip_id': equipment['id']}

                equip_interface_list = client.create_interface().list_all_by_equip(equipment['id'])

                lists['search_form'] = search_form

                if equip_interface_list.has_key('interfaces'):
                    lists['equip_interface'] = equip_interface_list['interfaces']
                if equipment['id_tipo_equipamento'] == str(PATCH_PANEL_ID):
                    lists['pp'] = "1"

        return render_to_response(LIST_EQUIPMENT_INTERFACES, lists, RequestContext(request))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('home')