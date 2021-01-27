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
import json
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, VipIpError, \
    IpEquipCantDissociateFromVip
from django.contrib import messages
from CadVlan.permissions import VLAN_MANAGEMENT, EQUIPMENT_MANAGEMENT, \
    NETWORK_TYPE_MANAGEMENT, ENVIRONMENT_VIP, IPS
from CadVlan.templates import NETIPV4, NETIPV6, IP4, IP6, IP4EDIT, IP6EDIT, \
    IP4ASSOC, IP6ASSOC, NET_FORM, NET6_EDIT, \
    NET4_EDIT, NET_EVIP_OPTIONS, AJAX_IPLIST_EQUIPMENT_DHCP_SERVER_HTML
from CadVlan.Util.converters.util import replace_id_to_name, split_to_array
from CadVlan.Net.forms import IPForm, IPEditForm, IPAssocForm, NetworkForm, \
    NetworkEditForm
from CadVlan.Net.business import is_valid_ipv4, is_valid_ipv6
from CadVlan.messages import network_ip_messages
from CadVlan.forms import DeleteForm
from CadVlan.messages import error_messages
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse
from CadVlan.OptionVip.forms import OptionVipNetForm
from django.http import HttpResponse
from django.template import loader
from CadVlan.Util.utility import get_param_in_request


logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True},
           {"permission": ENVIRONMENT_VIP, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def add_network_form(request):

    # lists = dict()
    # try:
    #
    #     # Get User
    #     auth = AuthSession(request.session)
    #     client = auth.get_clientFactory()
    #
    #     # Get all needs from NetworkAPI
    #     net_type_list = client.create_tipo_rede().listar()
    #     env_vip_list = {"environment_vip": []}
    #
    #     # Forms
    #     lists['form'] = NetworkForm(net_type_list, env_vip_list)
    #
    #     # If form was submited
    #     if request.method == 'POST':
    #         vlan_id = request.POST['vlan_name_id']
    #         available_evips = client.create_environment_vip().list_all_available(
    #             vlan_id) if vlan_id else {'environment_vip': []}
    #
    #         # Set data in form
    #         form = NetworkForm(net_type_list, available_evips, request.POST)
    #
    #         # Validate
    #         if form.is_valid():
    #
    #             vlan_id = form.cleaned_data['vlan_name_id']
    #             net_type = form.cleaned_data['net_type']
    #             env_vip = form.cleaned_data['env_vip']
    #             net_version = form.cleaned_data['ip_version']
    #             networkv4 = form.cleaned_data['networkv4']
    #             networkv6 = form.cleaned_data['networkv6']
    #             if env_vip:
    #                 cluster_unit = form.cleaned_data['cluster_unit']
    #                 cluster_unit = cluster_unit if cluster_unit else 'cluster-unit-1'
    #             else:
    #                 cluster_unit = None
    #             id_equips = request.POST.getlist('id_equip')
    #             nome_equips = request.POST.getlist('equip')
    #             id_ips = request.POST.getlist('id_ip')
    #             ips = request.POST.getlist('ip')
    #
    #             # Business
    #             client.create_vlan().get(vlan_id)
    #
    #             if net_version == "0":
    #                 network = networkv4
    #                 network_obj = client.create_network().add_network(
    #                     network, vlan_id, net_type, env_vip, cluster_unit)
    #                 net = network_obj.get('network')
    #                 for id_ip in id_ips:
    #                     client.create_dhcprelay_ipv4().add(net.get("id"), id_ip)
    #             else:
    #                 network = networkv6
    #                 network_obj = client.create_network().add_network(
    #                     network, vlan_id, net_type, env_vip, cluster_unit)
    #                 net = network_obj.get('network')
    #                 for id_ip in id_ips:
    #                     client.create_dhcprelay_ipv4().add(net.get("id"), id_ip)
    #
    #             messages.add_message(
    #                 request, messages.SUCCESS, network_ip_messages.get("success_insert"))
    #
    #             return HttpResponseRedirect(reverse('vlan.list.ajax'))
    #         # If invalid, send all error messages in fields
    #         lists['form'] = form
    #
    # except NetworkAPIClientError as e:
    #     logger.error(e)
    #     messages.add_message(request, messages.ERROR, e)
    #     # If some api error occurred, try to send data to html
    #     try:
    #         lists['form'] = form
    #     except NameError:
    #         pass
    #
    # return render_to_response(NET_FORM, lists, context_instance=RequestContext(request))

    messages.add_message(request,
                         messages.WARNING,
                         "The new network must to be created within a vlan.")
    return redirect('vlan.search.list')

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True},
           {"permission": ENVIRONMENT_VIP, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def vlan_add_network_form(request, id_vlan='0', sf_number='0', sf_name='0',
                          sf_environment='0', sf_nettype='0', sf_subnet='0',
                          sf_ipversion='0', sf_network='0', sf_iexact='0',
                          sf_acl='0'):

    lists = dict()
    lists['id_vlan'] = id_vlan
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
        # Get User
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all needs from NetworkAPI
        net_type_list = client.create_tipo_rede().listar()

        # If form was submited
        if request.method == 'POST':
            # Forms
            env_vip_list = {"environment_vip": []}
            lists['form'] = NetworkForm(net_type_list, env_vip_list)

            vlan_id = request.POST['vlan_name_id']
            available_evips = client.create_environment_vip().list_all_available(
                vlan_id) if vlan_id else {'environment_vip': []}

            # Set data in form
            form = NetworkForm(net_type_list, available_evips, request.POST)

            # Validate
            if form.is_valid():

                vlan_id = form.cleaned_data['vlan_name_id']
                net_type = form.cleaned_data['net_type']
                env_vip = form.cleaned_data['env_vip']
                net_version = form.cleaned_data['ip_version']
                networkv4 = form.cleaned_data['networkv4']
                networkv6 = form.cleaned_data['networkv6']
                if env_vip:
                    cluster_unit = form.cleaned_data['cluster_unit']
                    cluster_unit = cluster_unit if cluster_unit else 'cluster-unit-1'
                else:
                    cluster_unit = None
                id_equips = request.POST.getlist('id_equip')
                nome_equips = request.POST.getlist('equip')
                id_ips = request.POST.getlist('id_ip')
                ips = request.POST.getlist('ip')

                if net_version == "0":
                    network = networkv4
                    network_obj = client.create_network().add_network(
                        network, vlan_id, net_type, env_vip, cluster_unit)
                    net = network_obj.get('network')
                    for id_ip in id_ips:
                        client.create_dhcprelay_ipv4().add(net.get("id"), id_ip)
                else:
                    network = networkv6
                    network_obj = client.create_network().add_network(
                        network, vlan_id, net_type, env_vip, cluster_unit)
                    net = network_obj.get('network')
                    for id_ip in id_ips:
                        client.create_dhcprelay_ipv4().add(net.get("id"), id_ip)

                messages.add_message(
                    request, messages.SUCCESS, network_ip_messages.get("success_insert"))

                return HttpResponseRedirect(reverse('vlan.list.by.id',
                                                    args=[vlan_id, sf_number,
                                                          sf_name, sf_environment,
                                                          sf_nettype, sf_subnet,
                                                          sf_ipversion, sf_network,
                                                          sf_iexact, sf_acl]))
            # If invalid, send all error messages in fields
            lists['form'] = form

        if request.method == 'GET':
            env_vip_list = client.create_environment_vip().list_all_available(
                id_vlan)
            # Business
            vlan = client.create_vlan().get(id_vlan)
            vlan = vlan.get("vlan")

            environment = client.create_ambiente().buscar_por_id(
                vlan.get("ambiente")).get("ambiente")
            vlan_nome = "%s | %s - %s - %s" % (vlan.get("num_vlan"),
                                               environment.get("nome_divisao"),
                                               environment.get("nome_ambiente_logico"),
                                               environment.get("nome_grupo_l3"))

            # Forms
            lists['form'] = NetworkForm(net_type_list, env_vip_list, initial={
                                        'vlan_name': vlan_nome, 'vlan_name_id': vlan.get("id")})
            lists['dhcp_relays'] = list()

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        # If some api error occurred, try to send data to html
        try:
            lists['form'] = form
        except NameError:
            pass

    return render_to_response(NET_FORM, lists, context_instance=RequestContext(request))


def ajax_modal_ip_dhcp_server(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return __modal_ip_list_dhcp(request, client_api)


def __modal_ip_list_dhcp(request, client_api):

    lists = {
        'msg': str(),
        'ips': []
    }

    ips = {}
    status_code = 200

    equip_name = get_param_in_request(request, 'equip_name')

    try:
        # Valid Equipament
        equip = client_api.create_equipamento().listar_por_nome(equip_name).\
            get("equipamento")
        ips_list = client_api.create_ip().find_ips_by_equip(equip.get("id"))
    except NetworkAPIClientError as e:
        logger.error(e)
        status_code = 500
        return HttpResponse(json.dumps({'message': e.error, 'status': 'error'}),
                            status=status_code,
                            content_type='application/json')

    if not ips_list['ips']['ipv4'] and not ips_list['ips']['ipv6']:
        return HttpResponse(json.dumps({'message': u'Esse equipamento não tem nenhum IP que '
                                                   u'possa ser utilizado como DHCP server dessa rede.',
                                        'status': 'error'}),
                            status=status_code,
                            content_type='application/json')

    ips['list_ipv4'] = ips_list['ips']['ipv4']
    ips['list_ipv6'] = ips_list['ips']['ipv6']

    lists['ips'] = ips
    lists['equip'] = equip

    for ip in lists['ips']['list_ipv4']:
        ip['ip'] = "%s.%s.%s.%s" % (ip['oct1'], ip['oct2'], ip['oct3'], ip['oct4'])
    for ip in lists['ips']['list_ipv6']:
        ip['ip'] = "%s:%s:%s:%s:%s:%s:%s:%s" % (ip['bloco1'], ip['bloco2'], ip['bloco3'],
                                                ip['bloco4'], ip['bloco5'],
                                                ip['bloco6'], ip['bloco7'], ip['bloco8'])

    return HttpResponse(
        loader.render_to_string(
            AJAX_IPLIST_EQUIPMENT_DHCP_SERVER_HTML,
            lists,
            context_instance=RequestContext(request)
        ), status=status_code
    )


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True},
           {"permission": ENVIRONMENT_VIP, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def available_evip(request):

    lists = {}
    id_vlan = request.GET['id_vlan']

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    lists['items'] = client.create_environment_vip().list_all_available(
        id_vlan).get('environment_vip')

    response = HttpResponse(loader.render_to_string(
        NET_EVIP_OPTIONS, lists, context_instance=RequestContext(request)))
    response.status_code = 200
    return response


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def list_netip4_by_id(request, id_net='0', id_vlan='0', sf_number='0',
                      sf_name='0', sf_environment='0', sf_nettype='0',
                      sf_subnet='0', sf_ipversion='0', sf_network='0',
                      sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_net'] = id_net
    lists['id_vlan'] = id_vlan
    lists['sf_number'] = sf_number
    lists['sf_name'] = sf_name
    lists['sf_environment'] = sf_environment
    lists['sf_nettype'] = sf_nettype
    lists['sf_subnet'] = sf_subnet
    lists['sf_ipversion'] = sf_ipversion
    lists['sf_network'] = sf_network
    lists['sf_iexact'] = sf_iexact
    lists['sf_acl'] = sf_acl
    lists['dhcp_relays'] = list()

    try:

        lists['aba'] = 0
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # recuperando lista de vlans
        net = client.create_network().get_network_ipv4(id_net)

        vlan = client.create_vlan().get(net.get('network').get('vlan'))
        lists['vlan_id'] = vlan['vlan']['id']

        dhcp_relays = client.create_dhcprelay_ipv4().list(networkipv4=id_net)
        for dhcp in dhcp_relays:
            lists['dhcp_relays'].append(dhcp['ipv4'])

        lists['num_vlan'] = vlan['vlan']['num_vlan']
        lists['vxlan'] = vlan.get('vlan').get('vxlan')

        net['network']['vlan'] = vlan.get('vlan').get('nome')

        net_type = client.create_tipo_rede().listar()

        id_vip = net.get('network').get("ambient_vip")

        if id_vip is None:
            id_vip = 0

        else:

            lists['vip'] = client.create_environment_vip().search(
                id_vip).get("environment_vip")
            opts = client.create_option_vip().get_all()
            options_vip = client.create_option_vip().get_option_vip(id_vip)
            choice_opts = []
            if options_vip is not None:
                options_vip = options_vip.get('option_vip')

                if type(options_vip) == dict:
                    options_vip = [options_vip]

                for opt in options_vip:
                    choice_opts.append(opt.get("id"))

            lists['opt_form'] = OptionVipNetForm(
                opts, initial={'option_vip': choice_opts})

        lists['id_vip'] = id_vip

        lists['net'] = replace_id_to_name(
            [net['network']], net_type['net_type'], "network_type", "id", "name")

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('vlan.search.list')

    try:

        ips = client.create_ip().find_ip4_by_network(id_net)

        ips = ips.get('ips')

        ips_to_screen = []

        list_nomes = []

        for ip in ips:
            list_nomes = []
            if type(ip.get('equipamento')) == list:
                for equip in ip.get('equipamento'):
                    ip2 = dict()
                    ip2['id'] = ip['id']
                    ip2['oct1'] = ip['oct1']
                    ip2['oct2'] = ip['oct2']
                    ip2['oct3'] = ip['oct3']
                    ip2['oct4'] = ip['oct4']
                    ip2['descricao'] = ip['descricao']
                    ip2['equip_name'] = equip.get('nome')
                    ip2['equip_id'] = equip.get('id')
                    ips_to_screen.append(ip2)

                    list_nomes.append(equip.get('nome'))

                ip['equipamento'] = list_nomes
            else:
                ip2 = dict()
                ip2['id'] = ip['id']
                ip2['oct1'] = ip['oct1']
                ip2['oct2'] = ip['oct2']
                ip2['oct3'] = ip['oct3']
                ip2['oct4'] = ip['oct4']
                ip2['descricao'] = ip['descricao']
                ip2['equip_name'] = ip.get('equipamento').get('nome')
                ip2['equip_id'] = ip.get('equipamento').get('id')
                ips_to_screen.append(ip2)

                list_nomes = [ip.get('equipamento').get('nome')]
                ip['equipamento'] = list_nomes

        lists['ips'] = ips_to_screen
        lists['id'] = id_net
        lists['delete_form'] = DeleteForm()
        return render_to_response(NETIPV4, lists, context_instance=RequestContext(request))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists['ips'] = None
    except TypeError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    lists['id'] = id_net
    lists['delete_form'] = DeleteForm()
    return render_to_response(NETIPV4, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def list_netip6_by_id(request, id_net='0', id_vlan='0', sf_number='0',
                      sf_name='0', sf_environment='0', sf_nettype='0',
                      sf_subnet='0', sf_ipversion='0', sf_network='0',
                      sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_vlan'] = id_vlan
    lists['sf_number'] = sf_number
    lists['sf_name'] = sf_name
    lists['sf_environment'] = sf_environment
    lists['sf_nettype'] = sf_nettype
    lists['sf_subnet'] = sf_subnet
    lists['sf_ipversion'] = sf_ipversion
    lists['sf_network'] = sf_network
    lists['sf_iexact'] = sf_iexact
    lists['sf_acl'] = sf_acl
    lists['dhcp_relays'] = list()

    try:

        lists['aba'] = 0
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # recuperando lista de vlans
        net = client.create_network().get_network_ipv6(id_net)

        vlan = client.create_vlan().get(net.get('network').get('vlan'))
        lists['vlan_id'] = vlan.get('vlan')['id']
        lists['vxlan'] = vlan.get('vlan').get('vxlan')

        dhcp_relays = client.create_dhcprelay_ipv4().list(networkipv4=id_net)
        for dhcp in dhcp_relays:
            lists['dhcp_relays'].append(dhcp['ipv4'])

        net['network']['vlan'] = vlan.get('vlan').get('nome')

        lists['num_vlan'] = vlan['vlan']['num_vlan']
        net_type = client.create_tipo_rede().listar()

        id_vip = net.get('network').get("ambient_vip")

        if id_vip is None:
            id_vip = 0

        else:

            lists['vip'] = client.create_environment_vip().search(
                id_vip).get("environment_vip")
            opts = client.create_option_vip().get_all()
            options_vip = client.create_option_vip().get_option_vip(id_vip)
            choice_opts = []
            if options_vip is not None:
                options_vip = options_vip.get('option_vip')

                if type(options_vip) == dict:
                    options_vip = [options_vip]

                for opt in options_vip:
                    choice_opts.append(opt.get("id"))

            lists['opt_form'] = OptionVipNetForm(
                opts, initial={'option_vip': choice_opts})

        lists['id_vip'] = id_vip

        lists['net'] = replace_id_to_name(
            [net['network']], net_type['net_type'], "network_type", "id", "name")

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('vlan.search.list')

    try:

        ips = client.create_ip().find_ip6_by_network(id_net)

        ips = ips.get('ips')

        ips_to_screen = []

        list_nomes = []

        for ip in ips:
            list_nomes = []
            if type(ip.get('equipamento')) == list:
                for equip in ip.get('equipamento'):
                    ip2 = dict()
                    ip2['id'] = ip['id']
                    ip2['block1'] = ip['block1']
                    ip2['block2'] = ip['block2']
                    ip2['block3'] = ip['block3']
                    ip2['block4'] = ip['block4']
                    ip2['block5'] = ip['block5']
                    ip2['block6'] = ip['block6']
                    ip2['block7'] = ip['block7']
                    ip2['block8'] = ip['block8']
                    ip2['descricao'] = ip['descricao']
                    ip2['equip_name'] = equip.get('nome')
                    ip2['equip_id'] = equip.get('id')
                    ips_to_screen.append(ip2)

                    list_nomes.append(equip.get('nome'))

                ip['equipamento'] = list_nomes
            else:
                ip2 = dict()
                ip2['id'] = ip['id']
                ip2['block1'] = ip['block1']
                ip2['block2'] = ip['block2']
                ip2['block3'] = ip['block3']
                ip2['block4'] = ip['block4']
                ip2['block5'] = ip['block5']
                ip2['block6'] = ip['block6']
                ip2['block7'] = ip['block7']
                ip2['block8'] = ip['block8']
                ip2['descricao'] = ip['descricao']
                ip2['equip_name'] = ip.get('equipamento').get('nome')
                ip2['equip_id'] = ip.get('equipamento').get('id')
                ips_to_screen.append(ip2)

                list_nomes = [ip.get('equipamento').get('nome')]
                ip['equipamento'] = list_nomes

        lists['ips'] = ips_to_screen
        lists['id'] = id_net
        lists['delete_form'] = DeleteForm()

        return render_to_response(NETIPV6, lists, context_instance=RequestContext(request))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists['ips'] = None
    except TypeError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists['id'] = id_net
    lists['delete_form'] = DeleteForm()
    return render_to_response(NETIPV6, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def insert_ip4(request, id_net='0', id_vlan='0', sf_number='0',
               sf_name='0', sf_environment='0', sf_nettype='0',
               sf_subnet='0', sf_ipversion='0', sf_network='0',
               sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_vlan'] = id_vlan
    lists['sf_number'] = sf_number
    lists['sf_name'] = sf_name
    lists['sf_environment'] = sf_environment
    lists['sf_nettype'] = sf_nettype
    lists['sf_subnet'] = sf_subnet
    lists['sf_ipversion'] = sf_ipversion
    lists['sf_network'] = sf_network
    lists['sf_iexact'] = sf_iexact
    lists['sf_acl'] = sf_acl
    lists['id'] = id_net
    lists['form'] = IPForm()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        try:
            client.create_network().get_network_ipv4(id_net)
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list')

        if request.method == 'POST':

            form = IPForm(request.POST)
            lists['form'] = form

            if form.is_valid():

                equip_name = form.cleaned_data['equip_name']
                descricao = form.cleaned_data['descricao']
                oct1 = request.POST['oct1']
                oct2 = request.POST['oct2']
                oct3 = request.POST['oct3']
                oct4 = request.POST['oct4']
                ip = "%s.%s.%s.%s" % (oct1, oct2, oct3, oct4)

                if not (is_valid_ipv4(ip)):
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("ip_error"))
                    lists['id'] = id_net
                    lists['form'] = form
                    lists['oct1'] = oct1
                    lists['oct2'] = oct2
                    lists['oct3'] = oct3
                    lists['oct4'] = oct4
                    return render_to_response(IP4, lists,
                                              context_instance=RequestContext(request))

                else:
                    try:
                        equip = client.create_equipamento().listar_por_nome(
                            equip_name)
                        equip = equip.get('equipamento').get('id')
                        client.create_ip().save_ipv4(
                            ip, equip, descricao, id_net)
                        messages.add_message(
                            request, messages.SUCCESS, network_ip_messages.get("ip_sucess"))
                        return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                                            args=[id_net, id_vlan, sf_number,
                                                                  sf_name, sf_environment,
                                                                  sf_nettype, sf_subnet,
                                                                  sf_ipversion, sf_network,
                                                                  sf_iexact, sf_acl]))

                    except NetworkAPIClientError as e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['id'] = id_net
                        lists['form'] = form
                        lists['oct1'] = oct1
                        lists['oct2'] = oct2
                        lists['oct3'] = oct3
                        lists['oct4'] = oct4

                        return render_to_response(IP4, lists,
                                                  context_instance=RequestContext(request))

        ip = client.create_ip().get_available_ip4(id_net)
        ip = ip.get('ip')
        ip = ip.get('ip')
        ip = ip.split(".")
        lists['oct1'] = ip[0]
        lists['oct2'] = ip[1]
        lists['oct3'] = ip[2]
        lists['oct4'] = ip[3]

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(IP4, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def insert_ip6(request, id_net='0', id_vlan='0', sf_number='0', sf_name='0',
               sf_environment='0', sf_nettype='0', sf_subnet='0',
               sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_vlan'] = id_vlan
    lists['sf_number'] = sf_number
    lists['sf_name'] = sf_name
    lists['sf_environment'] = sf_environment
    lists['sf_nettype'] = sf_nettype
    lists['sf_subnet'] = sf_subnet
    lists['sf_ipversion'] = sf_ipversion
    lists['sf_network'] = sf_network
    lists['sf_iexact'] = sf_iexact
    lists['sf_acl'] = sf_acl
    lists['id'] = id_net
    lists['form'] = IPForm()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        try:
            client.create_network().get_network_ipv6(id_net)
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list')

        if request.method == 'POST':

            form = IPForm(request.POST)
            lists['form'] = form

            if form.is_valid():

                equip_name = form.cleaned_data['equip_name']
                descricao = form.cleaned_data['descricao']
                block1 = request.POST['block1']
                block2 = request.POST['block2']
                block3 = request.POST['block3']
                block4 = request.POST['block4']
                block5 = request.POST['block5']
                block6 = request.POST['block6']
                block7 = request.POST['block7']
                block8 = request.POST['block8']
                ip6 = "%s:%s:%s:%s:%s:%s:%s:%s" % (
                    block1, block2, block3, block4, block5, block6, block7, block8)

                if not (is_valid_ipv6(ip6)):
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("ip_error"))
                    lists['id'] = id_net
                    lists['form'] = form
                    lists['block1'] = block1
                    lists['block2'] = block2
                    lists['block3'] = block3
                    lists['block4'] = block4
                    lists['block5'] = block5
                    lists['block6'] = block6
                    lists['block7'] = block7
                    lists['block8'] = block8
                    return render_to_response(IP6, lists,
                                              context_instance=RequestContext(request))

                else:
                    try:
                        equip = client.create_equipamento().listar_por_nome(
                            equip_name)
                        equip = equip.get('equipamento').get('id')
                        client.create_ip().save_ipv6(
                            ip6, equip, descricao, id_net)
                        messages.add_message(
                            request, messages.SUCCESS, network_ip_messages.get("ip_sucess"))
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id',
                                                            args=[id_net, id_vlan, sf_number,
                                                                  sf_name, sf_environment,
                                                                  sf_nettype, sf_subnet,
                                                                  sf_ipversion, sf_network,
                                                                  sf_iexact, sf_acl]))

                    except NetworkAPIClientError as e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['id'] = id_net
                        lists['form'] = form
                        lists['block1'] = block1
                        lists['block2'] = block2
                        lists['block3'] = block3
                        lists['block4'] = block4
                        lists['block5'] = block5
                        lists['block6'] = block6
                        lists['block7'] = block7
                        lists['block8'] = block8

                        return render_to_response(IP6, lists, context_instance=RequestContext(request))

        ip = client.create_ip().get_available_ip6(id_net)
        ip = ip.get('ip6')
        ip = ip.get('ip6')
        ip = ip.split(":")
        lists['block1'] = ip[0]
        lists['block2'] = ip[1]
        lists['block3'] = ip[2]
        lists['block4'] = ip[3]
        lists['block5'] = ip[4]
        lists['block6'] = ip[5]
        lists['block7'] = ip[6]
        lists['block8'] = ip[7]

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(IP6, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def edit_ip4(request, id_net, id_ip4, id_vlan='0', sf_number='0', sf_name='0',
             sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0',
             sf_network='0', sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_net'] = id_net
    lists['id_vlan'] = id_vlan
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
        form = IPEditForm()

        try:
            client.create_network().get_network_ipv4(id_net)
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list')

        if request.method == 'POST':
            form = IPEditForm(request.POST)
            lists['form'] = form

            if form.is_valid():

                descricao = form.cleaned_data['descricao']
                oct1 = request.POST['oct1']
                oct2 = request.POST['oct2']
                oct3 = request.POST['oct3']
                oct4 = request.POST['oct4']
                equipamentos = form.cleaned_data['equip_names']
                ip = "%s.%s.%s.%s" % (oct1, oct2, oct3, oct4)

                if not (is_valid_ipv4(ip)):
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("ip_error"))
                    lists['equipamentos'] = equipamentos
                    lists['id_net'] = id_net
                    lists['id_ip'] = id_ip4
                    lists['form'] = form
                    lists['oct1'] = oct1
                    lists['oct2'] = oct2
                    lists['oct3'] = oct3
                    lists['oct4'] = oct4
                    return render_to_response(IP4EDIT, lists,
                                              context_instance=RequestContext(request))

                else:
                    try:
                        client.create_ip().edit_ipv4(ip, descricao, id_ip4)
                        messages.add_message(
                            request, messages.SUCCESS, network_ip_messages.get("ip_edit_sucess"))
                        return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                                            args=[id_net, id_vlan, sf_number,
                                                                  sf_name, sf_environment,
                                                                  sf_nettype, sf_subnet,
                                                                  sf_ipversion, sf_network,
                                                                  sf_iexact, sf_acl]))

                    except NetworkAPIClientError as e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['equipamentos'] = equipamentos
                        lists['id_net'] = id_net
                        lists['id_ip'] = id_ip4
                        lists['form'] = form
                        lists['oct1'] = oct1
                        lists['oct2'] = oct2
                        lists['oct3'] = oct3
                        lists['oct4'] = oct4

                        return render_to_response(IP4EDIT, lists,
                                                  context_instance=RequestContext(request))
            else:
                lists['equipamentos'] = request.POST['equip_names']
                lists['id_net'] = id_net
                lists['id_ip'] = id_ip4
                lists['form'] = form
                lists['oct1'] = request.POST['oct1']
                lists['oct2'] = request.POST['oct2']
                lists['oct3'] = request.POST['oct3']
                lists['oct4'] = request.POST['oct4']
                return render_to_response(IP4EDIT, lists, context_instance=RequestContext(request))

        if request.method == 'GET':

            ip = client.create_ip().find_ip4_by_id(id_ip4)
            ip = ip.get('ips')
            equipamentos = ip.get('equipamento')
            nomesEquipamentos = ''
            cont = 0
            if type(ip.get('equipamento')) == dict:
                nomesEquipamentos = equipamentos.get('nome')
            else:
                for equip in ip.get('equipamento'):
                    cont = cont + 1
                    if (cont == len(ip.get('equipamento'))):
                        nomesEquipamentos = nomesEquipamentos + \
                            equip.get('nome')
                    else:
                        nomesEquipamentos = nomesEquipamentos + \
                            equip.get('nome') + ', '

            lists['equipamentos'] = nomesEquipamentos
            lists['form'] = IPEditForm(
                initial={'descricao': ip.get('descricao'), 'equip_names': nomesEquipamentos})
            lists['oct1'] = ip.get('oct1')
            lists['oct2'] = ip.get('oct2')
            lists['oct3'] = ip.get('oct3')
            lists['oct4'] = ip.get('oct4')
            lists['id_net'] = id_net
            lists['id_ip'] = ip.get('id')

            return render_to_response(IP4EDIT, lists, context_instance=RequestContext(request))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                        args=[id_net, id_vlan, sf_number, sf_name,
                                              sf_environment, sf_nettype, sf_subnet,
                                              sf_ipversion, sf_network, sf_iexact, sf_acl]))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def edit_ip6(request, id_net, id_ip6, id_vlan='0', sf_number='0', sf_name='0',
             sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0',
             sf_network='0', sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_net'] = id_net
    lists['id_vlan'] = id_vlan
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
        form = IPEditForm()

        try:
            client.create_network().get_network_ipv6(id_net)
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list')

        if request.method == 'POST':
            form = IPEditForm(request.POST)
            lists['form'] = form

            if form.is_valid():

                equipamentos = form.cleaned_data['equip_names']
                descricao = form.cleaned_data['descricao']
                block1 = request.POST['block1']
                block2 = request.POST['block2']
                block3 = request.POST['block3']
                block4 = request.POST['block4']
                block5 = request.POST['block5']
                block6 = request.POST['block6']
                block7 = request.POST['block7']
                block8 = request.POST['block8']
                ip6 = "%s:%s:%s:%s:%s:%s:%s:%s" % (
                    block1, block2, block3, block4, block5, block6, block7, block8)

                if not (is_valid_ipv6(ip6)):
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("ip6_error"))
                    lists['id_net'] = id_net
                    lists['id_ip6'] = id_ip6
                    lists['form'] = form
                    lists['equipamentos'] = equipamentos
                    lists['block1'] = block1
                    lists['block2'] = block2
                    lists['block3'] = block3
                    lists['block4'] = block4
                    lists['block5'] = block5
                    lists['block6'] = block6
                    lists['block7'] = block7
                    lists['block8'] = block8
                    return render_to_response(IP6EDIT, lists, context_instance=RequestContext(request))

                else:
                    try:
                        client.create_ip().edit_ipv6(ip6, descricao, id_ip6)
                        messages.add_message(
                            request, messages.SUCCESS, network_ip_messages.get("ip_edit_sucess"))
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id',
                                                            args=[id_net, id_vlan, sf_number,
                                                                  sf_name, sf_environment,
                                                                  sf_nettype, sf_subnet,
                                                                  sf_ipversion, sf_network,
                                                                  sf_iexact, sf_acl]))

                    except NetworkAPIClientError as e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['id_net'] = id_net
                        lists['id_ip6'] = id_ip6
                        lists['form'] = form
                        lists['equipamentos'] = equipamentos
                        lists['block1'] = block1
                        lists['block2'] = block2
                        lists['block3'] = block3
                        lists['block4'] = block4
                        lists['block5'] = block5
                        lists['block6'] = block6
                        lists['block7'] = block7
                        lists['block8'] = block8

                        return render_to_response(IP6EDIT, lists,
                                                  context_instance=RequestContext(request))
            else:

                lists['equipamentos'] = request.POST['equip_names']
                lists['id_net'] = id_net
                lists['id_ip6'] = id_ip6
                lists['form'] = form
                ip = client.create_ip().get_available_ip6(id_net)
                ip = ip.get('ip6')
                ip = ip.get('ip6')
                ip = ip.split(":")
                lists['block1'] = ip[0]
                lists['block2'] = ip[1]
                lists['block3'] = ip[2]
                lists['block4'] = ip[3]
                lists['block5'] = ip[4]
                lists['block6'] = ip[5]
                lists['block7'] = ip[6]
                lists['block8'] = ip[7]
                return render_to_response(IP6EDIT, lists,
                                          context_instance=RequestContext(request))

        if request.method == 'GET':

            ip = client.create_ip().find_ip6_by_id(id_ip6)
            ip = ip.get('ips')
            equipamentos = ip.get('equipamento')
            nomesEquipamentos = ''
            cont = 0
            if type(ip.get('equipamento')) == dict:
                nomesEquipamentos = equipamentos.get('nome')
            else:
                for equip in ip.get('equipamento'):
                    cont = cont + 1
                    if (cont == len(ip.get('equipamento'))):
                        nomesEquipamentos = nomesEquipamentos + \
                            equip.get('nome')
                    else:
                        nomesEquipamentos = nomesEquipamentos + \
                            equip.get('nome') + ', '

            lists['equipamentos'] = nomesEquipamentos
            lists['form'] = IPEditForm(
                initial={'descricao': ip.get('descricao'),
                         'equip_names': nomesEquipamentos})
            lists['id_net'] = id_net
            lists['id_ip6'] = id_ip6
            lists['block1'] = ip.get('block1')
            lists['block2'] = ip.get('block2')
            lists['block3'] = ip.get('block3')
            lists['block4'] = ip.get('block4')
            lists['block5'] = ip.get('block5')
            lists['block6'] = ip.get('block6')
            lists['block7'] = ip.get('block7')
            lists['block8'] = ip.get('block8')

            return render_to_response(IP6EDIT, lists,
                                      context_instance=RequestContext(request))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('network.ip6.list.by.id',
                                        args=[id_net, id_vlan, sf_number, sf_name,
                                              sf_environment, sf_nettype, sf_subnet,
                                              sf_ipversion, sf_network, sf_iexact, sf_acl]))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def delete_ip4(request, id_net, id_vlan='0', sf_number='0', sf_name='0',
               sf_environment='0', sf_nettype='0', sf_subnet='0',
               sf_ipversion='0', sf_network='0', sf_iexact='0', sf_acl='0'):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        if request.method == 'POST':

            # Verifica se a rede passada realmente existe
            try:
                client.create_network().get_network_ipv4(id_net)
            except NetworkAPIClientError as e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                redirect('vlan.search.list')

            form = DeleteForm(request.POST)

            if form.is_valid():
                # Get user
                ip_client = client.create_ip()
                equip_client = client.create_equipamento()

                # All ids to be deleted
                ids = form.cleaned_data['ids']
                if ids is None or len(ids) <= 0:
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("select_one"))
                    return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                                        args=[id_net, id_vlan, sf_number,
                                                              sf_name, sf_environment,
                                                              sf_nettype, sf_subnet,
                                                              sf_ipversion, sf_network,
                                                              sf_iexact, sf_acl]))

                ids_eqs = split_to_array(ids)
                ids = []
                eq_ids = []

                for elem in ids_eqs:
                    elem_sep = split_to_array(elem, '-')
                    ids.append(elem_sep[0])
                    eq_ids.append(elem_sep[1])

                ips = ip_client.find_ip4_by_network(id_net)
                ips = ips.get('ips')

                # Verifica se Ip pertence e Rede passada
                listaIps = []

                for i in ips:
                    listaIps.append(i.get('id'))

                for id in ids:
                    if id not in listaIps:
                        messages.add_message(
                            request, messages.ERROR,
                            network_ip_messages.get("not_ip_in_net") % (id, id_net))
                        return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                                            args=[id_net, id_vlan, sf_number,
                                                                  sf_name, sf_environment,
                                                                  sf_nettype, sf_subnet,
                                                                  sf_ipversion, sf_network,
                                                                  sf_iexact, sf_acl]))

                error_list = list()
                success_count = 0

                # remove ip equipment associations, and ip if its the last
                # ip-equipment
                try:
                    for i in range(0, len(ids)):
                        equip_client.remover_ip(eq_ids[i], ids[i])
                        success_count += 1

                except (VipIpError, IpEquipCantDissociateFromVip) as e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    error_list.append(ids[i])

                except NetworkAPIClientError as e:
                    error_list.append(ids[i])

                if len(error_list) == len(ids):
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("can_not_remove_all"))
                    return list_netip4_by_id(request, id_net)

                elif len(error_list) > 0:
                    msg = ""

                    if success_count > 0:
                        messages.add_message(
                            request, messages.SUCCESS, network_ip_messages.get("ip_delete_sucess"))

                    for id_error in error_list:
                        msg = msg + id_error + ", "
                        msg = error_messages.get("can_not_remove") % msg[:-2]
                        messages.add_message(request, messages.WARNING, msg)
                        return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                                            args=[id_net, id_vlan, sf_number,
                                                                  sf_name, sf_environment,
                                                                  sf_nettype, sf_subnet,
                                                                  sf_ipversion, sf_network,
                                                                  sf_iexact, sf_acl]))

                else:
                    messages.add_message(
                        request, messages.SUCCESS, network_ip_messages.get("ip_delete_sucess"))
                    return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                                        args=[id_net, id_vlan, sf_number,
                                                              sf_name, sf_environment,
                                                              sf_nettype, sf_subnet,
                                                              sf_ipversion, sf_network,
                                                              sf_iexact, sf_acl]))

            else:
                messages.add_message(
                    request, messages.ERROR, error_messages.get("select_one"))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                        args=[id_net, id_vlan, sf_number, sf_name,
                                              sf_environment, sf_nettype, sf_subnet,
                                              sf_ipversion, sf_network, sf_iexact,
                                              sf_acl]))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def delete_ip6(request, id_net):
    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        if request.method == 'POST':

            # Verifica se a rede passada realmente existe
            try:
                client.create_network().get_network_ipv6(id_net)
            except NetworkAPIClientError as e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                redirect('vlan.search.list')

            form = DeleteForm(request.POST)

            if form.is_valid():
                # Get user
                ip_client = client.create_ip()
                equip_client = client.create_equipamento()

                # All ids to be deleted
                ids = form.cleaned_data['ids']
                if ids is None or len(ids) <= 0:
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("select_one"))
                    return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))

                ids_eqs = split_to_array(ids)
                ids = []
                eq_ids = []

                for elem in ids_eqs:
                    elem_sep = split_to_array(elem, '-')
                    ids.append(elem_sep[0])
                    eq_ids.append(elem_sep[1])

                ips = ip_client.find_ip6_by_network(id_net)
                ips = ips.get('ips')

                # Verifica se Ip pertence e Rede passada
                listaIps = []

                for i in ips:
                    listaIps.append(i.get('id'))

                for id in ids:
                    if id not in listaIps:
                        messages.add_message(
                            request, messages.ERROR,
                            network_ip_messages.get("not_ip_in_net") % (id, id_net))
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id',
                                                            args=[id_net]))

                error_list = list()
                success_count = 0
                # remove ip equipment associations, and ip if its the last
                # ip-equipment
                try:
                    for i in range(0, len(ids)):
                        equip_client.remove_ipv6(eq_ids[i], ids[i])
                        success_count += 1

                except VipIpError as e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    error_list.append(ids[i])

                except NetworkAPIClientError as e:
                    error_list.append(ids[i])

                if len(error_list) == len(ids):
                    messages.add_message(
                        request, messages.ERROR, error_messages.get("can_not_remove_all"))
                    return list_netip6_by_id(request, id_net)

                elif len(error_list) > 0:
                    msg = ""

                    if success_count > 0:
                        messages.add_message(
                            request, messages.SUCCESS,
                            network_ip_messages.get("ip_delete_sucess"))

                    for id_error in error_list:
                        msg = msg + id_error + ", "
                        msg = error_messages.get("can_not_remove") % msg[:-2]
                        messages.add_message(request, messages.WARNING, msg)
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id',
                                                            args=[id_net]))

                else:
                    messages.add_message(
                        request, messages.SUCCESS,
                        network_ip_messages.get("ip_delete_sucess"))
                    return HttpResponseRedirect(reverse('network.ip6.list.by.id',
                                                        args=[id_net]))

            else:
                messages.add_message(
                    request, messages.ERROR, error_messages.get("select_one"))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True},
           {"permission": ENVIRONMENT_VIP, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def edit_network4_form(request, id_net='0', id_vlan='0', sf_number='0',
                       sf_name='0', sf_environment='0',
                       sf_nettype='0', sf_subnet='0', sf_ipversion='0',
                       sf_network='0', sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_vlan'] = id_vlan
    lists['sf_number'] = sf_number
    lists['sf_name'] = sf_name
    lists['sf_environment'] = sf_environment
    lists['sf_nettype'] = sf_nettype
    lists['sf_subnet'] = sf_subnet
    lists['sf_ipversion'] = sf_ipversion
    lists['sf_network'] = sf_network
    lists['sf_iexact'] = sf_iexact
    lists['sf_acl'] = sf_acl

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    # Get all needs from NetworkAPI
    net_type_list = client.create_tipo_rede().listar()
    env_vip_list = client.create_environment_vip().list_all()
    try:
        network = client.create_network().get_network_ipv4(id_net)
        network = network.get("network")
    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        redirect('vlan.search.list')

    try:

        lists['id_net'] = network.get('id')
        lists['broadcast'] = network.get('broadcast')
        lists['oct1'] = network.get("oct1")
        lists['oct2'] = network.get("oct2")
        lists['oct3'] = network.get("oct3")
        lists['oct4'] = network.get("oct4")
        lists['block_net'] = network.get("block")

        if request.method == 'POST':

            form = NetworkEditForm(net_type_list, env_vip_list, request.POST)
            lists['form'] = form
            id_ips_list = request.POST.getlist('id_ip')
            id_ips = list()
            for item in id_ips_list:
                id_ips.append(int(item))

            if form.is_valid():

                env_vip = form.cleaned_data['env_vip']
                net_type = form.cleaned_data['net_type']
                ip_type = 0

                if env_vip:
                    cluster_unit = form.cleaned_data['cluster_unit']
                    cluster_unit = cluster_unit if cluster_unit else 'cluster-unit-1'
                else:
                    cluster_unit = None

                client.create_network().edit_network(
                    id_net, ip_type, net_type, env_vip, cluster_unit)

                dhcp_list = client.create_dhcprelay_ipv4().list(networkipv4=network.get('id'))
                dhcp_id_ip_list = list()
                for dhcp in dhcp_list:
                    dhcp_id_ip_list.append(dhcp['ipv4']['id'])

                dhcp_to_remove = list()
                dhcp_to_add = list()
                for id_ip in id_ips:
                    if id_ip not in dhcp_id_ip_list:
                        dhcp_to_add.append(id_ip)
                for id_ip in dhcp_id_ip_list:
                    if id_ip not in id_ips:
                        dhcp_to_remove.append(id_ip)

                for dhcp_id_ip in dhcp_to_add:
                    client.create_dhcprelay_ipv4().add(network.get("id"), dhcp_id_ip)
                for dhcp_id_ip in dhcp_to_remove:
                    for dhcp in dhcp_list:
                        if dhcp_id_ip == dhcp['ipv4']['id']:
                            client.create_dhcprelay_ipv4().remove(dhcp['id'])

                messages.add_message(
                    request, messages.SUCCESS, network_ip_messages.get("sucess_edit"))

                return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                                    args=[id_net, id_vlan, sf_number,
                                                          sf_name, sf_environment,
                                                          sf_nettype, sf_subnet,
                                                          sf_ipversion, sf_network,
                                                          sf_iexact, sf_acl]))

        # Get
        else:

            env_vip = network.get("ambient_vip")
            net_type = network.get("network_type")
            cluster_unit = network.get("cluster_unit")
            ip_version = 0
            vlan_id = network.get('vlan')
            vlan = client.create_vlan().get(vlan_id)
            vlan = vlan.get("vlan")
            environment = client.create_ambiente().buscar_por_id(
                vlan.get("ambiente")).get("ambiente")
            vlan_nome = "%s | %s - %s - %s" % (vlan.get("num_vlan"),
                                               environment.get("nome_divisao"),
                                               environment.get("nome_ambiente_logico"),
                                               environment.get("nome_grupo_l3"))
            lists['form'] = NetworkEditForm(
                net_type_list,
                env_vip_list,
                initial={
                    'vlan_name': vlan_nome, 
                    'net_type': net_type,
                    'env_vip': env_vip,
                    'cluster_unit': cluster_unit,
                    'ip_version': ip_version
                }
            )

            dhcp_relays_ipv4 = client.create_dhcprelay_ipv4().list(
                networkipv4=network.get('id'))
            dhcp_relays = list()
            for dhcp in dhcp_relays_ipv4:
                dhcp_dict = dict()
                dhcp_dict['ip'] = dhcp['ipv4']['ip_formated']
                dhcp_dict['id_ip'] = dhcp['ipv4']['id']
                equip_nome = client.create_ip().get_ipv4(
                    dhcp['ipv4']['id']).get('ipv4').get('equipamentos')[0]
                equip = client.create_equipamento().listar_por_nome(equip_nome)
                dhcp_dict['nome_equipamento'] = equip_nome
                dhcp_dict['id_equip'] = equip.get('equipamento').get('id')
                dhcp_relays.append(dhcp_dict)

            lists['dhcp_relays'] = dhcp_relays

    except NetworkAPIClientError as e:

        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(NET4_EDIT, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True},
           {"permission": ENVIRONMENT_VIP, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def edit_network6_form(request, id_net='0', id_vlan='0', sf_number='0',
                       sf_name='0', sf_environment='0', sf_nettype='0',
                       sf_subnet='0', sf_ipversion='0', sf_network='0',
                       sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_vlan'] = id_vlan
    lists['sf_number'] = sf_number
    lists['sf_name'] = sf_name
    lists['sf_environment'] = sf_environment
    lists['sf_nettype'] = sf_nettype
    lists['sf_subnet'] = sf_subnet
    lists['sf_ipversion'] = sf_ipversion
    lists['sf_network'] = sf_network
    lists['sf_iexact'] = sf_iexact
    lists['sf_acl'] = sf_acl

    id_ips = None

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    # Get all needs from NetworkAPI
    net_type_list = client.create_tipo_rede().listar()
    env_vip_list = client.create_environment_vip().list_all()

    try:
        network = client.create_network().get_network_ipv6(id_net)
        network = network.get("network")
    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        redirect('vlan.search.list')

    try:

        lists['id_net'] = network.get("id")
        lists['block1'] = network.get("block1")
        lists['block2'] = network.get("block2")
        lists['block3'] = network.get("block3")
        lists['block4'] = network.get("block4")
        lists['block5'] = network.get("block5")
        lists['block6'] = network.get("block6")
        lists['block7'] = network.get("block7")
        lists['block8'] = network.get("block8")
        lists['block_net'] = network.get("block")

        if request.method == 'POST':

            form = NetworkEditForm(net_type_list, env_vip_list, request.POST)
            lists['form'] = form

            if form.is_valid():

                env_vip = form.cleaned_data['env_vip']
                net_type = form.cleaned_data['net_type']
                ip_type = 1

                if env_vip:
                    cluster_unit = form.cleaned_data['cluster_unit']
                    cluster_unit = cluster_unit if cluster_unit else 'cluster-unit-1'
                else:
                    cluster_unit = None

                client.create_network().edit_network(
                    id_net, ip_type, net_type, env_vip, cluster_unit)

                dhcp_list = client.create_dhcprelay_ipv6().list(
                    networkipv6=network.get('id'))
                dhcp_id_ip_list = list()
                for dhcp in dhcp_list:
                    dhcp_id_ip_list.append(dhcp['ipv6']['id'])

                dhcp_to_remove = list()
                dhcp_to_add = list()
                for id_ip in id_ips:
                    if id_ip not in dhcp_id_ip_list:
                        dhcp_to_add.append(id_ip)
                for id_ip in dhcp_id_ip_list:
                    if id_ip not in id_ips:
                        dhcp_to_remove.append(id_ip)

                for dhcp_id_ip in dhcp_to_add:
                    client.create_dhcprelay_ipv6().add(network.get("id"), dhcp_id_ip)
                for dhcp_id_ip in dhcp_to_remove:
                    for dhcp in dhcp_list:
                        if dhcp_id_ip == dhcp['ipv6']['id']:
                            client.create_dhcprelay_ipv6().remove(dhcp['id'])

                messages.add_message(
                    request, messages.SUCCESS, network_ip_messages.get("sucess_edit"))

                return HttpResponseRedirect(reverse('network.ip6.list.by.id',
                                                    args=[id_net, id_vlan, sf_number,
                                                          sf_name, sf_environment,
                                                          sf_nettype, sf_subnet,
                                                          sf_ipversion, sf_network,
                                                          sf_iexact, sf_acl]))

        # Get
        else:
            env_vip = network.get("ambient_vip")
            net_type = network.get("network_type")
            ip_version = 1
            vlan_id = network.get('vlan')
            vlan = client.create_vlan().get(vlan_id)
            vlan = vlan.get("vlan")
            environment = client.create_ambiente().buscar_por_id(
                vlan.get("ambiente")).get("ambiente")
            vlan_nome = "%s | %s - %s - %s" % (vlan.get("num_vlan"),
                                               environment.get("nome_divisao"),
                                               environment.get("nome_ambiente_logico"),
                                               environment.get("nome_grupo_l3"))
            lists['form'] = lists['form'] = NetworkEditForm(net_type_list,
                                                            env_vip_list,
                                                            initial={'vlan_name': vlan_nome,
                                                                     'net_type': net_type,
                                                                     'env_vip': env_vip,
                                                                     'ip_version': ip_version})

    except NetworkAPIClientError as e:

        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(NET6_EDIT, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def delete_ip4_of_equip(request, id_ip, id_equip):
    try:

        if id_ip is None or id_ip == "":
            messages.add_message(
                request, messages.SUCCESS, network_ip_messages.get("net_invalid"))
            return redirect("equipment.search.list")

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        client.create_equipamento().remover_ip(id_equip, id_ip)
        # client.create_ip().delete_ip4(id_ip)

        messages.add_message(
            request, messages.SUCCESS, network_ip_messages.get("ip_equip_delete"))

        return HttpResponseRedirect(reverse('equipment.edit.by.id', args=[id_equip]))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('equipment.edit.by.id', args=[id_equip]))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def delete_ip6_of_equip(request, id_ip, id_equip):
    try:

        if id_ip is None or id_ip == "":
            messages.add_message(
                request, messages.SUCCESS, network_ip_messages.get("net_invalid"))
            return redirect("equipment.search.list")

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        client.create_equipamento().remove_ipv6(id_equip, id_ip)
        # client.create_ip().delete_ip6(id_ip)

        messages.add_message(
            request, messages.SUCCESS, network_ip_messages.get("ip_equip_delete"))

        return HttpResponseRedirect(reverse('equipment.edit.by.id', args=[id_equip]))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('equipment.edit.by.id', args=[id_equip]))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def insert_ip6_by_equip(request, id_net, id_equip):
    lists = dict()
    lists['id'] = id_net

    if id_net is None or id_net == "":
        messages.add_message(
            request, messages.SUCCESS, network_ip_messages.get("net_invalid"))
        return redirect("equipment.search.list")

    # REDIRECIONA PARA A PAGINA PARA ENTRAR NA ACTION CORRETA,USADA APENAS
    # PARA JA INSERIR O EQUIPAMENTO
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        try:
            client.create_network().get_network_ipv6(id_net)
            equip = client.create_equipamento().listar_por_id(
                id_equip).get('equipamento')
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list')

        lists['form'] = IPForm(initial={"equip_name": equip.get('nome')})
        ip = client.create_ip().get_available_ip6(id_net)
        ip = ip.get('ip6')
        ip = ip.get('ip6')
        ip = ip.split(":")
        lists['block1'] = ip[0]
        lists['block2'] = ip[1]
        lists['block3'] = ip[2]
        lists['block4'] = ip[3]
        lists['block5'] = ip[4]
        lists['block6'] = ip[5]
        lists['block7'] = ip[6]
        lists['block8'] = ip[7]

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(IP6, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def insert_ip4_by_equip(request, id_net, id_equip):
    lists = dict()
    lists['id'] = id_net

    if id_net is None or id_net == "":
        messages.add_message(
            request, messages.SUCCESS, network_ip_messages.get("net_invalid"))
        return redirect("equipment.search.list")

    # REDIRECIONA PARA A PAGINA PARA ENTRAR NA ACTION CORRETA, USADA APENAS
    # PARA JA INSERIR O EQUIPAMENTO
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        try:
            client.create_network().get_network_ipv4(id_net)
            equip = client.create_equipamento().listar_por_id(
                id_equip).get('equipamento')
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list')

        lists['form'] = IPForm(initial={"equip_name": equip.get('nome')})
        ip = client.create_ip().get_available_ip4(id_net)
        ip = ip.get('ip').get('ip')
        ip = ip.split(".")
        lists['oct1'] = ip[0]
        lists['oct2'] = ip[1]
        lists['oct3'] = ip[2]
        lists['oct4'] = ip[3]

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(IP4, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def assoc_ip4(request, id_net, id_ip4, id_vlan='0', sf_number='0',
              sf_name='0', sf_environment='0', sf_nettype='0',
              sf_subnet='0', sf_ipversion='0', sf_network='0',
              sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_net'] = id_net
    lists['id_vlan'] = id_vlan
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
        form = IPAssocForm()

        try:
            client.create_network().get_network_ipv4(id_net)
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list')

        if request.method == 'POST':
            form = IPAssocForm(request.POST)
            lists['form'] = form

            if form.is_valid():

                flag_error = False

                oct1 = request.POST['oct1']
                oct2 = request.POST['oct2']
                oct3 = request.POST['oct3']
                oct4 = request.POST['oct4']
                equipamentos = form.cleaned_data['equip_names']
                new_equip = form.cleaned_data['equip_name']

                if new_equip in equipamentos.split(','):
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("already_assoc_equip"))
                    flag_error = True
                else:
                    equip_dict = client.create_equipamento().listar_por_nome(
                        new_equip)

                ip = "%s.%s.%s.%s" % (oct1, oct2, oct3, oct4)

                if not (is_valid_ipv4(ip)):
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("ip_error"))
                    flag_error = True

                if flag_error:
                    lists['equipamentos'] = equipamentos
                    lists['id_net'] = id_net
                    lists['id_ip'] = id_ip4
                    lists['form'] = form
                    lists['oct1'] = oct1
                    lists['oct2'] = oct2
                    lists['oct3'] = oct3
                    lists['oct4'] = oct4
                    return render_to_response(IP4ASSOC, lists,
                                              context_instance=RequestContext(request))

                else:
                    try:
                        client.create_ip().assoc_ipv4(
                            id_ip4, equip_dict['equipamento']['id'], id_net)
                        messages.add_message(
                            request, messages.SUCCESS,
                            network_ip_messages.get("ip_assoc_success"))
                        return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                                            args=[id_net, id_vlan, sf_number,
                                                                  sf_name, sf_environment,
                                                                  sf_nettype, sf_subnet,
                                                                  sf_ipversion, sf_network,
                                                                  sf_iexact, sf_acl]))

                    except NetworkAPIClientError as e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['equipamentos'] = equipamentos
                        lists['id_net'] = id_net
                        lists['id_ip'] = id_ip4
                        lists['form'] = form
                        lists['oct1'] = oct1
                        lists['oct2'] = oct2
                        lists['oct3'] = oct3
                        lists['oct4'] = oct4

                        return render_to_response(IP4ASSOC, lists,
                                                  context_instance=RequestContext(request))
            else:
                lists['equipamentos'] = request.POST['equip_names']
                lists['id_net'] = id_net
                lists['id_ip'] = id_ip4
                lists['form'] = form
                lists['oct1'] = request.POST['oct1']
                lists['oct2'] = request.POST['oct2']
                lists['oct3'] = request.POST['oct3']
                lists['oct4'] = request.POST['oct4']
                return render_to_response(IP4ASSOC, lists, context_instance=RequestContext(request))

        if request.method == 'GET':

            ip = client.create_ip().find_ip4_by_id(id_ip4)
            ip = ip.get('ips')
            equipamentos = ip.get('equipamento')
            nomesEquipamentos = ''
            cont = 0
            if type(ip.get('equipamento')) == dict:
                nomesEquipamentos = equipamentos.get('nome')
            else:
                for equip in ip.get('equipamento'):
                    cont = cont + 1
                    if (cont == len(ip.get('equipamento'))):
                        nomesEquipamentos = nomesEquipamentos + \
                            equip.get('nome')
                    else:
                        nomesEquipamentos = nomesEquipamentos + \
                            equip.get('nome') + ','

            lists['equipamentos'] = nomesEquipamentos
            lists['form'] = IPAssocForm(
                initial={'descricao': ip.get('descricao'), 'equip_names': nomesEquipamentos})
            lists['oct1'] = ip.get('oct1')
            lists['oct2'] = ip.get('oct2')
            lists['oct3'] = ip.get('oct3')
            lists['oct4'] = ip.get('oct4')

            lists['form'].fields['descricao'].widget.attrs['readonly'] = True

            lists['id_net'] = id_net
            lists['id_ip'] = ip.get('id')

            return render_to_response(IP4ASSOC, lists, context_instance=RequestContext(request))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('network.ip4.list.by.id',
                                        args=[id_net, id_vlan, sf_number,
                                              sf_name, sf_environment,
                                              sf_nettype, sf_subnet,
                                              sf_ipversion, sf_network,
                                              sf_iexact, sf_acl]))


