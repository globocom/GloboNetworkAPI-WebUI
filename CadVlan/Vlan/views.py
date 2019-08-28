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
import json
import logging
from __builtin__ import Exception

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError
from networkapiclient.exception import VipIpError
from networkapiclient.exception import VlanError
from networkapiclient.exception import VlanNaoExisteError
from networkapiclient.Pagination import Pagination

from CadVlan.Acl.acl import checkAclGit
from CadVlan.Acl.acl import deleteAclGit
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.forms import CreateForm
from CadVlan.forms import DeleteForm
from CadVlan.forms import RemoveForm
from CadVlan.messages import acl_messages
from CadVlan.messages import error_messages
from CadVlan.messages import network_ip_messages
from CadVlan.messages import vlan_messages
from CadVlan.permissions import ENVIRONMENT_MANAGEMENT
from CadVlan.permissions import NETWORK_TYPE_MANAGEMENT
from CadVlan.permissions import VLAN_CREATE_SCRIPT
from CadVlan.permissions import VLAN_MANAGEMENT
from CadVlan.templates import AJAX_CONFIRM_VLAN
from CadVlan.templates import AJAX_SUGGEST_NAME
from CadVlan.templates import AJAX_VLAN_AUTOCOMPLETE
from CadVlan.templates import AJAX_VLAN_LIST
from CadVlan.templates import SEARCH_FORM_ERRORS
from CadVlan.templates import VLAN_EDIT
from CadVlan.templates import VLAN_FORM
from CadVlan.templates import VLAN_SEARCH_LIST
from CadVlan.templates import VLANS_DEETAIL
from CadVlan.Util.converters.util import replace_id_to_name
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.Decorators import has_perm
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Util.Enum import NETWORK_TYPES
from CadVlan.Util.git import GITCommandError
from CadVlan.Util.git import GITError
from CadVlan.Util.shortcuts import render_json
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.Util.utility import acl_key
from CadVlan.Util.utility import convert_string_to_boolean
from CadVlan.Util.utility import DataTablePaginator
from CadVlan.Util.utility import upcase_first_letter
from CadVlan.Vlan.business import cache_list_vlans
from CadVlan.Vlan.business import montaIPRede
from CadVlan.Vlan.forms import SearchVlanForm
from CadVlan.Vlan.forms import VlanForm

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def ajax_list_vlans(request, id_vlan="0", sf_number='0', sf_name='0', sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):

    try:

        # If form was submited
        if request.method == "GET":

            # Get user auth
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            # Get all environments from NetworkAPI
            env_list = get_environments(client)
            # Get all network types from NetworkAPI
            net_list = client.create_tipo_rede().listar()

            search_form = SearchVlanForm(env_list, net_list, request.GET)

            if search_form.is_valid():
                number = search_form.cleaned_data["number"]
                name = search_form.cleaned_data["name"]
                iexact = search_form.cleaned_data["iexact"]
                environment = search_form.cleaned_data["environment"]
                net_type = search_form.cleaned_data["net_type"]
                ip_version = search_form.cleaned_data["ip_version"]
                networkv4 = search_form.cleaned_data["networkv4"]
                networkv6 = search_form.cleaned_data["networkv6"]
                subnet = search_form.cleaned_data["subnet"]
                acl = search_form.cleaned_data["acl"]

                if len(networkv4) > 0:
                    network = networkv4
                elif len(networkv6) > 0:
                    network = networkv6
                else:
                    network = None

                if id_vlan == '1':
                    if not sf_number == '0':
                        number = sf_number
                    if not sf_name == '0':
                        name = sf_name
                    if sf_iexact == '0':
                        sf_iexact = False
                    elif sf_iexact == '1':
                        sf_iexact = True
                    iexact = sf_iexact
                    if not sf_environment == '0':
                        environment = sf_environment
                    if not sf_nettype == '0':
                        net_type = sf_nettype
                    if not sf_ipversion == '0':
                        ip_version = sf_ipversion
                    if not sf_network == '0':
                        if (sf_network.count('_') == 4):  # ipv4
                            sf_network = sf_network.replace("_", ".", 3)
                        else:  # ipv6
                            sf_network = sf_network.replace("_", ":", 7)
                        sf_network = sf_network.replace("_", "/")
                        network = sf_network
                    if not sf_subnet == '0':
                        subnet = sf_subnet
                    if sf_acl == '0':
                        sf_acl = False
                    elif sf_acl == '1':
                        sf_acl = True
                    acl = search_form.cleaned_data["acl"]

                if environment == "0":
                    environment = None
                if net_type == "0":
                    net_type = None

                # Pagination
                columnIndexNameMap = {0: '', 1: '', 2: 'num_vlan', 3: 'nome', 4: 'ambiente',
                                      5: 'tipo_rede', 6: 'network', 7: '', 8: 'acl_file_name', 9: 'acl_file_name_v6'}
                dtp = DataTablePaginator(request, columnIndexNameMap)

                # Make params
                dtp.build_server_side_list()

                # Set params in simple Pagination class
                pag = Pagination(dtp.start_record, dtp.end_record,
                                 dtp.asorting_cols, dtp.searchable_columns, dtp.custom_search)
                '', False, None, None, None, 2, 0, False
                # Call API passing all params
                vlans = client.create_vlan().find_vlans(
                    number, name, iexact, environment, net_type, network, ip_version, subnet, acl, pag)

                if "vlan" not in vlans:
                    vlans["vlan"] = []

                request_var = dict()

                if number is None:
                    number = '0'
                request_var["number"] = number
                if name == '':
                    name = '0'
                request_var["name"] = name
                if environment is None:
                    environment = '0'
                request_var["environment"] = environment
                if net_type is None:
                    net_type = '0'
                request_var["nettype"] = net_type
                if subnet is None:
                    subnet = '0'
                request_var["subnet"] = subnet
                if ip_version is None:
                    ip_version = '0'
                request_var["ipversion"] = ip_version
                if network is None:
                    network = '0'
                else:
                    network = network.replace(".", "_")
                    network = network.replace(":", "_")
                    network = network.replace("/", "_")
                request_var["network"] = network
                if iexact is False:
                    iexact = '0'
                elif iexact is True:
                    iexact = '1'
                request_var["iexact"] = iexact
                if acl is False:
                    acl = '0'
                elif acl is True:
                    acl = '1'
                request_var["acl"] = acl

                # Returns JSON
                return dtp.build_response(vlans["vlan"], vlans["total"], AJAX_VLAN_LIST, request, request_var)

            else:
                # Remake search form
                lists = dict()
                lists["search_form"] = search_form

                # Returns HTML
                response = HttpResponse(loader.render_to_string(
                    SEARCH_FORM_ERRORS, lists, context_instance=RequestContext(request)))
                # Send response status with error
                response.status_code = 412
                return response

    except NetworkAPIClientError, e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')
    except BaseException, e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}])
