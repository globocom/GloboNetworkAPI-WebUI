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

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext
from networkapiclient.ClientFactory import ClientFactory
from networkapiclient.exception import InvalidParameterError
from networkapiclient.exception import NetworkAPIClientError
from networkapiclient.exception import UserNotAuthenticatedError
from networkapiclient.exception import VipNaoExisteError

from CadVlan import templates
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.forms import DeleteForm
from CadVlan.messages import pool_messages
from CadVlan.messages import request_vip_messages
from CadVlan.Pool import facade as facade_pool
from CadVlan.settings import NETWORK_API_PASSWORD
from CadVlan.settings import NETWORK_API_URL
from CadVlan.settings import NETWORK_API_USERNAME
from CadVlan.Util.shortcuts import render_message_json
from CadVlan.Util.utility import clone
from CadVlan.Util.utility import get_param_in_request
from CadVlan.VipRequest import forms


logger = logging.getLogger(__name__)


def get_error_mesages(operation_text):

    msg_erro = ""
    msg_sucesso = ""
    msg_erro_parcial = ""

    if operation_text == 'DELETE':

        msg_erro = 'can_not_remove_all'
        msg_sucesso = 'success_remove'
        msg_erro_parcial = 'can_not_remove'

    elif operation_text == 'CREATE':

        msg_erro = 'can_not_create_all'
        msg_sucesso = 'success_create'
        msg_erro_parcial = 'can_not_create'

    elif operation_text == 'REMOVE':

        msg_erro = 'can_not_remove2_all'
        msg_sucesso = 'success_remove2'
        msg_erro_parcial = 'can_not_remove2'

    else:
        return None, None, None

    return msg_erro, msg_sucesso, msg_erro_parcial


def get_error_messages_one(operation_text):

    msg_erro = ""
    msg_sucesso = ""

    if operation_text == 'CREATE':
        msg_erro = 'can_not_create_one'
        msg_sucesso = 'success_create_one'
    elif operation_text == 'REMOVE':
        msg_erro = 'can_not_remove_one'
        msg_sucesso = 'success_remove_one'
    else:
        return None, None

    return msg_erro, msg_sucesso


def valid_field_table_dynamic(field):
    field = clone(field)
    if field is not None:
        for i in range(0, len(field)):
            if "-" in field:
                field.remove("-")
    return field


def _validate_pools(lists, pool):

    is_valid = True

    if not pool:
        lists['pools_error'] = pool_messages.get("select_one")
        is_valid = False

    return lists, is_valid


def _valid_ports(lists, ports_vip_ports):
    '''
        Valid ports
    '''

    is_valid = True

    if ports_vip_ports is not None:
        invalid_port_vip = [i for i in ports_vip_ports if int(i) > 65535 or int(i) < 1]

        if invalid_port_vip:
            lists['pools_error'] = request_vip_messages.get("invalid_port")
            is_valid = False

        if len(ports_vip_ports) != len(set(ports_vip_ports)):
            lists['pools_error'] = request_vip_messages.get("duplicate_vip")
            is_valid = False

        if ports_vip_ports is None or not ports_vip_ports:
            lists['pools_error'] = request_vip_messages.get("error_ports")
            is_valid = False
    else:
        lists['pools_error'] = request_vip_messages.get("error_ports_required")
        is_valid = False

    return lists, is_valid


def validate_user_networkapi(user_request, is_ldap_user):

    try:

        username, password = str(user_request).split("@")

        client = ClientFactory(
            NETWORK_API_URL, NETWORK_API_USERNAME, NETWORK_API_PASSWORD)

        client_user = client.create_usuario().authenticate(
            username, password, is_ldap_user)

    except Exception, e:
        logger.error(e)
        raise UserNotAuthenticatedError(e)

    return client, client_user


def popular_client_shared(request, client_api):

    lists = dict()
    status_code = None
    lists['clients'] = ''

    try:
        finality = get_param_in_request(request, 'finality')

        if finality is None:
            raise InvalidParameterError(
                "Parâmetro inválido: O campo finalidade inválido ou não foi informado.")

        client_evip = client_api.create_api_environment_vip()

        lists['clients'] = client_evip.environmentvip_step(finality)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500

    # Returns HTML
    return HttpResponse(
        loader.render_to_string(
            templates.AJAX_VIPREQUEST_CLIENT,
            lists,
            context_instance=RequestContext(request)
        ),
        status=status_code
    )


def ajax_shared_view_vip(request, id_vip, lists):

    lists['id_vip'] = id_vip

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['vip'] = vip = client.create_api_vip_request().get_vip_request_details(id_vip).get('vips')[0]

        # apenas reals
        reals = []
        for ports in vip['ports']:
            for pool in ports['pools']:
                for real in pool['server_pool']['server_pool_members']:
                    reals.append(real)

        lists['reals'] = reals
        lists['len_porta'] = int(len(vip['ports']))
        lists['len_equip'] = int(len(vip['equipments']))

        # Returns HTML
        response = HttpResponse(
            loader.render_to_string(
                templates.VIPREQUEST_VIEW_AJAX,
                lists,
                context_instance=RequestContext(request)
            )
        )
        response.status_code = 200
        return response

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    # Returns HTML
    response = HttpResponse(
        loader.render_to_string(
            templates.VIPREQUEST_VIEW_AJAX,
            lists,
            context_instance=RequestContext(request)
        )
    )
    # Send response status with error
    response.status_code = 412
    return response


