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
from networkapiclient.exception import EnvironmentVipNotFoundError, InvalidParameterError, NetworkAPIClientError, UserNotAuthorizedError, NumeroRackDuplicadoError 
from django.contrib import messages
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.templates import RACK_FORM, RACK_VIEW_AJAX
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
from CadVlan.messages import auth_messages, equip_messages, error_messages, rack_messages
from CadVlan.Util.converters.util import split_to_array

import json


logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
def rack_form(request):
   
    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        if request.method == 'POST':

            form = RackForm(request.POST)
            
            if form.is_valid():
                rack_number = form.cleaned_data['rack_number']
                mac_sw1 = form.cleaned_data['mac_address_sw1']
                mac_sw2 = form.cleaned_data['mac_address_sw2']
                mac_ilo = form.cleaned_data['mac_address_ilo']
                nome_sw1 = form.cleaned_data['nome_sw1']
                nome_sw2 = form.cleaned_data['nome_sw2']
                nome_ilo = form.cleaned_data['nome_ilo']

                # Validacao: MAC 
                if not mac_sw1=='':
                    if not (mac_sw1.count(':') == 5):
                        raise InvalidParameterError(u'Endereco MAC invalido. Formato: FF:FF:FF:FF:FF:FF') 
                    mac_sw1_val = mac_sw1.split(':')
                    if ((len(mac_sw1_val[0])>2) or (len(mac_sw1_val[1])>2) or (len(mac_sw1_val[2])>2) or (len(mac_sw1_val[3])>2) or (len(mac_sw1_val[4])>2) or (len(mac_sw1_val[5])>2)):
                        raise InvalidParameterError(u'Endereco MAC invalido. Formato: FF:FF:FF:FF:FF:FF') 

                id_sw1 = None
                if not nome_sw1=='':
                    try:
                        equip = client.create_equipamento().listar_por_nome(nome_sw1)
                        equip = equip.get('equipamento')
                        id_sw1 = equip['id']
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)                
                        return redirect('rack.form')

                id_sw2 = None
                if not nome_sw2=='':
                    try:
                        equip2 = client.create_equipamento().listar_por_nome(nome_sw2)
                        equip2 = equip2.get('equipamento')
                        id_sw2 = equip2['id']
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)

                id_ilo = None
                if not nome_ilo=='':
                    try:
                        equip_ilo = client.create_equipamento().listar_por_nome(nome_ilo)
                        equip_ilo = equip_ilo.get('equipamento')
                        id_ilo = equip_ilo['id']
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                 
                rack = client.create_rack().insert_rack(rack_number, mac_sw1, mac_sw2, mac_ilo, id_sw1, id_sw2, id_ilo)
                messages.add_message(request, messages.SUCCESS, rack_messages.get("success_insert"))
                return render_to_response(RACK_FORM, {'form': form}, context_instance=RequestContext(request))

        else:
            form = RackForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    return render_to_response(RACK_FORM, {'form': form}, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def ajax_view(request):

    # Get user
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()

    return ajax_rack_view(request, client_api)


def ajax_rack_view(request, client_api):

    try:

        racks = dict()

        # Get all racks from NetworkAPI
        racks = client_api.create_rack().find_racks()

        if not racks.has_key("rack"):
                    racks["rack"] = []

        rack = racks.get('rack')

        for var in rack:
            id_equip1 = var.get("id_sw1")
            id_equip2 = var.get("id_sw2")
            id_equip3 = var.get("id_ilo")
            mac_1 = var.get("mac_sw1")           
            mac_2 = var.get("mac_sw2")           
            mac_3 = var.get("mac_ilo")
           
            if not id_equip1==None:
                equip1 = client_api.create_equipamento().listar_por_id(id_equip1) 
                equip1 = equip1.get('equipamento')
                var['id_sw1'] = equip1.get('nome')
            else:
                var['id_sw1'] = ''
            if not id_equip2==None:
                equip2 = client_api.create_equipamento().listar_por_id(id_equip2)
                equip2 = equip2.get('equipamento')
                var['id_sw2'] = equip2.get('nome')    
            else:
                var['id_sw2'] = ''
            if not id_equip3==None:
                equip3 = client_api.create_equipamento().listar_por_id(id_equip3)
                equip3 = equip3.get('equipamento')
                var['id_ilo'] = equip3.get('nome')
            else:
                var['id_ilo'] = ''
            if mac_1==None:
                var['mac_sw1'] = ''
            if mac_2==None:
                var['mac_sw2'] = ''
            if mac_3==None:
                var['mac_ilo'] = ''

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(RACK_VIEW_AJAX, racks, context_instance=RequestContext(request))