def ajax_autocomplete_vlans(request):
    try:

        vlan_list = dict()

        # Get user auth
        auth = AuthSession(request.session)
        vlan = auth.get_clientFactory().create_vlan()

        # Get list of vlans from cache
        vlan_list = cache_list_vlans(vlan)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(AJAX_VLAN_AUTOCOMPLETE, vlan_list, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def search_list(request, id_vlan='0', sf_number='0', sf_name='0', sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):

    try:

        lists = dict()
        lists["delete_form"] = DeleteForm()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all environments from NetworkAPI
        env_list = get_environments(client)
        # Get all network types from NetworkAPI
        net_list = client.create_tipo_rede().listar()

        lists["search_form"] = SearchVlanForm(env_list, net_list)

        lists['search_var'] = id_vlan
        lists['sf_number'] = sf_number
        lists['sf_name'] = sf_name
        lists['sf_environment'] = sf_environment
        lists['sf_nettype'] = sf_nettype
        lists['sf_subnet'] = sf_subnet
        lists['sf_ipversion'] = sf_ipversion
        lists['sf_network'] = sf_network
        lists['sf_iexact'] = sf_iexact
        lists['sf_acl'] = sf_acl

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VLAN_SEARCH_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def list_by_id(request, id_vlan='0', sf_number='0', sf_name='0', sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):

    lists = dict()
    listaIps = []
    lista = []
    lists["delete_form"] = DeleteForm()
    lists["create_form"] = CreateForm()
    lists["remove_form"] = RemoveForm()
    lists['sf_number'] = sf_number
    lists['sf_name'] = sf_name
    lists['sf_environment'] = sf_environment
    lists['sf_nettype'] = sf_nettype
    lists['sf_subnet'] = sf_subnet
    lists['sf_ipversion'] = sf_ipversion
    lists['sf_network'] = sf_network
    lists['sf_iexact'] = sf_iexact
    lists['sf_acl'] = sf_acl

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # recuperando lista de vlans

        vlans = client.create_vlan().get(id_vlan)

        # Get all environments from NetworkAPI
        env_list = get_environments(client)
        environment = env_list.get('environments')

        vlans = vlans.get('vlan')
        for ambiente in environment:
            logger.info(ambiente)
            logger.info(vlans)
            if int(vlans.get('ambiente')) == int(ambiente.get('id')):
                vlans['ambiente'] = ambiente.get("name")
                vlans['ambiente_id'] = ambiente.get("id")
                break

        # FE - PORTAL - CORE/DENSIDADE
        lists['vlan'] = vlans

        vlans = None

        vlans = client.create_vlan().get(id_vlan)

        vlans = vlans.get('vlan')

        redesIPV4 = vlans["redeipv4"]
        if len(redesIPV4) > 0:
            listaIps.append(montaIPRede(redesIPV4))

        redesIPV6 = vlans.get("redeipv6")
        if len(redesIPV6) > 0:
            listaIps.append(montaIPRede(redesIPV6, False))

        # Show 'Criar Redes' button
        lists['exists_active_network'] = 0
        lists['exists_not_active_network'] = 0

        for item in listaIps:
            for i in item:
                # Show/Hide create and/or remove network button
                if i['active'] == 'False':
                    lists['exists_not_active_network'] = 1
                else:
                    lists['exists_active_network'] = 1

                lista.append(i)

        net_type = client.create_tipo_rede().listar()

        lista = replace_id_to_name(
            lista, net_type['net_type'], "network_type", "id", "name")

        lists['net_vlans'] = lista

        return render_to_response(VLANS_DEETAIL, lists, context_instance=RequestContext(request))

    except VlanNaoExisteError, e:
        logger.error(e)
        return redirect('vlan.search.list')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except TypeError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VLANS_DEETAIL, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def vlan_form(request):
    lists = dict()
    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all environments from NetworkAPI
        environment = get_environments(client)


        if request.method == 'POST':

            form = VlanForm(environment, request.POST)

            lists['form'] = form

            if form.is_valid():

                name = form.cleaned_data['name']
                acl_file = form.cleaned_data['acl_file']
                acl_file_v6 = form.cleaned_data['acl_file_v6']
                description = form.cleaned_data['description']
                number = form.cleaned_data['number']
                environment_id = form.cleaned_data['environment']
                network_ipv4 = form.cleaned_data['network_ipv4']
                network_ipv6 = form.cleaned_data['network_ipv6']

                # Criar a Vlan
                if number:
                    vlan = client.create_vlan().insert_vlan(environment_id, name, number, description, acl_file,
                                                            acl_file_v6, network_ipv4, network_ipv6)
                    id_vlan = vlan.get('vlan').get('id')
                else:
                    vlan = client.create_vlan().allocate_without_network(environment_id, name, description, None)
                    id_vlan = vlan.get('vlan').get('id')
                    if int(network_ipv4):
                        client.create_network().add_network_ipv4(id_vlan, None, None, None)
                    if int(network_ipv6):
                        client.create_network().add_network_ipv6(id_vlan, None, None, None)

                messages.add_message(request, messages.SUCCESS, vlan_messages.get("vlan_sucess"))

                # redireciona para a listagem de vlans
                return HttpResponseRedirect(reverse('vlan.list.by.id', args=[id_vlan]))
        # Get
        if request.method == 'GET':
            lists['form'] = VlanForm(environment)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VLAN_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def vlan_edit(request, id_vlan='0', sf_number='0', sf_name='0', sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):
    lists = dict()
    lists['id_vlan'] = id_vlan
    lists['acl_created_v4'] = "False"
    lists['acl_created_v6'] = "False"
    lists['form_error'] = "False"
    lists['sf_number'] = sf_number
    lists['sf_name'] = sf_name
    lists['sf_environment'] = sf_environment
    lists['sf_nettype'] = sf_nettype
    lists['sf_subnet'] = sf_subnet
    lists['sf_ipversion'] = sf_ipversion
    lists['sf_network'] = sf_network
    lists['sf_iexact'] = sf_iexact
    lists['sf_acl'] = sf_acl

    vlan = None

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        try:
            vlan = client.create_vlan().get(id_vlan)
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list')

        if request.method == 'GET':

            # Get all environments from NetworkAPI
            environment = get_environments(client)

            vlan = vlan.get("vlan")

            lists['form'] = VlanForm(environment, initial={'name': vlan.get('nome'), "number": vlan.get('num_vlan'), "environment": vlan.get(
                "ambiente"), "description": vlan.get('descricao'), "acl_file": vlan.get('acl_file_name'), "acl_file_v6": vlan.get('acl_file_name_v6')})

        if request.method == 'POST':

            # Get all environments from NetworkAPI
            environment = get_environments(client)
            form = VlanForm(environment, request.POST)
            lists['form'] = form
            vlan = vlan.get('vlan')

            if form.is_valid():

                nome = form.cleaned_data['name']
                numero = form.cleaned_data['number']
                acl_file = form.cleaned_data['acl_file']
                acl_file_v6 = form.cleaned_data['acl_file_v6']
                descricao = form.cleaned_data['description']
                ambiente = form.cleaned_data['environment']
                apply_vlan = form.cleaned_data['apply_vlan']

                # client.editar
                client.create_vlan().edit_vlan(
                    ambiente, nome, numero, descricao, acl_file, acl_file_v6, id_vlan)
                messages.add_message(
                    request, messages.SUCCESS, vlan_messages.get("vlan_edit_sucess"))

                # If click apply
                if apply_vlan is True:
                    return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan, sf_number, sf_name, sf_environment, sf_nettype, sf_subnet, sf_ipversion, sf_network, sf_iexact, sf_acl]))

                return HttpResponseRedirect(reverse('vlan.list.by.id', args=[id_vlan, sf_number, sf_name, sf_environment, sf_nettype, sf_subnet, sf_ipversion, sf_network, sf_iexact, sf_acl]))

            else:
                lists['form_error'] = "True"

        lists['acl_valida_v4'] = vlan.get("acl_valida")
        lists['acl_valida_v6'] = vlan.get("acl_valida_v6")

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    try:

        environment = client.create_ambiente().buscar_por_id(
            vlan.get("ambiente")).get("ambiente")

        if vlan.get('acl_file_name') is not None:

            is_acl_created = checkAclGit(vlan.get(
                'acl_file_name'), environment, NETWORK_TYPES.v4, AuthSession(request.session).get_user())

            lists[
                'acl_created_v4'] = "False" if is_acl_created is False else "True"

        if vlan.get('acl_file_name_v6') is not None:

            is_acl_created = checkAclGit(vlan.get(
                'acl_file_name_v6'), environment, NETWORK_TYPES.v6, AuthSession(request.session).get_user())

            lists[
                'acl_created_v6'] = "False" if is_acl_created is False else "True"

    except GITCommandError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VLAN_EDIT, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def ajax_acl_name_suggest(request):
    lists = dict()
    try:

        nome = request.GET['nome']
        id_ambiente = request.GET['id_ambiente']

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        environment = client.create_ambiente().buscar_por_id(
            id_ambiente).get('ambiente')

        suggest_name = str(
            nome + environment['nome_ambiente_logico']).replace(" ", "")
        lists['suggest_name'] = suggest_name

        # Returns HTML
        response = HttpResponse(loader.render_to_string(
            AJAX_SUGGEST_NAME, lists, context_instance=RequestContext(request)))
        # Send response status with error
        response.status_code = 200
        return response

    except:

        lists['suggest_name'] = ''
        # Returns HTML
        response = HttpResponse(loader.render_to_string(
            AJAX_SUGGEST_NAME, lists, context_instance=RequestContext(request)))
        # Send response status with error
        response.status_code = 200
        return response


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def ajax_confirm_vlan(request):
    lists = dict()
    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        message_confirm = ''
        message_confirm_numbers = ''
        is_number = int(request.GET['is_number'])

        network = None
        ip_version = 2
        number = None
        subnet = 0

        # Check in vlan insert/update
        if is_number == 1:
            number = request.GET['number']
            id_environment = request.GET['id_environment']
            id_vlan = request.GET['id_vlan']
        # Check in net insert
        else:
            netipv4 = request.GET['netipv4']
            netipv6 = request.GET['netipv6']
            id_vlan = request.GET['id_vlan']

            if netipv4 == '':
                ip_version = 1
                network = netipv6
            else:
                ip_version = 0
                network = netipv4
            subnet = 1

        """Filter vlans by number or network subnet"""
        # Pagination
        columnIndexNameMap = {0: '', 1: '', 2: 'num_vlan', 3: 'nome', 4: 'ambiente',
                              5: 'tipo_rede', 6: 'network', 7: '', 8: 'acl_file_name', 9: 'acl_file_name_v6'}
        dtp = DataTablePaginator(request, columnIndexNameMap)

        # Make params
        dtp.build_server_side_list()

        # Set params in simple Pagination class
        pag = Pagination(
            0, 100, dtp.asorting_cols, dtp.searchable_columns, dtp.custom_search)

        # Call API passing all params
        vlans = client.create_vlan().find_vlans(
            number, '', False, None, None, network, ip_version, subnet, False, pag)
        """Filter end"""

        if 'vlan' in vlans:
            for vlan in vlans.get('vlan'):
                # Ignore the same Vlan for validation
                if vlan['id'] != id_vlan:
                    # is_number means that validation is with number vlan
                    # (number used in another environment)
                    if is_number == 1:
                        if int(vlan['ambiente']) != int(id_environment):
                            needs_confirmation = client.create_vlan().confirm_vlan(
                                number, id_environment).get('needs_confirmation')
                            if needs_confirmation == 'True':
                                message_confirm = "a vlan de número " + \
                                    str(number) + " já existe no ambiente " + \
                                    str(vlan['ambiente_name'])
                        else:
                            message_confirm = ''
                            break
                    # else the validation is with network
                    else:
                        network_confirm = network.replace('/', 'net_replace')
                        needs_confirmation = client.create_vlan().confirm_vlan(
                            network_confirm, id_vlan, ip_version).get('needs_confirmation')
                        if needs_confirmation == 'True':
                            message_confirm = "A rede compatível " + str(network) + " já existe no ambiente " + str(
                                vlan['ambiente_name']) + ". Deseja alocar essa rede mesmo assim?"
                        else:
                            message_confirm = ''
                            break

        # also validate if the number is in valid range
        if is_number:
            has_numbers_availables = client.create_vlan().check_number_available(
                id_environment, number, id_vlan).get('has_numbers_availables')
            has_numbers_availables = convert_string_to_boolean(
                has_numbers_availables)
            if not has_numbers_availables:
                message_confirm_numbers = 'O número está fora do range definido'

        # The number is in another environment and the number isn't in right
        # range, so concatenate the messages
        if message_confirm and message_confirm_numbers:
            message_confirm = message_confirm_numbers + \
                ' e a ' + message_confirm
        # Only the number isn't in right range
        elif not message_confirm and message_confirm_numbers:
            message_confirm = message_confirm_numbers

        # Concatenate the question in message
        if is_number and message_confirm:
            message_confirm += '. Deseja criar essa vlan mesmo assim?'

        # Upcase only first letter in message and add to dict
        lists['confirm_message'] = upcase_first_letter(message_confirm)

        # Returns HTML
        response = HttpResponse(loader.render_to_string(
            AJAX_CONFIRM_VLAN, lists, context_instance=RequestContext(request)))
        # Send response status with error
        response.status_code = 200
        return response

    except:

        lists['confirm_message'] = ''
        # Returns HTML
        response = HttpResponse(loader.render_to_string(
            AJAX_CONFIRM_VLAN, lists, context_instance=RequestContext(request)))
        # Send response status with error
        response.status_code = 200
        return response


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def delete_all(request, sf_number='0', sf_name='0', sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_vlan = auth.get_clientFactory().create_vlan()
            client = auth.get_clientFactory()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each vlan selected to remove
            for id_vlan in ids:
                try:

                    vlan = client_vlan.get(id_vlan).get("vlan")
                    environment = client.create_ambiente().buscar_por_id(
                        vlan.get("ambiente")).get("ambiente")

                    # Execute in NetworkAPI
                    client_vlan.deallocate(id_vlan)

                    # commenting code to remove acl files - issue #40
                    # key_acl_v4 = acl_key(NETWORK_TYPES.v4)
                    # key_acl_v6 = acl_key(NETWORK_TYPES.v6)
                    # user = AuthSession(request.session).get_user()

                    # try:
                    #     if vlan.get(key_acl_v4) is not None:
                    #         if checkAclGit(vlan.get(key_acl_v4), environment, NETWORK_TYPES.v4, user):
                    #             deleteAclGit(
                    #                 vlan.get(key_acl_v4), environment, NETWORK_TYPES.v4, user)

                    #     if vlan.get(key_acl_v6) is not None:
                    #         if checkAclGit(vlan.get(key_acl_v6), environment, NETWORK_TYPES.v6, user):
                    #             deleteAclGit(
                    #                 vlan.get(key_acl_v6), environment, NETWORK_TYPES.v6, user)

                    # except GITError, e:
                    #     messages.add_message(
                    #         request, messages.WARNING, vlan_messages.get("vlan_git_error"))

                except VipIpError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    error_list.append(id_vlan)
                    have_errors = True

                except VlanError, e:
                    error_list.append(id_vlan)
                    have_errors = True

                except NetworkAPIClientError, e:
                    logger.error(e)
                    error_list.append(id_vlan)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True

            # If all has ben removed
            if have_errors is False:
                messages.add_message(
                    request, messages.SUCCESS, vlan_messages.get("success_remove"))

            else:
                if len(ids) == len(error_list):
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("can_not_remove_error"))
                else:
                    msg = ""
                    for id_error in error_list:
                        msg = msg + id_error + ", "
                    msg = error_messages.get("can_not_remove") % msg[:-2]
                    messages.add_message(request, messages.WARNING, msg)

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('vlan.search.list')
    # return HttpResponseRedirect(reverse('vlan.search.list', args=["1", sf_number, sf_name, sf_environment, sf_nettype, sf_subnet, sf_ipversion, sf_network, sf_iexact, sf_acl]))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def delete_all_network(request, id_vlan='0', sf_number='0', sf_name='0', sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_network = auth.get_clientFactory().create_network()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # Control others exceptions
            have_errors = False
            error_list = list()

            # For each networks selected to remove
            for value in ids:
                try:

                    var = split_to_array(value, sep='-')

                    id_network = var[0]
                    network = var[1]

                    # Execute in NetworkAPI
                    if network == NETWORK_TYPES.v4:
                        client_network.deallocate_network_ipv4(id_network)

                    else:
                        client_network.deallocate_network_ipv6(id_network)

                except VipIpError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    error_list.append(id_network)

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    error_list.append(id_network)

            # If all has ben removed
            if have_errors is False:
                messages.add_message(
                    request, messages.SUCCESS, vlan_messages.get("success_remove_network"))

            else:
                if len(ids) == len(error_list):
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("can_not_remove_error"))
                else:
                    msg = ""
                    for id_error in error_list:
                        msg = msg + id_error + ", "
                    msg = error_messages.get("can_not_remove") % msg[:-2]
                    messages.add_message(request, messages.WARNING, msg)

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return HttpResponseRedirect(reverse('vlan.list.by.id', args=[id_vlan, sf_number, sf_name, sf_environment, sf_nettype, sf_subnet, sf_ipversion, sf_network, sf_iexact, sf_acl]))