def shared_load_pool(request, client, form_acess=None, external=False):

    try:
        is_copy = request.GET.get('is_copy', 1)
        pool_id = request.GET.get('pool_id')

        action = reverse('external.save.pool') if external else reverse('save.pool')
        load_pool_url = reverse('pool.modal.ips.ajax.external') if external else reverse('pool.modal.ips.ajax')

        pool = client.create_api_pool().get_pool_details(pool_id)['server_pools'][0]
        environment_id = pool['environment']['id']

        server_pool_members = list()
        server_pool_members_raw = pool.get('server_pool_members')
        if server_pool_members_raw:
            for obj_member in server_pool_members_raw:

                ipv4 = obj_member.get('ip')
                ipv6 = obj_member.get('ipv6')
                ip_obj = ipv4 or ipv6

                # equipment = client.create_pool().get_equip_by_ip(ip_obj.get('id'))

                # get_equip_by_ip method can return many equipments related with those Ips,
                # this is an error, because the equipment returned cannot be the same

                server_pool_members.append({
                    'id': obj_member['id'],
                    'id_equip': obj_member['equipment']['id'],
                    'nome_equipamento': obj_member['equipment']['name'],
                    'priority': obj_member['priority'],
                    'port_real': obj_member['port_real'],
                    'weight': obj_member['weight'],
                    'id_ip': ip_obj.get('id'),
                    'member_status': obj_member.get('member_status'),
                    'ip': ip_obj.get('ip_formated')}
                )

        healthcheck = pool['healthcheck']['healthcheck_type']
        healthcheck_expect = pool['healthcheck']['healthcheck_expect']
        healthcheck_request = pool['healthcheck']['healthcheck_request']
        healthcheck_destination = pool['healthcheck']['destination'].split(':')[1]
        healthcheck_destination = healthcheck_destination if healthcheck_destination != '*' else ''

        form_initial = {
            'id': pool_id,
            'environment': environment_id,
            'default_port': pool.get('default_port'),
            'balancing': pool.get('lb_method'),
            'servicedownaction': pool.get('servicedownaction').get('id'),
            'maxcon': pool.get('default_limit'),
            'identifier': pool.get('identifier')
        }

        lb_method_choices = facade_pool.populate_optionsvips_choices(client)
        servicedownaction_choices = facade_pool.populate_servicedownaction_choices(client)
        healthcheck_choices = facade_pool.populate_healthcheck_choices(client)

        environment_choices = [(pool.get('environment').get('id'), pool.get('environment').get('name'))]
        form_pool = forms.PoolForm(
            environment_choices,
            lb_method_choices,
            servicedownaction_choices,
            initial=form_initial
        )

        form_initial = {
            'healthcheck': healthcheck,
            'healthcheck_request': healthcheck_request,
            'healthcheck_expect': healthcheck_expect,
            'healthcheck_destination': healthcheck_destination
        }

        form_healthcheck = forms.PoolHealthcheckForm(
            healthcheck_choices,
            initial=form_initial
        )

        if external:
            action = reverse('external.save.pool')
        else:
            action = reverse('save.pool')

        context_attrs = {
            'form_pool': form_pool,
            'form_healthcheck': form_healthcheck,
            'action': action,
            'load_pool_url': load_pool_url,
            'pool_members': server_pool_members,
            'selection_form': DeleteForm(),
            'show_environment': False,
            'is_copy': bool(int(is_copy))
        }

        return render(
            request,
            templates.VIPREQUEST_POOL_FORM,
            context_attrs,
        )

    except NetworkAPIClientError, e:
        logger.error(e)
        return render_message_json(str(e), messages.ERROR)


def shared_load_options_pool(request, client, form_acess=None, external=False):

    try:

        context_attrs = dict()

        environment_vip_id = request.GET.get('environment_vip_id')

        pools = client.create_api_pool().pool_by_environmentvip(environment_vip_id)

        context_attrs['pool_choices'] = pools['server_pools']

        return render(
            request,
            templates.VIPREQUEST_POOL_OPTIONS,
            context_attrs
        )

    except NetworkAPIClientError, e:
        logger.error(e)
        return render_message_json(str(e), messages.ERROR)


def shared_pool_member_items(request, client, form_acess=None, external=False):

    try:

        pool_id = request.GET.get('pool_id')
        pool = client.create_api_pool().get_pool_details(pool_id)
        pool_data = {
            'server_pool': pool['server_pools'][0],
            'external': external
        }

        if external:
            token = form_acess.initial.get("token")
            pool_data.update({'token': token})

        return render(request, templates.POOL_MEMBER_ITEMS, pool_data)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return render_message_json(str(e), messages.ERROR)


def _format_form_error(forms):

    errors = list()

    for form in forms:
        for field, error in form.errors.items():
            errors.append('<b>%s</b>: %s' % (field, ', '.join(error)))

    return errors


def _ipv4(v4):
    ipv4 = dict()
    ipv4["id"] = int(v4.get("ip").get("id"))
    ipv4["ip_formated"] = str(v4.get("ip_formated"))
    return ipv4


def _ipv6(v6):
    ipv6 = dict()
    ipv6["id"] = int(v6.get("ip").get("id"))
    ipv6["ip_formated"] = str(v6.get("ip_formated"))
    return ipv6


def _options(form):
    options = dict()
    options["cache_group"] = int(form.cleaned_data["caches"])
    options["traffic_return"] = int(form.cleaned_data["trafficreturn"])
    options["timeout"] = int(form.cleaned_data["timeout"])
    options["persistence"] = int(form.cleaned_data["persistence"])
    return options