@log
@login_required
@has_perm([{"permission": IPS, "write": True},
           {"permission": EQUIPMENT_MANAGEMENT, "read": True},
           {"permission": VLAN_MANAGEMENT, "read": True},
           {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def assoc_ip6(request, id_net, id_ip6, id_vlan='0', sf_number='0', sf_name='0',
              sf_environment='0', sf_nettype='0', sf_subnet='0', sf_ipversion='0',
              sf_network='0', sf_iexact='0', sf_acl='0'):

    lists = dict()
    lists['id_net'] = id_net
    lists['id_vlan'] = id_vlan
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
        form = IPAssocForm()

        try:
            client.create_network().get_network_ipv6(id_net)
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list')

        if request.method == 'POST':
            form = IPAssocForm(request.POST)
            lists['form'] = form

            if form.is_valid():

                flag_error = False

                block1 = request.POST['block1']
                block2 = request.POST['block2']
                block3 = request.POST['block3']
                block4 = request.POST['block4']
                block5 = request.POST['block5']
                block6 = request.POST['block6']
                block7 = request.POST['block7']
                block8 = request.POST['block8']

                equipamentos = form.cleaned_data['equip_names']
                new_equip = form.cleaned_data['equip_name']

                if new_equip in equipamentos.split(','):
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("already_assoc_equip"))
                    flag_error = True
                else:
                    equip_dict = client.create_equipamento().listar_por_nome(
                        new_equip)

                ip6 = "%s:%s:%s:%s:%s:%s:%s:%s" % (
                    block1, block2, block3, block4, block5, block6, block7, block8)

                if not (is_valid_ipv6(ip6)):
                    messages.add_message(
                        request, messages.ERROR, network_ip_messages.get("ip_error"))
                    flag_error = True

                if flag_error:
                    lists['equipamentos'] = equipamentos
                    lists['id_net'] = id_net
                    lists['id_ip'] = id_ip6
                    lists['form'] = form
                    lists['block1'] = block1
                    lists['block2'] = block2
                    lists['block3'] = block3
                    lists['block4'] = block4
                    lists['block5'] = block5
                    lists['block6'] = block6
                    lists['block7'] = block7
                    lists['block8'] = block8
                    return render_to_response(IP6ASSOC, lists,
                                              context_instance=RequestContext(request))

                else:
                    try:
                        client.create_ip().assoc_ipv6(
                            id_ip6, equip_dict['equipamento']['id'], id_net)
                        messages.add_message(
                            request, messages.SUCCESS, network_ip_messages.get("ip_assoc_success"))
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id',
                                                            args=[id_net, id_vlan, sf_number,
                                                                  sf_name, sf_environment,
                                                                  sf_nettype, sf_subnet,
                                                                  sf_ipversion, sf_network,
                                                                  sf_iexact, sf_acl]))

                    except NetworkAPIClientError as e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['equipamentos'] = equipamentos
                        lists['id_net'] = id_net
                        lists['id_ip'] = id_ip6
                        lists['form'] = form
                        lists['block1'] = block1
                        lists['block2'] = block2
                        lists['block3'] = block3
                        lists['block4'] = block4
                        lists['block5'] = block5
                        lists['block6'] = block6
                        lists['block7'] = block7
                        lists['block8'] = block8

                        return render_to_response(IP6ASSOC, lists,
                                                  context_instance=RequestContext(request))
            else:
                lists['equipamentos'] = request.POST['equip_names']
                lists['id_net'] = id_net
                lists['id_ip'] = id_ip6
                lists['form'] = form
                lists['block1'] = request.POST['block1']
                lists['block2'] = request.POST['block2']
                lists['block3'] = request.POST['block3']
                lists['block4'] = request.POST['block4']
                lists['block5'] = request.POST['block5']
                lists['block6'] = request.POST['block6']
                lists['block7'] = request.POST['block7']
                lists['block8'] = request.POST['block8']

                return render_to_response(IP6ASSOC, lists,
                                          context_instance=RequestContext(request))

        if request.method == 'GET':

            ip = client.create_ip().find_ip6_by_id(id_ip6)
            ip = ip.get('ips')
            equipamentos = ip.get('equipamento')
            nomesEquipamentos = ''
            cont = 0
            if type(ip.get('equipamento')) == dict:
                nomesEquipamentos = equipamentos.get('nome')
            else:
                for equip in ip.get('equipamento'):
                    cont = cont + 1
                    if (cont == len(ip.get('equipamento'))):
                        nomesEquipamentos = nomesEquipamentos + \
                            equip.get('nome')
                    else:
                        nomesEquipamentos = nomesEquipamentos + \
                            equip.get('nome') + ','

            lists['equipamentos'] = nomesEquipamentos
            lists['form'] = IPAssocForm(
                initial={'descricao': ip.get('descricao'), 'equip_names': nomesEquipamentos})
            lists['block1'] = ip.get('block1')
            lists['block2'] = ip.get('block2')
            lists['block3'] = ip.get('block3')
            lists['block4'] = ip.get('block4')
            lists['block5'] = ip.get('block5')
            lists['block6'] = ip.get('block6')
            lists['block7'] = ip.get('block7')
            lists['block8'] = ip.get('block8')

            lists['form'].fields['descricao'].widget.attrs['readonly'] = True

            lists['id_net'] = id_net
            lists['id_ip'] = ip.get('id')

            return render_to_response(IP6ASSOC, lists,
                                      context_instance=RequestContext(request))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('network.ip6.list.by.id',
                                        args=[id_net, id_vlan, sf_number,
                                              sf_name, sf_environment,
                                              sf_nettype, sf_subnet,
                                              sf_ipversion, sf_network,
                                              sf_iexact, sf_acl]))