@log
@login_required
@has_perm([{"permission": VLAN_CREATE_SCRIPT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def create(request, id_vlan="0", sf_number='0', sf_name='0', sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):
    """ Set column 'ativada = 1' """

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # If vlan with parameter id_vlan  don't exist, VlanNaoExisteError
        # exception will be called
        vlan = client.create_vlan().get(id_vlan)

        client.create_vlan().create_vlan(id_vlan)

        messages.add_message(
            request, messages.SUCCESS, vlan_messages.get("vlan_create_success"))

    except VlanNaoExisteError, e:
        logger.error(e)
        return redirect('vlan.search.list')

    # Redirect to list_all action
    return HttpResponseRedirect(reverse('vlan.list.by.id', args=[id_vlan, sf_number, sf_name, sf_environment, sf_nettype, sf_subnet, sf_ipversion, sf_network, sf_iexact, sf_acl]))


@log
@login_required
@has_perm([{"permission": VLAN_CREATE_SCRIPT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def create_network(request, id_vlan="0", sf_number='0', sf_name='0', sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):
    """ Set column 'active = 1' in tables  """
    try:
        if request.method == 'POST':

            form = CreateForm(request.POST)

            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            networks_activated = False
            networks_was_activated = True

            equipments_ipv4 = list()
            equipments_ipv6 = list()

            if form.is_valid():

                # If vlan with parameter id_vlan  don't exist,
                # VlanNaoExisteError exception will be called
                vlan = client.create_vlan().get(id_vlan)

                environment = client.create_ambiente().buscar_por_id(
                    vlan['vlan']["ambiente"]).get("ambiente")

                # All ids to be activated
                ids = split_to_array(form.cleaned_data['ids_create'])

                for id in ids:
                    value = id.split('-')
                    id_net = value[0]
                    network_type = value[1]

                    if network_type == 'v4':
                        net = client.create_network().get_network_ipv4(id_net)
                    else:
                        net = client.create_network().get_network_ipv6(id_net)

                    if net['network']['active'] == 'True':
                        networks_activated = True
                    else:
                        networks_was_activated = False

                    if network_type == 'v4':
                        equipments_ipv4.extend(
                            list_equipment_by_network_ip4(client, id_net))

                        client.create_api_network_ipv4().deploy(id_net)
                    else:
                        equipments_ipv6.extend(
                            list_equipment_by_network_ip6(client, id_net))

                        client.create_api_network_ipv6().deploy(id_net)

                apply_acl_for_network_v4(
                    request, client, equipments_ipv4, vlan, environment)

                apply_acl_for_network_v6(
                    request, client, equipments_ipv6, vlan, environment)

                if networks_activated is True:
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("networks_activated"))

                if networks_was_activated is False:
                    messages.add_message(
                        request, messages.SUCCESS, network_ip_messages.get("net_create_success"))

            else:
                vlan = client.create_vlan().get(id_vlan)
                if vlan['vlan']['ativada'] == 'True':
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("vlan_select_one"))
                else:
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("select_one"))

    except VlanNaoExisteError, e:
        logger.error(e)
        return redirect('vlan.search.list')
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('vlan.list.by.id', args=[id_vlan, sf_number, sf_name, sf_environment, sf_nettype, sf_subnet, sf_ipversion, sf_network, sf_iexact, sf_acl]))


@log
@login_required
@has_perm([{"permission": VLAN_CREATE_SCRIPT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def remove_network(request, id_vlan="0", sf_number='0', sf_name='0', sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):
    """ Set column 'active = 0' in tables  """
    try:
        if request.method == 'POST':

            form = RemoveForm(request.POST)

            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            networks_activated = False
            networks_was_activated = True

            equipments_ipv4 = list()
            equipments_ipv6 = list()

            if form.is_valid():

                # If vlan with parameter id_vlan  don't exist,
                # VlanNaoExisteError exception will be called
                vlan = client.create_vlan().get(id_vlan)

                environment = client.create_ambiente().buscar_por_id(
                    vlan['vlan']["ambiente"]).get("ambiente")

                # All ids to be activated
                ids = split_to_array(form.cleaned_data['ids_remove'])

                for id in ids:
                    value = id.split('-')
                    id_net = value[0]
                    network_type = value[1]

                    if network_type == 'v4':
                        net = client.create_network().get_network_ipv4(id_net)
                    else:
                        net = client.create_network().get_network_ipv6(id_net)

                    if net['network']['active'] == 'True':
                        networks_activated = True
                    else:
                        networks_was_activated = False

                    if network_type == 'v4':
                        equipments_ipv4.extend(
                            list_equipment_by_network_ip4(client, id_net))

                        client.create_api_network_ipv4().undeploy(id_net)
                    else:
                        equipments_ipv6.extend(
                            list_equipment_by_network_ip6(client, id_net))

                        client.create_api_network_ipv6().undeploy(id_net)

                if networks_activated is False:
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("networks_deactivated"))

                if networks_was_activated is True:
                    messages.add_message(
                        request, messages.SUCCESS, network_ip_messages.get("net_remove_success"))

            else:
                vlan = client.create_vlan().get(id_vlan)
                if vlan['vlan']['ativada'] == 'False':
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("vlan_select_one"))
                else:
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("select_one"))

    except VlanNaoExisteError, e:
        logger.error(e)
        return redirect('vlan.search.list')
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('vlan.list.by.id', args=[id_vlan, sf_number, sf_name, sf_environment, sf_nettype, sf_subnet, sf_ipversion, sf_network, sf_iexact, sf_acl]))


def list_equipment_by_network_ip4(client, id_net):

    equipments = []

    ips = client.create_ip().find_ip4_by_network(id_net).get('ips')

    for ip in ips:
        if isinstance(ip.get('equipamento'), list):
            for equip in ip.get('equipamento'):
                new_ip = dict()
                new_ip['equipamento'] = dict()
                new_ip['equipamento']['oct1'] = ip['oct1']
                new_ip['equipamento']['oct2'] = ip['oct2']
                new_ip['equipamento']['oct3'] = ip['oct3']
                new_ip['equipamento']['oct4'] = ip['oct4']
                new_ip['equipamento']['descricao'] = ip['descricao']
                new_ip['equipamento']['nome'] = equip.get('nome')
                new_ip['equipamento']['id'] = equip.get('id')
                equipments.append(new_ip)

        else:
            equipments.append(ip)

    return equipments


def list_equipment_by_network_ip6(client, id_net):

    equipments = []

    ips = client.create_ip().find_ip6_by_network(id_net).get('ips')

    for ip in ips:
        if isinstance(ip.get('equipamento'), list):
            for equip in ip.get('equipamento'):
                new_ip = dict()
                new_ip['equipamento'] = dict()
                new_ip['equipamento']['block1'] = ip['block1']
                new_ip['equipamento']['block2'] = ip['block2']
                new_ip['equipamento']['block3'] = ip['block3']
                new_ip['equipamento']['block4'] = ip['block4']
                new_ip['equipamento']['block5'] = ip['block5']
                new_ip['equipamento']['block6'] = ip['block6']
                new_ip['equipamento']['block7'] = ip['block7']
                new_ip['equipamento']['block8'] = ip['block8']
                new_ip['equipamento']['descricao'] = ip['descricao']
                new_ip['equipamento']['equip_name'] = equip.get('nome')
                new_ip['equipamento']['id'] = equip.get('id')
                equipments.append(new_ip)

        else:
            equipments.append(ip)

    return equipments


def apply_acl_for_network_v4(request, client, equipments_v4, vlan, environment):

    try:

        if equipments_v4:
            if vlan['vlan']['acl_valida'] == 'True':
                apply_acl_for_network(
                    request, client, equipments_v4, vlan, environment, 'v4')
                messages.add_message(
                    request, messages.SUCCESS, acl_messages.get("seccess_apply_valid_acl") % 'ipv4')
            else:
                messages.add_message(
                    request, messages.WARNING, acl_messages.get("error_apply_ivalid_acl") % 'ipv4')

    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, acl_messages.get(
            "error_apply_acl_for_network") % 'ipv4')