def _vip_dict(form, envvip, options, v4, v6, pools, vip_id):
    vip = {
        "id": int(vip_id) if vip_id else None,
        "name": str(form.cleaned_data["name"]),
        "service": str(form.cleaned_data["service"]),
        "business": str(form.cleaned_data["business"]),
        "environmentvip": int(envvip),
        "ipv4": v4,
        "ipv6": v6,
        "ports": pools,
        "options": options
    }
    return vip


def _get_optionsvip_by_environmentvip(environment_vip, client_api):
    '''
        Return list of optionvip by environmentvip
    '''
    lists = {
        "timeout": list(),
        "caches": list(),
        "persistence": list(),
        "trafficreturn": list(),
        "l4_protocol": list(),
        "l7_protocol": list(),
        "l7_rule": list()
    }
    client_apiovip = client_api.create_api_option_vip()
    optionsvip = client_apiovip.option_vip_by_environment(environment_vip)

    for optionvip in optionsvip:
        if optionvip["option"]["tipo_opcao"] == 'timeout':
            lists['timeout'].append(optionvip["option"])
        if optionvip["option"]["tipo_opcao"] == 'cache':
            lists['caches'].append(optionvip["option"])
        if optionvip["option"]["tipo_opcao"] == 'Persistencia':
            lists['persistence'].append(optionvip["option"])
        if optionvip["option"]["tipo_opcao"] == 'Retorno de trafego':
            lists['trafficreturn'].append(optionvip["option"])
        if optionvip["option"]["tipo_opcao"] == 'l4_protocol':
            lists['l4_protocol'].append(optionvip["option"])
        if optionvip["option"]["tipo_opcao"] == 'l7_protocol':
            lists['l7_protocol'].append(optionvip["option"])
        if optionvip["option"]["tipo_opcao"] == 'l7_rule':
            lists['l7_rule'].append(optionvip["option"])

    return lists


def _valid_form_and_submit(forms_aux, request, lists, client_api, edit=False, vip_id=False):
    '''
        Valid form of vip request(new and edit)
    '''
    # instances
    client_apienv = client_api.create_api_environment_vip()
    client_apipool = client_api.create_api_pool()

    is_valid = True
    is_error = False
    id_vip_created = None

    # Pools - request by POST
    # list of port's ids
    ports_vip_ids = valid_field_table_dynamic(
        request.POST.getlist('ports_vip_ids'))
    # ports
    ports_vip_ports = valid_field_table_dynamic(
        request.POST.getlist('ports_vip_ports'))
    # list of l4 protocols
    ports_vip_l4_protocols = valid_field_table_dynamic(
        request.POST.getlist('ports_vip_l4_protocols'))
    # list of l7 protocols
    ports_vip_l7_protocols = valid_field_table_dynamic(
        request.POST.getlist('ports_vip_l7_protocols'))

    # valid ports and pools
    pool_ids = list()
    ports_vip_pool_id = list()
    ports_vip_l7_rules = list()
    ports_vip_l7_rules_orders = list()
    ports_vip_l7_rules_values = list()

    class GetOutOfLoop(Exception):
        pass
    is_valid_pools = True
    is_valid_ports = True
    try:
        for i, port in enumerate(ports_vip_ports):

            pool_ids.append(valid_field_table_dynamic(
                request.POST.getlist('idsPool_' + port)))
            ports_vip_pool_id.append(valid_field_table_dynamic(
                request.POST.getlist('ports_vip_pool_id_' + port)))
            ports_vip_l7_rules.append(valid_field_table_dynamic(
                request.POST.getlist('ports_vip_l7_rules_' + port)))
            ports_vip_l7_rules_orders.append(valid_field_table_dynamic(
                request.POST.getlist('ports_vip_l7_rules_orders_' + port)))
            ports_vip_l7_rules_values.append(valid_field_table_dynamic(
                request.POST.getlist('ports_vip_l7_rules_values_' + port)))

            for pool in pool_ids[i]:
                lists, is_valid_pool = _validate_pools(lists, pool)
                if not is_valid_pool:
                    is_valid_pools = is_valid_pool
                    raise GetOutOfLoop

        lists, is_valid_port = _valid_ports(lists, ports_vip_ports)
        if not is_valid_port:
            is_valid_ports = is_valid_port
            raise GetOutOfLoop

    except GetOutOfLoop:
        pass

    # Environment - request by POST
    finality = request.POST.get("step_finality")
    client = request.POST.get("step_client")
    environment_vip = request.POST.get("environment_vip")

    # environments - data
    forms_aux['finalities'] = client_apienv.environmentvip_step()
    if finality:
        forms_aux['clients'] = client_apienv.environmentvip_step(finality)
        if client:
            forms_aux['environments'] = client_apienv.environmentvip_step(finality, client)

    # Options - data
    if environment_vip:
        lists_options = _get_optionsvip_by_environmentvip(environment_vip, client_api)
        forms_aux['timeout'] = lists_options['timeout']
        forms_aux['caches'] = lists_options['caches']
        forms_aux['persistence'] = lists_options['persistence']
        forms_aux['trafficreturn'] = lists_options['trafficreturn']
        forms_aux['l4_protocol'] = lists_options['l4_protocol']
        forms_aux['l7_protocol'] = lists_options['l7_protocol']
        forms_aux['l7_rule'] = lists_options['l7_rule']

        forms_aux['pools'] = client_apipool.pool_by_environmentvip(environment_vip)

    default_l7_rule = None
    for opt in lists_options['l7_rule']:
        if opt['nome_opcao_txt'] == 'default_vip':
            default_l7_rule = opt['id']

    # forms with data and request by POST
    form_basic = forms.RequestVipBasicForm(forms_aux, request.POST)
    form_environment = forms.RequestVipEnvironmentVipForm(forms_aux, request.POST)
    form_option = forms.RequestVipOptionVipForm(forms_aux, request.POST)
    form_port_option = forms.RequestVipPortOptionVipForm(forms_aux, request.POST)
    form_ip = forms.RequestVipIPForm(forms_aux, request.POST)

    if form_basic.is_valid() and form_environment.is_valid() and form_option.is_valid() and \
            form_ip.is_valid() and is_valid_ports and is_valid_pools:

        options = _options(form_option)

        name = form_basic.cleaned_data["name"]
        environment_vip = form_environment.cleaned_data["environment_vip"]
        ipv4_check = form_ip.cleaned_data["ipv4_check"]
        ipv6_check = form_ip.cleaned_data["ipv6_check"]

        ipv4 = None
        ipv6 = None

        try:
            if ipv4_check:

                ipv4_type = form_ip.cleaned_data["ipv4_type"]
                ipv4_specific = form_ip.cleaned_data["ipv4_specific"]

                try:
                    if ipv4_type == '0':

                        ips = client_api.create_ip().get_available_ip4_for_vip(
                            environment_vip, name
                        )
                        ipv4 = int(ips.get("ip").get("id"))

                    else:
                        ips = client_api.create_ip().check_vip_ip(
                            ipv4_specific, environment_vip
                        )
                        ipv4 = int(ips.get("ip").get("id"))

                except NetworkAPIClientError, e:
                    is_valid = False
                    is_error = True
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)

            if ipv6_check:

                ipv6_type = form_ip.cleaned_data["ipv6_type"]
                ipv6_specific = form_ip.cleaned_data["ipv6_specific"]

                try:
                    if ipv6_type == '0':
                        ips6 = client_api.create_ip().get_available_ip6_for_vip(
                            environment_vip, name)
                        ipv6 = int(ips6.get("ip").get("id"))

                    else:
                        ips6 = client_api.create_ip().check_vip_ip(
                            ipv6_specific, environment_vip)
                        ipv6 = int(ips6.get("ip").get("id"))
                except NetworkAPIClientError, error:
                    is_valid = False
                    is_error = True
                    logger.error(error)
                    messages.add_message(request, messages.ERROR, error)

            if not is_error:

                pools = list()
                for i, port in enumerate(ports_vip_ports):

                    port_dict = {
                        "id": int(ports_vip_ids[i]) if ports_vip_ids[i] else None,
                        "port": int(port),
                        "options": {
                            "l4_protocol": int(ports_vip_l4_protocols[i]),
                            "l7_protocol": int(ports_vip_l7_protocols[i])
                        },
                        "pools": []
                    }

                    for j, pool in enumerate(pool_ids[i]):

                        pool_dict = {
                            "id": int(ports_vip_pool_id[i][j]) if ports_vip_pool_id[i][j] else None,
                            "server_pool": int(pool_ids[i][j]),
                            "l7_rule": int(ports_vip_l7_rules[i][j]) if ports_vip_l7_rules[i][j] else default_l7_rule,
                            "order": ports_vip_l7_rules_orders[i][j] if ports_vip_l7_rules_orders[i][j] else None,
                            "l7_value": ports_vip_l7_rules_values[i][j] if ports_vip_l7_rules_values[i][j] else None
                        }
                        port_dict['pools'].append(pool_dict)

                    pools.append(port_dict)

                if edit:
                    vip = _vip_dict(form_basic, environment_vip, options, ipv4, ipv6, pools, vip_id)
                    vip = client_api.create_api_vip_request().update_vip_request(vip, vip_id)
                    id_vip_created = vip_id
                else:
                    vip = _vip_dict(form_basic, environment_vip, options, ipv4, ipv6, pools, vip_id)
                    vip = client_api.create_api_vip_request().save_vip_request(vip)
                    id_vip_created = vip[0].get("id")

        except NetworkAPIClientError, error:
            is_valid = False
            is_error = True
            logger.error(error)
            messages.add_message(request, messages.ERROR, error)

        finally:
            try:
                if is_error and ipv4_check and ipv4_type == '0' and ipv4 is not None:
                    client_api.create_ip().delete_ip4(ipv4)

                if is_error and ipv6_check and ipv6_type == '0' and ipv6 is not None:
                    client_api.create_api_network_ipv6().delete_ipv6(ipv6)

            except NetworkAPIClientError, error:
                logger.error(error)
    else:
        is_valid = False

    pools_add = list()
    if pool_ids:
        for index, port in enumerate(ports_vip_ports):
            l4_protocol = [env for env in forms_aux["l4_protocol"]
                           if int(ports_vip_l4_protocols[index]) == int(env["id"])][0]
            l7_protocol = [env for env in forms_aux["l7_protocol"]
                           if int(ports_vip_l7_protocols[index]) == int(env["id"])][0]
            raw_server_pool = {
                "id": ports_vip_ids[index],
                "port": ports_vip_ports[index],
                "options": {
                    "l4_protocol": l4_protocol,
                    "l7_protocol": l7_protocol
                },
                "pools": []
            }

            for index_pool, pool_id in enumerate(pool_ids[index]):
                pool_json = client_api.create_api_pool()\
                    .get_pool_details(pool_id)["server_pools"][0]

                raw_server_pool["pools"].append({
                    "id": int(ports_vip_pool_id[index][index_pool]) if ports_vip_pool_id[index][index_pool] else None,
                    "server_pool": pool_json,
                    "l7_rule": {
                        "id": int(ports_vip_l7_rules[index][index_pool]) if ports_vip_l7_rules[index][index_pool] else default_l7_rule,
                    },
                    "order": ports_vip_l7_rules_orders[index][index_pool] if ports_vip_l7_rules_orders[index][index_pool] else None,
                    "l7_value": ports_vip_l7_rules_values[index][index_pool] if ports_vip_l7_rules_values[index][index_pool] else None
                })

            pools_add.append(raw_server_pool)

    lists['pools_add'] = pools_add
    lists['form_basic'] = form_basic
    lists['form_environment'] = form_environment
    lists['form_option'] = form_option
    lists['form_port_option'] = form_port_option
    lists['form_ip'] = form_ip

    return lists, is_valid, id_vip_created