def apply_acl_for_network_v6(request, client, equipments_v6, vlan, environment):

    try:

        if equipments_v6:
            if vlan['vlan']['acl_valida_v6'] == 'True':
                apply_acl_for_network(
                    request, client, equipments_v6, vlan, environment, 'v6')
                messages.add_message(
                    request, messages.SUCCESS, acl_messages.get("seccess_apply_valid_acl") % 'ipv6')
            else:
                messages.add_message(
                    request, messages.WARNING, acl_messages.get("error_apply_ivalid_acl") % 'ipv6')

    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, acl_messages.get(
            "error_apply_acl_for_network") % 'ipv6')


def apply_acl_for_network(request, client, equipments, vlan, environment, network_type):

    try:

        apply_result = client.create_vlan().apply_acl(
            equipments, vlan.get("vlan"), environment, network_type)

        is_apply = apply_result.get('is_apply')

        if is_apply != '0':
            raise Exception(
                'Não foi possível aplicar ACL aos equipamentos da rede')

    except Exception, e:
        raise e

def get_environments(client):
    try:
        # Get all environments from NetworkAPI
        search_env = {
            'extends_search': [],
            'start_record': 0,
            'custom_search': '',
            'end_record': 99999999,
            'asorting_cols': [],
            'searchable_columns': []}
        env_cli = client.create_api_environment()
        # env_list = env_cli.search()
        return client.create_api_environment().search(search=search_env, kind='basic')

    except Exception, e:
        raise e



@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def ajax_get_available_ip_config_by_environment_id(request):

    if request.method == 'GET':
        environment_id = request.GET.get('environment_id')

        context = {}
        available_environment_config_ipv4 = False
        available_environment_config_ipv6 = False
        vlan_range = False
        hide_vlan_range = True

        if int(environment_id):

            try:
                auth = AuthSession(request.session)
                client = auth.get_clientFactory()
                hide_vlan_range = False
                env_list = client.create_ambiente().configuration_list_all(environment_id)

                lists_configuration = env_list.get('lists_configuration')

                for config in lists_configuration:
                    if config.get('type', '').upper() == 'V4':
                        available_environment_config_ipv4 = True
                    if config.get('type', '').upper() == 'V6':
                        available_environment_config_ipv6 = True

                # if range:
                ambiente = client.create_ambiente().buscar_por_id(environment_id)
                ambiente = ambiente.get("ambiente")
                if ambiente.get('min_num_vlan_1'):
                    vlan_range = True

            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
            except BaseException, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)

    context['available_environment_config_ipv4'] = available_environment_config_ipv4
    context['available_environment_config_ipv6'] = available_environment_config_ipv6
    context['vlan_range'] = vlan_range
    context['hide_vlan_range'] = hide_vlan_range

    return render_json(json.dumps(context))