def _valid_form_and_submit_update(forms_aux, vip, request, lists, client_api, vip_id=False):
    '''
        Valid form of vip request(new and edit)
    '''

    environment_vip = vip.get("environmentvip").get('id')

    # instances
    client_apipool = client_api.create_api_pool()

    is_valid = True
    is_error = False
    id_vip_created = None

    # Pools - request by POST
    # list of port's ids
    ports_vip_ids = valid_field_table_dynamic(
        request.POST.getlist('ports_vip_ids'))
    # ports
    ports_vip_ports = valid_field_table_dynamic(
        request.POST.getlist('ports_vip_ports'))
    # list of l4 protocols
    ports_vip_l4_protocols = valid_field_table_dynamic(
        request.POST.getlist('ports_vip_l4_protocols'))
    # list of l7 protocols
    ports_vip_l7_protocols = valid_field_table_dynamic(
        request.POST.getlist('ports_vip_l7_protocols'))

    # valid ports and pools
    pool_ids = list()
    ports_vip_pool_id = list()
    ports_vip_l7_rules = list()
    ports_vip_l7_rules_orders = list()
    ports_vip_l7_rules_values = list()

    class GetOutOfLoop(Exception):
        pass
    is_valid_pools = True
    is_valid_ports = True
    try:
        for i, port in enumerate(ports_vip_ports):

            pool_ids.append(valid_field_table_dynamic(
                request.POST.getlist('idsPool_' + port)))
            ports_vip_pool_id.append(valid_field_table_dynamic(
                request.POST.getlist('ports_vip_pool_id_' + port)))
            ports_vip_l7_rules.append(valid_field_table_dynamic(
                request.POST.getlist('ports_vip_l7_rules_' + port)))
            ports_vip_l7_rules_orders.append(valid_field_table_dynamic(
                request.POST.getlist('ports_vip_l7_rules_orders_' + port)))
            ports_vip_l7_rules_values.append(valid_field_table_dynamic(
                request.POST.getlist('ports_vip_l7_rules_values_' + port)))

            for pool in pool_ids[i]:
                lists, is_valid_pool = _validate_pools(lists, pool)
                if not is_valid_pool:
                    is_valid_pools = is_valid_pool
                    raise GetOutOfLoop

        lists, is_valid_port = _valid_ports(lists, ports_vip_ports)
        if not is_valid_port:
            is_valid_ports = is_valid_port
            raise GetOutOfLoop

    except GetOutOfLoop:
        pass

    # Options - data
    lists_options = _get_optionsvip_by_environmentvip(environment_vip, client_api)
    forms_aux['timeout'] = lists_options['timeout']
    forms_aux['caches'] = [vip.get('options').get('cache_group')]
    forms_aux['trafficreturn'] = [vip.get('options').get('traffic_return')]
    forms_aux['persistence'] = lists_options['persistence']
    forms_aux['l4_protocol'] = lists_options['l4_protocol']
    forms_aux['l7_protocol'] = lists_options['l7_protocol']
    forms_aux['l7_rule'] = lists_options['l7_rule']

    default_l7_rule = None
    for opt in lists_options['l7_rule']:
        if opt['nome_opcao_txt'] == 'default_vip':
            default_l7_rule = opt['id']

    forms_aux['pools'] = client_apipool.pool_by_environmentvip(environment_vip)

    # forms with data and request by POST
    form_basic = forms.RequestVipBasicForm(forms_aux, request.POST)
    form_option = forms.RequestVipOptionVipEditForm(forms_aux, request.POST)
    form_port_option = forms.RequestVipPortOptionVipForm(forms_aux, request.POST)

    if form_basic.is_valid() and form_option.is_valid() and is_valid_ports and is_valid_pools:

        options = _options(form_option)

        environment_vip = vip.get('environmentvip').get('id')
        ipv4 = vip.get('ipv4').get('id') if vip.get('ipv4') else None
        ipv6 = vip.get('ipv6').get('id') if vip.get('ipv6') else None

        try:

            if not is_error:

                pools = list()
                for i, port in enumerate(ports_vip_ports):

                    port_dict = {
                        "id": int(ports_vip_ids[i]) if ports_vip_ids[i] else None,
                        "port": int(port),
                        "options": {
                            "l4_protocol": int(ports_vip_l4_protocols[i]),
                            "l7_protocol": int(ports_vip_l7_protocols[i])
                        },
                        "pools": []
                    }

                    for j, pool in enumerate(pool_ids[i]):

                        pool_dict = {
                            "id": int(ports_vip_pool_id[i][j]) if ports_vip_pool_id[i][j] else None,
                            "server_pool": int(pool_ids[i][j]),
                            "l7_rule": int(ports_vip_l7_rules[i][j]) if ports_vip_l7_rules[i][j] else default_l7_rule,
                            "order": ports_vip_l7_rules_orders[i][j] if ports_vip_l7_rules_orders[i][j] else None,
                            "l7_value": ports_vip_l7_rules_values[i][j] if ports_vip_l7_rules_values[i][j] else None
                        }
                        port_dict['pools'].append(pool_dict)

                    pools.append(port_dict)

                vip = _vip_dict(form_basic, environment_vip, options, ipv4, ipv6, pools, vip_id)
                vip = client_api.create_api_vip_request().update_vip(vip, vip_id)
                id_vip_created = vip_id

        except NetworkAPIClientError, error:
            is_valid = False
            is_error = True
            logger.error(error)
            messages.add_message(request, messages.ERROR, error)

    else:
        is_valid = False

    pools_add = list()
    if pool_ids:
        for index, port in enumerate(ports_vip_ports):
            l4_protocol = [env for env in forms_aux["l4_protocol"]
                           if int(ports_vip_l4_protocols[index]) == int(env["id"])][0]
            l7_protocol = [env for env in forms_aux["l7_protocol"]
                           if int(ports_vip_l7_protocols[index]) == int(env["id"])][0]
            raw_server_pool = {
                "id": ports_vip_ids[index],
                "port": ports_vip_ports[index],
                "options": {
                    "l4_protocol": l4_protocol,
                    "l7_protocol": l7_protocol
                },
                "pools": []
            }

            for index_pool, pool_id in enumerate(pool_ids[index]):
                pool_json = client_api.create_api_pool()\
                    .get_pool_details(pool_id)["server_pools"][0]

                raw_server_pool["pools"].append({
                    "id": int(ports_vip_pool_id[index][index_pool]) if ports_vip_pool_id[index][index_pool] else None,
                    "server_pool": pool_json,
                    "l7_rule": {
                        "id": int(ports_vip_l7_rules[index][index_pool]) if ports_vip_l7_rules[index][index_pool] else default_l7_rule,
                    },
                    "order": ports_vip_l7_rules_orders[index][index_pool] if ports_vip_l7_rules_orders[index][index_pool] else None,
                    "l7_value": ports_vip_l7_rules_values[index][index_pool] if ports_vip_l7_rules_values[index][index_pool] else None
                })

            pools_add.append(raw_server_pool)

    lists['pools_add'] = pools_add
    lists['form_basic'] = form_basic
    lists['form_option'] = form_option
    lists['form_port_option'] = form_port_option

    return lists, is_valid, id_vip_created


def _create_options_environment(client, env_vip_id):
    '''
        Return list of environments by environment vip
    '''
    choices_environment = [('', '-')]

    environments = client.create_api_vip_request()\
        .list_environment_by_environmet_vip(env_vip_id)

    for env in environments:
        choices_environment.append(
            (env['id'], env['name'])
        )

    return choices_environment


def shared_save_pool(request, client, form_acess=None, external=False):

    try:

        env_vip_id = request.POST.get('environment_vip')

        # Get Data From Request Post To Save
        pool_id = request.POST.get('id')
        environment_id = request.POST.get('environment')

        members = dict()
        members["id_pool_member"] = request.POST.getlist('id_pool_member')
        members["id_equips"] = request.POST.getlist('id_equip')
        members["name_equips"] = request.POST.getlist('equip')
        members["priorities"] = request.POST.getlist('priority')
        members["ports_reals"] = request.POST.getlist('ports_real_reals')
        members["weight"] = request.POST.getlist('weight')
        members["id_ips"] = request.POST.getlist('id_ip')
        members["ips"] = request.POST.getlist('ip')
        members["environment"] = environment_id

        environment_choices = _create_options_environment(client, env_vip_id)
        lb_method_choices = facade_pool.populate_optionsvips_choices(client)
        servicedownaction_choices = facade_pool.populate_servicedownaction_choices(client)
        healthcheck_choices = facade_pool.populate_healthcheck_choices(client)

        form_pool = forms.PoolForm(
            environment_choices,
            lb_method_choices,
            servicedownaction_choices,
            request.POST
        )

        form_healthcheck = forms.PoolHealthcheckForm(
            healthcheck_choices,
            request.POST
        )

        if form_pool.is_valid() and form_healthcheck.is_valid():

            param_dic = {}

            pool = dict()
            pool["id"] = pool_id

            servicedownaction = facade_pool.format_servicedownaction(client, form_pool)
            healthcheck = facade_pool.format_healthcheck(request)

            pool["identifier"] = str(form_pool.cleaned_data['identifier'])
            pool["default_port"] = int(form_pool.cleaned_data['default_port'])
            pool["environment"] = int(form_pool.cleaned_data['environment'])
            pool["servicedownaction"] = servicedownaction
            pool["lb_method"] = str(form_pool.cleaned_data['balancing'])
            pool["healthcheck"] = healthcheck
            pool["default_limit"] = int(form_pool.cleaned_data['maxcon'])
            server_pool_members = facade_pool.format_server_pool_members(request, pool["default_limit"])
            pool["server_pool_members"] = server_pool_members

            client.create_pool().save_pool(pool)
            if pool_id:
                param_dic['message'] = pool_messages.get('success_update')
            else:
                param_dic['message'] = pool_messages.get('success_insert')

            return HttpResponse(json.dumps(param_dic), content_type="application/json")

        errors = form_pool.errors + form_healthcheck.errors

        return render_message_json('<br>'.join(errors), messages.ERROR)

    except Exception, e:
        logger.error(e)
        return render_message_json(str(e), messages.ERROR)


def add_form_shared(request, client_api, form_acess="", external=False):
    """
    Method to render form request vip
    """

    try:
        lists = dict()

        lists["action"] = reverse('vip-request.form')
        lists['ports'] = ''
        lists['ports_error'] = ''
        lists['reals_error'] = ''
        lists['form_acess'] = form_acess
        lists['external'] = external

        if external:
            lists['token'] = form_acess.initial.get("token")

        finality_list = client_api.create_api_environment_vip().environmentvip_step()

        forms_aux = dict()
        forms_aux['finalities'] = finality_list
        forms_aux['pools'] = list()

        if request.method == "POST":

            lists, is_valid, id_vip = _valid_form_and_submit(
                forms_aux,
                request,
                lists,
                client_api
            )

            if is_valid:

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    request_vip_messages.get("success_insert")
                )

                if external:
                    return HttpResponseRedirect(
                        "%s?token=%s" % (
                            reverse('vip-request.edit.external',
                                    args=[id_vip]),
                            form_acess.initial.get("token")
                        )
                    )
                else:
                    return redirect('vip-request.list')

        else:

            lists['form_basic'] = forms.RequestVipBasicForm(forms_aux)
            lists['form_environment'] = forms.RequestVipEnvironmentVipForm(forms_aux)
            lists['form_option'] = forms.RequestVipOptionVipForm(forms_aux)
            lists['form_port_option'] = forms.RequestVipPortOptionVipForm(forms_aux)
            lists['form_ip'] = forms.RequestVipIPForm(forms_aux)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    template = templates.VIPREQUEST_FORM_EXTERNAL if external else templates.VIPREQUEST_FORM

    return render_to_response(
        template,
        lists,
        context_instance=RequestContext(request)
    )


def edit_form_shared(request, id_vip, client_api, form_acess="", external=False):
    """
    Method to render form request vip
    """

    try:
        lists = dict()

        lists['id_vip'] = id_vip
        lists["action"] = reverse('vip-request.edit', args=[id_vip])
        lists['ports'] = ''
        lists['ports_error'] = ''
        lists['form_acess'] = form_acess
        lists['external'] = external

        if external:
            lists['token'] = form_acess.initial.get("token")

        vip = client_api.create_api_vip_request().get_vip_request_details(id_vip)['vips'][0]

        if vip.get('created') is True:
            return redirect(reverse('vip-request.tab.edit', args=[id_vip]))

        finality_list = client_api.create_api_environment_vip().environmentvip_step()

        forms_aux = dict()
        forms_aux['finalities'] = finality_list
        forms_aux['pools'] = list()

        if request.method == "POST":

            lists, is_valid, id_vip = _valid_form_and_submit(
                forms_aux,
                request,
                lists,
                client_api,
                True,
                id_vip
            )

            if is_valid:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    request_vip_messages.get("success_edit")
                )

                if external:

                    return HttpResponseRedirect(
                        "%s?token=%s" % (
                            reverse('vip-request.edit.external', args=[id_vip]),
                            form_acess.initial.get("token")
                        )
                    )
                else:
                    return redirect('vip-request.list')

        else:

            for opt in vip.get("options"):
                val = vip.get("options").get(opt).get('id') if vip.get("options").get(opt) else None
                if opt == 'timeout':
                    timeout = val
                elif opt == 'cache_group':
                    caches = val
                elif opt == 'persistence':
                    persistence = val
                elif opt == 'traffic_return':
                    trafficreturn = val

            if vip.get("ipv4"):
                ipv4_check = True
                ipv4_type = '1'
                ipv4_specific = vip.get("ipv4").get("ip_formated")
            else:
                ipv4_check = False
                ipv4_type = ''
                ipv4_specific = ''

            if vip.get("ipv6"):
                ipv6_check = True
                ipv6_type = '1'
                ipv6_specific = vip.get("ipv6").get("ip_formated")
            else:
                ipv6_check = False
                ipv6_type = ''
                ipv6_specific = ''

            client_apipool = client_api.create_api_pool()
            client_apienv = client_api.create_api_environment_vip()

            environment_vip = vip.get("environmentvip").get('id')

            finality = vip.get("environmentvip").get('finalidade_txt')
            client = vip.get("environmentvip").get('cliente_txt')
            environment = vip.get("environmentvip").get('ambiente_p44_txt')

            forms_aux['finalities'] = client_apienv.environmentvip_step()
            if finality:
                forms_aux['clients'] = client_apienv.environmentvip_step(finality)
                if client:
                    forms_aux['environments'] = client_apienv.environmentvip_step(finality, client)

            options_list = _get_optionsvip_by_environmentvip(environment_vip, client_api)
            forms_aux['timeout'] = options_list['timeout']
            forms_aux['caches'] = options_list['caches']
            forms_aux['persistence'] = options_list['persistence']
            forms_aux['trafficreturn'] = options_list['trafficreturn']
            forms_aux['l4_protocol'] = options_list['l4_protocol']
            forms_aux['l7_protocol'] = options_list['l7_protocol']
            forms_aux['l7_rule'] = options_list['l7_rule']

            forms_aux['pools'] = client_apipool.pool_by_environmentvip(environment_vip)

            lists['form_basic'] = forms.RequestVipBasicForm(
                forms_aux,
                initial={
                    "business": vip.get("business"),
                    "service": vip.get("service"),
                    "name": vip.get("name"),
                    "created": vip.get("created")
                }
            )

            lists['form_environment'] = forms.RequestVipEnvironmentVipForm(
                forms_aux,
                initial={
                    "step_finality": finality,
                    "step_client": client,
                    "step_environment": environment,
                    "environment_vip": environment_vip
                }
            )

            lists['form_option'] = forms.RequestVipOptionVipForm(
                forms_aux,
                initial={
                    "timeout": timeout,
                    "caches": caches,
                    "persistence": persistence,
                    "trafficreturn": trafficreturn,
                }
            )

            lists['form_port_option'] = forms.RequestVipPortOptionVipForm(forms_aux)

            # for port in vip.get("ports"):
            #     for pool in port.get('pools'):
            #         pool.get('server_pool')
            #         pl = dict()
            #         pl["server_pool"] =  pool.get('server_pool')
            # #         pl["server_pool"]["port_vip"] = pool['port']

            pools_add = vip.get("ports")
            # for pool in vip.get("pool"):
            #     pool["server_pool"]["port_vip"] = pool['port']
            #     pool["server_pool"]["port_vip_id"] = pool['id']
            #     pools_add.append(pool)

            lists['pools_add'] = pools_add

            lists['form_ip'] = forms.RequestVipIPForm(
                forms_aux,
                initial={
                    "ipv4_check": ipv4_check,
                    "ipv4_type": ipv4_type,
                    "ipv4_specific": ipv4_specific,
                    "ipv6_check": ipv6_check,
                    "ipv6_type": ipv6_type,
                    "ipv6_specific": ipv6_specific
                }
            )

    except VipNaoExisteError, e:
        logger.error(e)
        messages.add_message(
            request, messages.ERROR, request_vip_messages.get("invalid_vip"))
        return redirect('vip-request.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    template = templates.VIPREQUEST_EDIT_EXTERNAL if external else templates.VIPREQUEST_FORM

    return render_to_response(template, lists, context_instance=RequestContext(request))


def popular_environment_shared(request, client_api):
    """
    Method to return environment vip list by finality and client
    Param: finality
    Param: client
    """

    lists = dict()
    status_code = None
    lists['environments'] = ''

    try:

        finality = get_param_in_request(request, 'finality')
        if finality is None:
            raise InvalidParameterError(
                "Parâmetro inválido: O campo finalidade inválido ou não foi informado.")

        client = get_param_in_request(request, 'client')
        if client is None:
            raise InvalidParameterError(
                "Parâmetro inválido: O campo cliente inválido ou não foi informado.")

        client_evip = client_api.create_api_environment_vip()

        lists['environments'] = client_evip.environmentvip_step(finality, client)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500

    # Returns HTML
    return HttpResponse(
        loader.render_to_string(
            templates.AJAX_VIPREQUEST_ENVIRONMENT,
            lists,
            context_instance=RequestContext(request)
        ),
        status=status_code
    )


def popular_options_shared(request, client_api):
    """
    Method to return options vip list by environment vip
    Param: environment_vip
    Param: id_vip
    """

    lists = dict()
    status_code = None

    try:
        environment_vip = get_param_in_request(request, 'environment_vip')
        if environment_vip is None:
            raise InvalidParameterError(
                "Parâmetro inválido: O campo Ambiente Vip inválido ou não foi informado.")

        lists = _get_optionsvip_by_environmentvip(environment_vip, client_api)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500

    # Returns Json
    try:
        return HttpResponse(
            loader.render_to_string(
                templates.AJAX_VIPREQUEST_OPTIONS,
                lists,
                context_instance=RequestContext(request)
            ),
            status=status_code
        )
    except Exception, e:
        print e


def shared_load_new_pool(request, client, form_acess=None, external=False):
    """
    Method to return options pool list by environment
    Param: request.GET.get('env_vip_id')
    """

    try:

        pool_members = list()

        env_vip_id = request.GET.get('env_vip_id')

        action = reverse('external.save.pool') if external else reverse('save.pool')
        load_pool_url = reverse('pool.modal.ips.ajax.external') if external else reverse('pool.modal.ips.ajax')

        environment_choices = _create_options_environment(client, env_vip_id)
        lb_method_choices = facade_pool.populate_optionsvips_choices(client)
        servicedownaction_choices = facade_pool.populate_servicedownaction_choices(client)
        healthcheck_choices = facade_pool.populate_healthcheck_choices(client)

        lists = dict()
        lists["form_pool"] = forms.PoolForm(environment_choices, lb_method_choices,
                                            servicedownaction_choices)
        lists["form_healthcheck"] = forms.PoolHealthcheckForm(healthcheck_choices)
        lists["action"] = action
        lists["load_pool_url"] = load_pool_url
        lists["pool_members"] = pool_members
        lists["show_environment"] = True
        return render(
            request,
            templates.VIPREQUEST_POOL_FORM,
            lists
        )

    except NetworkAPIClientError, e:
        logger.error(e)
        return render_message_json(str(e), messages.ERROR)
