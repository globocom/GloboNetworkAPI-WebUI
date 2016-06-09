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

import base64
import hashlib
import json
import logging
import re
from time import strftime

from CadVlan import templates
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.forms import CreateForm, DeleteForm, RemoveForm, ValidateForm
from CadVlan.Ldap.model import Ldap, LDAPNotFoundError
from CadVlan.messages import auth_messages, equip_group_messages, error_messages, \
    pool_messages, request_vip_messages
from CadVlan.permissions import POOL_ALTER_SCRIPT, POOL_CREATE_SCRIPT, POOL_MANAGEMENT, POOL_REMOVE_SCRIPT, \
    VIP_ALTER_SCRIPT, VIP_CREATE_SCRIPT, VIP_REMOVE_SCRIPT, VIPS_REQUEST
from CadVlan.Pool import facade as facade_pool
from CadVlan.settings import ACCESS_EXTERNAL_TTL, NETWORK_API_PASSWORD, NETWORK_API_URL, NETWORK_API_USERNAME
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.Decorators import has_perm, has_perm_external, log, login_required
from CadVlan.Util.shortcuts import render_message_json
from CadVlan.Util.utility import clone, DataTablePaginator, get_param_in_request, IP_VERSION, \
    is_valid_int_param, safe_list_get, validates_dict
from CadVlan.VipRequest import forms
from CadVlan.VipRequest.encryption import Encryption

from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import redirect, render, render_to_response
from django.template import loader
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from networkapiclient.ClientFactory import ClientFactory
from networkapiclient.exception import EnvironmentVipError, EnvironmentVipNotFoundError, EquipamentoNaoExisteError, \
    InvalidBalMethodValueError, InvalidCacheValueError, InvalidParameterError, InvalidPersistenceValueError, \
    InvalidPriorityValueError, InvalidTimeoutValueError, IpEquipmentError, IpError, IpNaoExisteError, \
    IpNotFoundByEquipAndVipError, NetworkAPIClientError, RealParameterValueError, RealServerPortError, \
    RealServerPriorityError, RealServerScriptError, RealServerWeightError, ScriptError, UserNotAuthenticatedError, \
    VipAllreadyCreateError, VipError, VipNaoExisteError
from networkapiclient.Pagination import Pagination


logger = logging.getLogger(__name__)


OPERATION = {0: 'DELETE', 1: 'VALIDATE', 2: 'CREATE', 3: 'REMOVE'}


vip_all_permission = {"permission": VIPS_REQUEST, "read": True, "write": True}
pool_all_permission = {"permission": POOL_MANAGEMENT, "read": True, "write": True}
pool_read_permission = {"permission": POOL_MANAGEMENT, "read": True}


@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "read": True}, ])
def search_list(request):
    try:

        lists = dict()
        lists["delete_form"] = DeleteForm()
        lists["validate_form"] = ValidateForm()
        lists["create_form"] = CreateForm()
        lists["remove_form"] = RemoveForm()
        lists["search_form"] = forms.SearchVipRequestForm()
        lists['modal'] = 'false'

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(
        templates.VIPREQUEST_SEARCH_LIST,
        lists,
        context_instance=RequestContext(request)
    )


@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "read": True}, ])
def ajax_view_vip(request, id_vip):
    lists = dict()
    return ajax_shared_view_vip(request, id_vip, lists)


@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "read": True}, ])
def delete_validate_create_remove(request, operation):

    operation_text = OPERATION.get(int(operation))

    if request.method == 'POST':

        form = DeleteForm(request.POST) if operation_text == 'DELETE' else ValidateForm(
            request.POST) if operation_text == 'VALIDATE' else CreateForm(request.POST) if operation_text == 'CREATE' else RemoveForm(request.POST)
        id = 'ids' if operation_text == 'DELETE' else 'ids_val' if operation_text == 'VALIDATE' else 'ids_create' if operation_text == 'CREATE' else 'ids_remove'

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_vip = auth.get_clientFactory().create_vip()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data[id])

            # All messages to display
            error_list = list()
            error_list_created = list()
            error_list_not_validate = list()

            # Control others exceptions
            have_errors = False

            # FLAG only for  ERROR  in create
            all_ready_msg_script_error = False

            # For each script selected to remove
            for id_vip in ids:
                try:

                    if operation_text == 'DELETE':
                        # Execute in NetworkAPI
                        # criar remover
                        client_vip.remover(id_vip)

                    elif operation_text == 'CREATE':

                        client_vip.criar(id_vip)

                    elif operation_text == 'VALIDATE':
                        # criar validar
                        client_vip.validate(id_vip)

                    elif operation_text == 'REMOVE':
                        # remover
                        client_vip.remove_script(id_vip)

                except VipAllreadyCreateError, e:
                    logger.error(e)
                    error_list_created.append(id_vip)
                except VipError, e:
                    logger.error(e)
                    error_list_not_validate.append(id_vip)
                except ScriptError, e:
                    logger.error(e)
                    if not all_ready_msg_script_error:
                        messages.add_message(request, messages.ERROR, e)
                    all_ready_msg_script_error = True
                    error_list.append(id_vip)
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    error_list.append(id_vip)

            msg_error_call, msg_sucess_call, msg_some_error_call = get_error_mesages(
                operation_text)

            if len(error_list_not_validate) > 0:

                msg = ""
                for id_error in error_list_not_validate:
                    msg = msg + id_error + ','

                if operation_text == 'REMOVE':
                    msg = request_vip_messages.get('not_created') % msg[:-1]
                else:
                    msg = request_vip_messages.get(
                        'validate_before') % msg[:-1]
                messages.add_message(request, messages.WARNING, msg)
                have_errors = True

            if len(error_list_created) > 0:

                msg = ""
                for id_error in error_list_created:
                    msg = msg + id_error + ','

                msg = request_vip_messages.get('all_ready_create') % msg[:-1]
                messages.add_message(request, messages.WARNING, msg)
                have_errors = True

            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(
                    request, messages.ERROR, request_vip_messages.get(msg_error_call))

            # If cant remove someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = request_vip_messages.get(msg_some_error_call) % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all has ben removed
            elif have_errors is False:
                messages.add_message(
                    request, messages.SUCCESS, request_vip_messages.get(msg_sucess_call))

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('vip-request.list')


@log
@login_required
@has_perm([{"permission": VIP_CREATE_SCRIPT, "write": True}])
def create_vip(request):
    delete_validate_create_remove_2(request, 2)
    # Redirect to list_all action
    return redirect('vip-request.list')


@log
@login_required
@has_perm([{"permission": VIP_REMOVE_SCRIPT, "write": True}])
def remove_vip(request):
    delete_validate_create_remove_2(request, 3)
    # Redirect to list_all action
    return redirect('vip-request.list')


@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "write": True}])
def delete_vip(request):
    delete_validate_create_remove_2(request, 0)
    # Redirect to list_all action
    return redirect('vip-request.list')


@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "read": True}, {"permission": VIPS_REQUEST, "write": True}])
def ajax_validate_create_remove(request, id_vip, operation):

    operation_text = OPERATION.get(int(operation))

    # Get user
    auth = AuthSession(request.session)
    client_vip = auth.get_clientFactory().create_vip()

    msg = ""
    msg_type = ""
    changed = ""
    msg_error_call, msg_success_call = get_error_messages_one(operation_text)

    # This method has a generic permission VIPS_REQUEST, but each of the
    # operations has its own permission.

    try:

        if operation_text == 'CREATE':
            client_vip.criar(id_vip)

        elif operation_text == 'VALIDATE':
            client_vip.validate(id_vip)

        elif operation_text == 'REMOVE':
            client_vip.remove_script(id_vip)

    except VipAllreadyCreateError, e:
        logger.error(e)
        msg = request_vip_messages.get('all_ready_create_one')
    except VipError, e:
        logger.error(e)
        msg = request_vip_messages.get('validate_before_one')
    except ScriptError, e:
        logger.error(e)
        msg = request_vip_messages.get(msg_error_call)
    except NetworkAPIClientError, e:
        logger.error(e)
        msg = request_vip_messages.get(msg_error_call)
    except Exception, e:
        logger.error(e)
        msg = e

    if (msg):
        msg_type = 'error'
    else:
        msg = request_vip_messages.get(msg_success_call)
        msg_type = 'success'
        changed = True

    # Return the shared view method with messages
    lists = dict()
    lists['message'] = msg
    lists['msg_type'] = msg_type
    if (changed):
        lists['changed'] = changed

    return ajax_shared_view_vip(request, id_vip, lists)


def get_error_mesages(operation_text):

    msg_erro = ""
    msg_sucesso = ""
    msg_erro_parcial = ""

    if operation_text == 'DELETE':

        msg_erro = 'can_not_remove_all'
        msg_sucesso = 'success_remove'
        msg_erro_parcial = 'can_not_remove'

    elif operation_text == 'VALIDATE':

        msg_erro = 'can_not_validate_all'
        msg_sucesso = 'success_validate'
        msg_erro_parcial = 'can_not_validate'

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

    if operation_text == 'VALIDATE':
        msg_erro = 'can_not_validate_one'
        msg_sucesso = 'success_validate_one'
    elif operation_text == 'CREATE':
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


def _validate_pools(lists, pools):

    is_valid = True

    if not pools:
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


def valid_realthcheck(healthcheck_type):

    lists = list()
    is_valid = True

    if not healthcheck_type:
        lists.append(request_vip_messages.get("required_healthcheck"))
        is_valid = False

    return is_valid, lists


def valid_reals(id_equips, ports, priorities, id_ips, default_port):

    lists = list()
    is_valid = True

    try:
        if int(default_port) > 65535:
            lists.append(request_vip_messages.get("invalid_port"))
            is_valid = False

        if id_equips is not None and id_ips is not None:

            invalid_ports_real = [
                i for i in ports if int(i) > 65535 or int(i) < 1]
            invalid_priority = [
                i for i in priorities if int(i) > 4294967295 or int(i) < 0]

            if invalid_priority:
                lists.append(request_vip_messages.get("invalid_priority"))
                is_valid = False

            if invalid_ports_real:
                lists.append(request_vip_messages.get("invalid_port"))
                is_valid = False

            if len(id_equips) != len(id_ips):
                lists.append(pool_messages.get("error_port_missing"))
                is_valid = False

            invalid_ips = 0

            for i in range(0, len(id_ips)):
                for j in range(0, len(id_ips)):
                    if i == j:
                        pass
                    elif ports[i] == ports[j] and id_ips[i] == id_ips[j]:
                        invalid_ips += 1

            if invalid_ips > 0:
                lists.append(pool_messages.get('error_same_port'))
                is_valid = False

    except Exception, e:
        logger.error(e)
        lists.append(request_vip_messages.get("invalid_port"))
        is_valid = False

    return is_valid, lists


def ports_(ports_vip, ports_real):

    ports = []
    if ports_vip is not None and ports_real is not None:
        for i in range(0, len(ports_vip)):
            ports.append("%s:%s" % (ports_vip[i], ports_real[i]))

    return ports


def mount_table_ports_vip(lists, ports_vip, vip_port_ids=[]):

    if ports_vip is not None and ports_vip != '':

        ports = []
        for i in range(0, len(ports_vip)):

            if ports_vip[i] != '':
                port_raw = dict()
                port_raw['ports_vip'] = ports_vip[i]
                if vip_port_ids:
                    port_raw["vip_port_id"] = safe_list_get(vip_port_ids, i)
                ports.append(port_raw)

        lists['ports'] = ports

    return lists


def mount_table_ports(lists, ports_vip, ports_real):

    if ports_vip is not None and ports_vip != '':

        ports = []
        for i in range(0, len(ports_vip)):

            if ports_real[i] != '' and ports_vip[i] != '':
                ports.append(
                    {'ports_real': ports_real[i], 'ports_vip': ports_vip[i]})

        lists['ports'] = ports

    return lists


def mount_table_reals(lists, id_equip, id_ip, weight, priority, equip, ip, ports_vip_reals, ports_real_reals, version=None, status=None):

    if id_equip is not None and id_equip != '':

        reals = []
        for i in range(0, len(id_equip)):

            if id_equip[i] != '' and id_ip[i] != '':

                if not ports_real_reals and not ports_vip_reals:
                    if weight:
                        reals.append({'priority': priority[i], 'weight': weight[i], 'id_equip': id_equip[
                                     i], 'equip': equip[i], 'id_ip': id_ip[i], 'ip': ip[i]})
                    else:
                        reals.append({'priority': priority[i], 'weight': '', 'id_equip': id_equip[
                                     i], 'equip': equip[i], 'id_ip': id_ip[i], 'ip': ip[i]})
                else:
                    if weight and priority:
                        reals.append({'priority': priority[i], 'weight': weight[i], 'id_equip': id_equip[i], 'equip': equip[
                                     i], 'id_ip': id_ip[i], 'ip': ip[i], 'ports_vip': ports_vip_reals[i], 'ports_real': ports_real_reals[i]})

                    else:
                        if not weight and not priority:
                            reals.append({'priority': '', 'weight': '', 'id_equip': id_equip[i], 'equip': equip[i], 'id_ip': id_ip[
                                         i], 'ip': ip[i], 'ports_vip': ports_vip_reals[i], 'ports_real': ports_real_reals[i]})

                        elif not weight:
                            reals.append({'priority': priority[i], 'weight': '', 'id_equip': id_equip[i], 'equip': equip[
                                         i], 'id_ip': id_ip[i], 'ip': ip[i], 'ports_vip': ports_vip_reals[i], 'ports_real': ports_real_reals[i]})
                        else:
                            reals.append({'priority': '', 'weight': weight[i], 'id_equip': id_equip[i], 'equip': equip[
                                         i], 'id_ip': id_ip[i], 'ip': ip[i], 'ports_vip': ports_vip_reals[i], 'ports_real': ports_real_reals[i]})

        if status is not None and status != []:
            for i in range(0, len(reals)):
                reals[i]['status'] = status[i]

        if version is not None and version != []:
            for i in range(0, len(reals)):
                reals[i]['version'] = version[i]

        lists['reals'] = reals

    return lists


def reals_(id_equip, id_ip, equip, ip, ports_vip_reals, ports_real_reals):

    reals = []

    if id_equip is not None and id_ip is not None:

        reals = []
        for i in range(0, len(id_equip)):
            reals.append({"real_name": equip[i], "real_ip": ip[i], "port_vip": ports_vip_reals[
                         i], "id_ip": id_ip[i], "port_real": ports_real_reals[i]})

    return reals


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_client_external(request, form_acess, client):
    return popular_client_shared(request, client)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_client(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return popular_client_shared(request, client_api)


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_rule_external(request, form_acess, client):
    return popular_rule_shared(request, client)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_rule(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return popular_rule_shared(request, client_api)


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_model_ip_real_server_external(request, form_acess, client):
    return model_ip_real_server_shared(request, client)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_model_ip_real_server(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return model_ip_real_server_shared(request, client_api)


def parse_real_server(request, vip, client_api, id_vip, id_evip, is_status=False, valid=True):
    reals = []
    if "reals" in vip:
        reals = validates_dict(vip['reals'], 'real')

    prioritys = []
    if "reals_prioritys" in vip:
        prioritys = validates_dict(vip['reals_prioritys'], 'reals_priority')

    weights = []
    if "reals_weights" in vip:
        weights = validates_dict(vip['reals_weights'], 'reals_weight')

    id_equip = []
    id_ip = []
    weight = []
    priority = []
    equip = []
    ip = []
    status = []
    version = []
    for i in range(0, len(reals)):

        real = None

        try:

            real_name = reals[i].get("real_name")
            real_ip = reals[i].get("real_ip")

            real = client_api.create_vip().valid_real_server(
                real_ip, real_name, id_evip, valid).get("real")

            equip_aux = real.get("equipment")
            ip_aux = real.get("ip")

            equip.append(equip_aux.get("nome"))
            id_equip.append(equip_aux.get("id"))

            id_ip.append(ip_aux.get("id"))
            ip.append(real_ip)

            if is_status:

                version.append(ip_aux.get("version"))

                try:
                    port_vip = None
                    port_real = None
                    if 'port_vip' in reals[i] and 'port_real' in reals[i]:
                        port_vip = reals[i].get("port_vip")
                        port_real = reals[i].get("port_real")

                    if ip_aux.get("version") == IP_VERSION.IPv4[1]:
                        code = client_api.create_vip().checar_real(
                            id_vip, ip_aux.get("id"), equip_aux.get("id"), port_vip, port_real)
                    else:
                        code = client_api.create_vip().check_real_ipv6(
                            id_vip, ip_aux.get("id"), equip_aux.get("id"), port_vip, port_real)

                    if code is not None and 'sucesso' in code:

                        code = int(
                            code.get('sucesso').get('descricao').get('stdout'))

                        if 2 == code:  # Disable
                            status.append(0)

                        elif 3 == code:  # Enable
                            status.append(1)

                        else:
                            status.append(0)

                    else:
                        status.append(0)

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    status.append(0)

            if prioritys:
                priority.append(prioritys[i])

            if weights:
                weight.append(weights[i])

        except (EquipamentoNaoExisteError, IpNaoExisteError, IpNotFoundByEquipAndVipError), e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, request_vip_messages.get(
                "error_existing_reals") % (real_name, real_ip))

        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)

    return id_equip, id_ip, weight, priority, equip, ip, status, version


@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "read": True}, ])
def tab_real_server_status(request, id_vip):

    try:

        lists = dict()
        lists['idt'] = id_vip
        lists['status_form'] = DeleteForm()

        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()

        vip = client_api.create_vip().get_by_id(id_vip).get("vip")
        vip['equipamento'] = validates_dict(vip, 'equipamento')
        vip['environments'] = validates_dict(vip, 'environments')
        vip['balancing'] = str(vip.get("metodo_bal")).upper()
        lists['vip'] = vip

        finality = vip.get("finalidade")
        client = vip.get("cliente")
        environment = vip.get("ambiente")

        id_evip = client_api.create_environment_vip().search(
            None, finality, client, environment).get("environment_vip").get("id")

        id_equip, id_ip, weight, priority, equip, ip, status, version = parse_real_server(
            request, vip, client_api, id_vip, id_evip, True)

        port_vip_list = list()
        port_real_list = list()

        if 'reals' in vip:
            reals_list = vip['reals'].get('real')
            if type(reals_list) is not list:
                port_vip_list.append(reals_list['port_vip'])
                port_real_list.append(reals_list['port_real'])
            else:
                for real_l in reals_list:
                    port_vip_list.append(real_l['port_vip'])
                    port_real_list.append(real_l['port_real'])

        lists = mount_table_reals(
            lists, id_equip, id_ip, weight, priority, equip, ip, port_vip_list, port_real_list, version, status)

    except EnvironmentVipNotFoundError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, request_vip_messages.get(
            "error_existing_environment_vip") % (finality, client, environment))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(
        templates.VIPREQUEST_TAB_REAL_SERVER_STATUS,
        lists,
        context_instance=RequestContext(request)
    )


@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "read": True}, ])
def tab_pools(request, id_vip):

    lists = dict()
    lists['idt'] = id_vip
    lists['status_form'] = DeleteForm()

    try:
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()

        lists['vip'] = vip = client_api.create_api_vip_request().get_vip_request_details(id_vip)['vips'][0]

        finality = vip["environmentvip"]["finalidade_txt"]
        client = vip["environmentvip"]["cliente_txt"]
        environment = vip["environmentvip"]["ambiente_p44_txt"]

    except EnvironmentVipNotFoundError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, request_vip_messages.get(
            "error_existing_environment_vip") % (finality, client, environment))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(
        templates.VIPREQUEST_TAB_POOLS,
        lists,
        context_instance=RequestContext(request)
    )


@log
@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "read": True}])
def pool_datatable(request, id_vip):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        column_index_name_map = {
            0: 'identifier',
            1: 'default_port',
            2: 'healthcheck__healthcheck_type',
            3: 'environment',
            4: 'pool_created',
            5: ''
        }

        dtp = DataTablePaginator(request, column_index_name_map)

        dtp.build_server_side_list()

        dtp.searchable_columns = [
            'identifier',
            'default_port',
            'pool_created',
            'healthcheck__healthcheck_type',
        ]

        pagination = Pagination(
            dtp.start_record,
            dtp.end_record,
            dtp.asorting_cols,
            dtp.searchable_columns,
            dtp.custom_search
        )

        pools = client.create_pool().list_all_by_reqvip(id_vip, pagination)

        return dtp.build_response(
            pools["pools"],
            pools["total"],
            templates.VIPREQUEST_POOL_DATATABLE,
            request
        )

    except NetworkAPIClientError, e:
        logger.error(e.error)
        return render_message_json(e.error, messages.ERROR)


@log
@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "read": True}, ])
def tab_real_server(request, id_vip):

    try:
        lists = dict()
        lists['idt'] = id_vip
        html = ''

        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()

        vip = client_api.create_vip().get_by_id(id_vip).get("vip")
        vip['equipamento'] = validates_dict(vip, 'equipamento')
        vip['environments'] = validates_dict(vip, 'environments')
        vip['balancing'] = str(vip.get("metodo_bal")).upper()
        lists['vip'] = vip

        finality = vip.get("finalidade")
        client = vip.get("cliente")
        environment = vip.get("ambiente")

        try:
            environment_vip = client_api.create_environment_vip().search(
                None, finality, client, environment).get("environment_vip").get("id")
            lists['environment_vip'] = environment_vip
        except Exception, e:
            environment_vip = None
            messages.add_message(request, messages.ERROR, request_vip_messages.get(
                "error_existing_environment_vip") % (finality, client, environment))

        maxcon = vip.get("maxcon")

        balancing = vip.get("metodo_bal")
        lists['balancing'] = balancing

        form_real = forms.RequestVipFormReal(initial={"maxcon": maxcon})
        lists['form_real'] = form_real

        parse = True

        # Already edited
        if request.method == "POST":
            try:

                alter_priority = request.POST.getlist('alter_priority')

                # Real - data TABLE REALS
                ports_vip_reals = valid_field_table_dynamic(request.POST.getlist(
                    'ports_vip_reals')) if "ports_vip_reals" in request.POST else None
                ports_real_reals = valid_field_table_dynamic(request.POST.getlist(
                    'ports_real_reals')) if "ports_real_reals" in request.POST else None

                priority = valid_field_table_dynamic(
                    request.POST.getlist('priority')) if "priority" in request.POST else None
                weight = valid_field_table_dynamic(
                    request.POST.getlist('weight')) if "weight" in request.POST else None
                id_equip = valid_field_table_dynamic(
                    request.POST.getlist('id_equip')) if "id_equip" in request.POST else None
                equip = valid_field_table_dynamic(
                    request.POST.getlist('equip')) if "equip" in request.POST else None
                id_ip = valid_field_table_dynamic(
                    request.POST.getlist('id_ip')) if "id_ip" in request.POST else None
                ip = valid_field_table_dynamic(
                    request.POST.getlist('ip')) if "ip" in request.POST else None

                lists, is_valid_reals = valid_reals(
                    lists, balancing, id_equip, id_ip, weight, priority, ports_vip_reals, ports_real_reals)

                if is_valid_reals:
                    reals = reals_(
                        id_equip, id_ip, equip, ip, ports_vip_reals, ports_real_reals)
                    client_api.create_vip().edit_reals(
                        id_vip, balancing, reals, priority, weight, alter_priority)

                    messages.add_message(request, messages.SUCCESS, request_vip_messages.get(
                        "tab_edit_success") % 'real server')
                else:
                    html = lists['reals_error']
                    parse = False

            except (EnvironmentVipError, InvalidTimeoutValueError, InvalidBalMethodValueError, InvalidCacheValueError, InvalidPersistenceValueError, InvalidPriorityValueError, EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, request_vip_messages.get(
                    "tab_edit_error") % 'real server')

                try:
                    raise e
                except InvalidTimeoutValueError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get(
                        "error_existing_timeout") % vip['timeout'])
                except InvalidBalMethodValueError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get(
                        "error_existing_balancing") % vip['balancing'])
                except InvalidCacheValueError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get(
                        "error_existing_cache") % vip['cache'])
                except InvalidPersistenceValueError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get(
                        "error_existing_persistence") % vip['persistencia'])
                except InvalidPriorityValueError, e:
                    messages.add_message(
                        request, messages.ERROR, request_vip_messages.get("error_priority"))
                except EnvironmentVipError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get(
                        "error_existing_environment_vip") % (finality, client, environment))
                except (EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                    messages.add_message(request, messages.ERROR, e)

            except RealServerScriptError, e:
                logger.error(e)
                messages.add_message(request, messages.WARNING, e)
            except InvalidParameterError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
            except Exception, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)

        if parse is True:
            ports = []
            if "portas_servicos" in vip:
                if vip['portas_servicos'] is not None:
                    if type(vip['portas_servicos']['porta']) == unicode or len(vip['portas_servicos']['porta']) == 1:
                        vip['portas_servicos']['porta'] = [
                            vip['portas_servicos']['porta']]

                    ports = vip.get("portas_servicos").get('porta')

            ports_vip = []
            ports_real = []
            for port in ports:
                p = str(port).split(":")
                ports_vip.append(p[0])

                if len(p) > 1:
                    ports_real.append(p[1])
                else:
                    ports_real.append('')

            lists = mount_table_ports(lists, ports_vip, ports_real)

            id_equip, id_ip, weight, priority, equip, ip, status, version = parse_real_server(
                request, vip, client_api, id_vip, environment_vip, False, False)

            port_vip_list = list()
            port_real_list = list()

            if 'reals' in vip:
                reals_list = vip['reals'].get('real')
                if type(reals_list) is not list:
                    port_vip_list.append(reals_list['port_vip'])
                    port_real_list.append(reals_list['port_real'])
                else:
                    for real_l in reals_list:
                        port_vip_list.append(real_l['port_vip'])
                        port_real_list.append(real_l['port_real'])

            lists = mount_table_reals(
                lists, id_equip, id_ip, weight, priority, equip, ip, port_vip_list, port_real_list, version, status)

    except VipNaoExisteError, e:
        logger.error(e)
        messages.add_message(
            request, messages.ERROR, request_vip_messages.get("invalid_vip"))
        return redirect('vip-request.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    if request.method == "POST":
        return HttpResponse(content=html, status=200)
    else:
        return render_to_response(
            templates.VIPREQUEST_TAB_REAL_SERVER,
            lists,
            context_instance=RequestContext(request)
        )


@log
@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "read": True}, ])
def tab_healthcheck(request, id_vip):

    try:
        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()

        lists = dict()
        lists['idt'] = id_vip

        vip = client_api.create_vip().get_by_id(id_vip).get("vip")

        finality = vip.get("finalidade")
        client = vip.get("cliente")
        environment = vip.get("ambiente")

        environment_vip = client_api.create_environment_vip().search(
            None, finality, client, environment)
        id_environment_vip = environment_vip.get('environment_vip').get('id')

        client_ovip = client_api.create_option_vip()
        healthcheck_options = client_ovip.buscar_healthchecks(
            int(id_environment_vip))
        healthcheck_options = healthcheck_options.get('healthcheck_opt', [])

        vip['equipamento'] = validates_dict(vip, 'equipamento')
        vip['environments'] = validates_dict(vip, 'environments')
        vip['balancing'] = str(vip.get("metodo_bal")).upper()
        lists['vip'] = vip

        healthcheck_list = client_api.create_ambiente(
        ).listar_healtchcheck_expect_distinct().get("healthcheck_expect")

        # Already edited
        if request.method == "POST":

            form_healthcheck = forms.RequestVipFormHealthcheck(
                healthcheck_list, healthcheck_options, request.POST)
            lists['form_healthcheck'] = form_healthcheck

            if form_healthcheck.is_valid():

                healthcheck_type = form_healthcheck.cleaned_data[
                    "healthcheck_type"]
                healthcheck = form_healthcheck.cleaned_data["healthcheck"]
                expect = form_healthcheck.cleaned_data["expect"]

                if expect is not None:
                    expect = int(expect)

                try:

                    if environment_vip is None:
                        raise EnvironmentVipError(environment_vip)

                    client_api.create_vip().alter_healthcheck(
                        id_vip, healthcheck_type, healthcheck, expect)
                    messages.add_message(request, messages.SUCCESS, request_vip_messages.get(
                        "tab_edit_success") % 'healthcheck')

                except (EnvironmentVipError, InvalidTimeoutValueError, InvalidBalMethodValueError, InvalidCacheValueError, InvalidPersistenceValueError, InvalidPriorityValueError, EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, request_vip_messages.get(
                        "tab_edit_error") % 'healthcheck')

                    try:
                        raise e
                    except InvalidTimeoutValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_timeout") % vip['timeout'])
                    except InvalidBalMethodValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_balancing") % vip['balancing'])
                    except InvalidCacheValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_cache") % vip['cache'])
                    except InvalidPersistenceValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_persistence") % vip['persistencia'])
                    except InvalidPriorityValueError, e:
                        messages.add_message(
                            request, messages.ERROR, request_vip_messages.get("error_priority"))
                    except EnvironmentVipError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_environment_vip") % (finality, client, environment))
                    except (EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                        messages.add_message(request, messages.ERROR, e)

                except InvalidParameterError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                except Exception, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)

        # Request to edit
        else:
            expect = vip.get("id_healthcheck_expect")
            healthcheck_type = vip.get("healthcheck_type")
            healthcheck = vip.get("healthcheck")

            form_healthcheck = forms.RequestVipFormHealthcheck(healthcheck_list, healthcheck_options, initial={
                "healthcheck_type": healthcheck_type, "healthcheck": healthcheck, "expect": expect})

            lists['form_healthcheck'] = form_healthcheck

    except VipNaoExisteError, e:
        logger.error(e)
        messages.add_message(
            request, messages.ERROR, request_vip_messages.get("invalid_vip"))
        return redirect('vip-request.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(
        templates.VIPREQUEST_TAB_HEALTHCHECK,
        lists,
        context_instance=RequestContext(request)
    )


@log
@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "read": True}, ])
def tab_maxcon(request, id_vip):

    try:
        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()

        lists = dict()
        lists['idt'] = id_vip

        vip = client_api.create_vip().get_by_id(id_vip).get("vip")
        vip['equipamento'] = validates_dict(vip, 'equipamento')
        vip['environments'] = validates_dict(vip, 'environments')
        vip['balancing'] = str(vip.get("metodo_bal")).upper()
        lists['vip'] = vip

        # Already edited
        if request.method == "POST":

            form_real = forms.RequestVipFormReal(request.POST)
            lists['form_real'] = form_real

            if form_real.is_valid():

                maxcon = form_real.cleaned_data["maxcon"]
                # equip_name = form_real.cleaned_data["equip_name"]

                try:

                    finality = vip.get("finalidade")
                    client = vip.get("cliente")
                    environment = vip.get("ambiente")

                    environment_vip = client_api.create_environment_vip().search(
                        None, finality, client, environment)
                    if environment_vip is None:
                        raise EnvironmentVipError(environment_vip)

                    client_api.create_vip().alter_maxcon(id_vip, maxcon)
                    messages.add_message(request, messages.SUCCESS, request_vip_messages.get(
                        "tab_edit_success") % 'maxconn')

                except (EnvironmentVipError, InvalidTimeoutValueError, InvalidBalMethodValueError, InvalidCacheValueError, InvalidPersistenceValueError, InvalidPriorityValueError, EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                    logger.error(e)
                    messages.add_message(
                        request, messages.ERROR, request_vip_messages.get("tab_edit_error") % 'maxconn')

                    try:
                        raise e
                    except InvalidTimeoutValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_timeout") % vip['timeout'])
                    except InvalidBalMethodValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_balancing") % vip['balancing'])
                    except InvalidCacheValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_cache") % vip['cache'])
                    except InvalidPersistenceValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_persistence") % vip['persistencia'])
                    except InvalidPriorityValueError, e:
                        messages.add_message(
                            request, messages.ERROR, request_vip_messages.get("error_priority"))
                    except EnvironmentVipError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get(
                            "error_existing_environment_vip") % (finality, client, environment))
                    except (EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                        messages.add_message(request, messages.ERROR, e)

                except InvalidParameterError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                except Exception, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)

        # Request to edit
        else:
            maxcon = vip.get("maxcon")
            equip_name = vip.get("equip_name")

            form_real = forms.RequestVipFormReal(
                initial={"equip_name": equip_name, "maxcon": maxcon})
            lists['form_real'] = form_real

    except VipNaoExisteError, e:
        logger.error(e)
        messages.add_message(
            request, messages.ERROR, request_vip_messages.get("invalid_vip"))
        return redirect('vip-request.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(
        templates.VIPREQUEST_TAB_MAXCON,
        lists,
        context_instance=RequestContext(request)
    )


@log
@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "read": True}, ])
def status_real_server(request, id_vip, status):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_api = auth.get_clientFactory()
            client_vip = auth.get_clientFactory().create_vip()

            # All ids to be change status
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            enable = False
            if status == "enable":
                enable = True

            for idts in ids:

                try:

                    idt_vector = split_to_array(idts, sep="-")

                    equip_id = idt_vector[0]
                    ip_id = idt_vector[1]
                    version = idt_vector[2]
                    port_vip = idt_vector[3]
                    port_real = idt_vector[4]

                    if version == IP_VERSION.IPv4[1]:

                        if enable:
                            client_vip.habilitar_real(
                                id_vip, ip_id, equip_id, port_vip, port_real)
                        else:
                            client_vip.desabilitar_real(
                                id_vip, ip_id, equip_id, port_vip, port_real)

                    elif version == IP_VERSION.IPv6[1]:

                        if enable:
                            client_vip.enable_real_ipv6(
                                id_vip, ip_id, equip_id, port_vip, port_real)
                        else:
                            client_vip.disable_real_ipv6(
                                id_vip, ip_id, equip_id, port_vip, port_real)

                except ScriptError, e:
                    logger.error(e)
                    have_errors = True
                    equip_aux = client_api.create_equipamento().listar_por_id(
                        equip_id).get("equipamento")
                    error_list.append(equip_aux.get("nome"))

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant change nothing
            if len(error_list) == len(ids):
                messages.add_message(request, messages.ERROR, request_vip_messages.get(
                    "can_not_real_all") % ('Habilitar' if enable else 'Desabilitar'))

            # If cant change someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                messages.add_message(request, messages.WARNING, request_vip_messages.get(
                    "can_not_real") % (('Habilitar' if enable else 'Desabilitar'), msg[:-2]))

            # If all has ben changed
            elif have_errors is False:
                messages.add_message(request, messages.SUCCESS, request_vip_messages.get(
                    "success_real") % ('Habilitado' if enable else 'Desabilitado'))

            else:
                messages.add_message(request, messages.ERROR, request_vip_messages.get(
                    "can_not_real_all") % (('Habilitar' if enable else 'Desabilitar')))

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    return HttpResponseRedirect(reverse('vip-request.tab.real.server.status.edit', args=[id_vip]))


@csrf_exempt
@log
def generate_token(request):
    try:

        lists = {}

        form = forms.GenerateTokenForm(
            request.POST) if request.method == 'POST' else forms.GenerateTokenForm()

        if form.is_valid():

            user_ldap_ass = ""
            user = str(form.cleaned_data['user'])
            idt = None if not form.cleaned_data[
                'requestVip'] else form.cleaned_data['requestVip']
            ttl = ACCESS_EXTERNAL_TTL if not form.cleaned_data[
                'p'] else form.cleaned_data['p']

            # Login with LDAP
            if form.cleaned_data['is_ldap_user']:
                username_ldap, password_ldap = str(user).split("@")
                try:
                    user_ldap = Ldap("").get_user(username_ldap)
                except LDAPNotFoundError, e:
                    raise Exception(auth_messages.get("user_ldap_not_found"))

                pwd_ldap = user_ldap['userPassword']
                activate = user_ldap.get('nsaccountlock')
                pwd = password_ldap

                if re.match("\{(MD|md)5\}.*", pwd_ldap, 0):
                    pwd = base64.b64encode(hashlib.md5(pwd).digest())
                    pwd_ldap = pwd_ldap[pwd_ldap.index("}") + 1:]

                if pwd == pwd_ldap and (activate is None or activate.upper() == 'FALSE'):
                    # Valid User
                    client, client_user = validate_user_networkapi(
                        user, form.cleaned_data['is_ldap_user'])
                    user_ldap_client = client_user.get('user')
                    user_ldap_ass = user_ldap_client['user_ldap']
                else:
                    client_user = None
            else:
                # Valid User
                client, client_user = validate_user_networkapi(
                    user, form.cleaned_data['is_ldap_user'])

            # Valid User
            if client_user is None:
                raise UserNotAuthenticatedError("user_invalid")
            else:
                # Valid idt
                if idt is not None and not is_valid_int_param(idt):
                    raise Exception(
                        error_messages.get("invalid_param") % "requestVip")

                # Valid ttl
                if not is_valid_int_param(ttl):
                    raise Exception(error_messages.get("invalid_param") % "p")

                if idt is not None:
                    client.create_vip().get_by_id(idt)

                # Encrypt hash
                user_hash = Encryption().Encrypt(user + "@" + str(user_ldap_ass))

                # Get Authenticate User
                authenticate_user = client_user.get('user')

                # Get Permissions by Authenticate User
                permissions = authenticate_user and authenticate_user.get('permission')

                # Generates token
                key = "%s:%s:%s" % (__name__, str(user), str(strftime("%Y%m%d%H%M%S")))

                token = hashlib.sha1(key).hexdigest()

                data_to_cache = {"user_hash": user_hash, "permissions": permissions}

                # Set token in cache
                cache.set(token, data_to_cache, int(ttl))

                lists["token"] = token

                if idt is not None:
                    lists["url"] = reverse("vip-request.edit.external", args=[idt])
                else:
                    lists["url"] = reverse("vip-request.form.external")

            return render_to_response(templates.VIPREQUEST_TOKEN, lists, context_instance=RequestContext(request))

    except InvalidParameterError, e:
        logger.error(e)
        lists["error"] = error_messages.get("invalid_param") % "id"

    except VipNaoExisteError, e:
        logger.error(e)
        lists["error"] = request_vip_messages.get("invalid_vip")
    except Exception, e:
        logger.error(e)
        lists["error"] = e

    return render_to_response(
        templates.JSON_ERROR,
        lists,
        context_instance=RequestContext(request)
    )


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


def popular_rule_shared(request, client_api):

    lists = dict()
    status_code = None

    try:
        rule_id = get_param_in_request(request, 'rule_id')
        if rule_id is None:
            raise InvalidParameterError(
                "Parâmetro inválido: O campo Ambiente Vip inválido ou não foi informado.")

        rule = client_api.create_rule().get_rule_by_id(rule_id).get('rule')

        lists['rule'] = '\n'.join(rule['rule_contents'])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500

    # Returns Json
    return HttpResponse(
        loader.render_to_string(
            templates.AJAX_VIPREQUEST_RULE,
            lists,
            context_instance=RequestContext(request)
        ),
        status=status_code
    )


def model_ip_real_server_shared(request, client_api):

    lists = dict()
    lists['msg'] = ''
    lists['ips'] = ''
    ips = None
    equip = None
    balancing = None
    status_code = None

    try:

        id_evip = get_param_in_request(request, 'environment_vip')
        equip_name = get_param_in_request(request, 'equip_name')
        balancing = get_param_in_request(request, 'balancing')

        # equip_real = split_to_array(get_param_in_request(
        #     request, 'equip_real')) if get_param_in_request(request, 'equip_real') is not None else None
        # ips_real = split_to_array(get_param_in_request(
        #     request, 'ips_real')) if get_param_in_request(request, 'ips_real') is not None else None

        # Valid Equipament
        equip = client_api.create_equipamento().listar_por_nome(
            equip_name).get("equipamento")

        ips = client_api.create_ip().get_ip_by_equip_and_vip(
            equip_name, id_evip)

        ipv4 = validates_dict(ips, 'ipv4')
        ipv6 = validates_dict(ips, 'ipv6')

        # Valid is IP existing in table
        # Sprint 36 - Is possible repeat the same IP
        """for equi in equip_real:

            if equip_name == equi:

                if ipv4 is not None:

                    for i in range(0, len(ipv4)):

                        for ip_r in ips_real:

                            if  ( i <= (len(ipv4)-1) )  :

                                if ipv4[i]['ip'] == str(ip_r).replace("%3A", ":"):
                                    del ipv4[i]

                if ipv6 is not None:

                    for i in range(0, len(ipv6)):

                        for ip_r in ips_real:

                            if  ( i <= (len(ipv6)-1) )  :

                                if ipv6[i]['ip'] == str(ip_r).replace("%3A", ":"):
                                    del ipv6[i]"""

        ips['ipv4'] = ipv4
        ips['ipv6'] = ipv6

    except IpError, e:
        pass

    except EquipamentoNaoExisteError, e:
        logger.error(e)
        lists['msg'] = equip_group_messages.get("invalid_equipament_group")

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500

    lists['ips'] = loader.render_to_string(
        templates.AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER_HTML,
        {
            'ips': ips,
            'equip': equip,
            'balancing': balancing
        },
        context_instance=RequestContext(request)
    )

    # Returns Json
    return HttpResponse(
        loader.render_to_string(
            templates.AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER,
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


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def external_load_pool_for_copy(request, form_acess, client):
    return shared_load_pool(request, client, form_acess, external=True)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def load_pool_for_copy(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    return shared_load_pool(request, client)


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
            'healthcheck': healthcheck,
            'maxcon': pool.get('default_limit'),
            'identifier': pool.get('identifier')
        }

        lb_method_choices = facade_pool.populate_optionsvips_choices(client)
        servicedownaction_choices = facade_pool.populate_servicedownaction_choices(client)
        healthcheck_choices = _create_options_pool_as_healthcheck(client, environment_id)

        environment_choices = [(pool.get('environment').get('id'), pool.get('environment').get('name'))]
        form_pool = forms.PoolForm(
            environment_choices,
            lb_method_choices,
            servicedownaction_choices,
            healthcheck_choices,
            initial=form_initial
        )

        form_initial = {
            'healthcheck_request': healthcheck_request,
            'healthcheck_expect': healthcheck_expect,
            'healthcheck_destination': healthcheck_destination
        }

        form_healthcheck = forms.PoolHealthcheckForm(
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


def _create_options_pool_as_healthcheck(client, environment_id):

    options_pool_choices = [('', '-')]

    if environment_id:

        options_pool = client.create_pool().get_opcoes_pool_by_ambiente(
            environment_id
        ).get('opcoes_pool')

        for obj_option in options_pool:
            options_pool_choices.append((
                obj_option['opcao_pool']['description'],
                obj_option['opcao_pool']['description']
            ))

    return options_pool_choices


def _create_options_vip(client):

    default_balancing = 'Balanceamento'

    options_vip_choices = [('', '-')]

    options_vip = client.create_option_vip().get_all().get('option_vip')

    for obj_option in options_vip:
        if obj_option['tipo_opcao'] == default_balancing:
            options_vip_choices.append((
                obj_option['nome_opcao_txt'],
                obj_option['nome_opcao_txt']
            ))

    return options_vip_choices


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def external_load_options_pool(request, form_acess, client):

    return shared_load_options_pool(request, client, form_acess, external=True)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def load_options_pool(request):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    return shared_load_options_pool(request, client)


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


@csrf_exempt
@log
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def external_pool_member_items(request, form_acess, client):

    return shared_pool_member_items(
        request,
        client,
        form_acess,
        external=True
    )


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def pool_member_items(request):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    return shared_pool_member_items(request, client)


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


def _pool_dict(port_id, port, l4_protocol, l7_protocol, pool, l7_rule):

    pool_dict = {
        "id": int(port_id) if port_id else None,
        "port": int(port),
        "options": {
            "l4_protocol": int(l4_protocol),
            "l7_protocol": int(l7_protocol)
        },
        "pools": [{
            "server_pool": int(pool),
            "l7_rule": int(l7_rule),
            "l7_value": None
        }]
    }

    return pool_dict


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

############
# Forms
#############


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def edit_form(request, id_vip):
    """
    Method to call edit_form_shared
    """
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return edit_form_shared(request, id_vip, client_api)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_environment(request):
    """
    Method to call popular_environment_shared
    """
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return popular_environment_shared(request, client_api)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def add_form(request):
    """
    Method to call add_form_shared
    """
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return add_form_shared(request, client_api)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_options(request):
    """
    Method to call popular_options_shared
    """

    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return popular_options_shared(request, client_api)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def load_new_pool(request):
    """
    Method to call shared_load_new_pool
    """
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    return shared_load_new_pool(request, client)


@log
@login_required
@require_http_methods(["POST"])
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True},
    {"permission": POOL_CREATE_SCRIPT, "write": True},
    {"permission": POOL_REMOVE_SCRIPT, "write": True},
])
def save_pool(request):
    """
    Method to call shared_save_pool
    """
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    return shared_save_pool(request, client)

#############
# Forms external
#############


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def edit_form_external(request, id_vip, form_acess, client):
    """
    Method to call edit_form_shared when use by external way
    """
    return edit_form_shared(request, id_vip, client, form_acess, True)


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_options_external(request, form_acess, client):
    """
    Method to call popular_options_shared when use external way
    """
    return popular_options_shared(request, client)


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_environment_external(request, form_acess, client):
    """
    Method to call popular_environment_shared when use by external way
    """
    return popular_environment_shared(request, client)


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def add_form_external(request, form_acess, client):
    """
    Method to call add_form_shared when use by external way
    """
    return add_form_shared(request, client, form_acess, True)


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def external_load_new_pool(request, form_acess, client):
    """
    Method to call shared_load_new_pool when use by external way
    """
    return shared_load_new_pool(request, client, form_acess, external=True)


@csrf_exempt
@log
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True, "write": True},
    {"permission": POOL_ALTER_SCRIPT, "write": True},
    {"permission": POOL_CREATE_SCRIPT, "write": True},
    {"permission": POOL_REMOVE_SCRIPT, "write": True},
])
def external_save_pool(request, form_acess, client):
    """
    Method to call shared_save_pool when use by external way
    """
    return shared_save_pool(request, client, form_acess, external=True)


############
# methods shared
#############
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
        lists['reals_error'] = ''
        lists['form_acess'] = form_acess
        lists['external'] = external

        if external:
            lists['token'] = form_acess.initial.get("token")

        vip = client_api.create_api_vip_request().get_vip_request_details(id_vip)['vips'][0]

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

        lists = dict()
        lists["form_pool"] = forms.PoolForm(
            environment_choices, lb_method_choices, servicedownaction_choices)
        lists["form_healthcheck"] = forms.PoolHealthcheckForm()
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


@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "read": True}, ])
def delete_validate_create_remove_2(request, operation):

    operation_text = OPERATION.get(int(operation))

    if request.method == 'POST':

        form = DeleteForm(request.POST) if operation_text == 'DELETE' else ValidateForm(
            request.POST) if operation_text == 'VALIDATE' else CreateForm(request.POST) if operation_text == 'CREATE' else RemoveForm(request.POST)
        id = 'ids' if operation_text == 'DELETE' else 'ids_val' if operation_text == 'VALIDATE' else 'ids_create' if operation_text == 'CREATE' else 'ids_remove'

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_vip = auth.get_clientFactory().create_vip()
            client_api_vip = auth.get_clientFactory().create_api_vip_request()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data[id])
            vip_id = form.cleaned_data[id]

            # All messages to display
            error_list = list()
            error_list_created = list()
            error_list_not_validate = list()

            # Control others exceptions
            have_errors = False

            # FLAG only for  ERROR  in create
            all_ready_msg_script_error = False

            # For each script selected to remove
            try:
                if operation_text == 'DELETE':
                    client_api_vip.delete_vip_request(vip_id)
                elif operation_text == 'REMOVE':
                    client_api_vip.remove_vip(vip_id)
                elif operation_text == 'CREATE':
                    client_api_vip.create_vip(vip_id)

            except VipAllreadyCreateError, e:
                logger.error(e)
                error_list_created.append(vip_id)
            except VipError, e:
                logger.error(e)
                error_list_not_validate.append(vip_id)
            except ScriptError, e:
                logger.error(e)
                if not all_ready_msg_script_error:
                    messages.add_message(request, messages.ERROR, e)
                all_ready_msg_script_error = True
                error_list.append(vip_id)
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                error_list.append(vip_id)

            for id_vip in ids:
                try:
                    if operation_text == 'VALIDATE':
                        client_vip.validate(id_vip)
                except VipAllreadyCreateError, e:
                    logger.error(e)
                    error_list_created.append(id_vip)
                except VipError, e:
                    logger.error(e)
                    error_list_not_validate.append(id_vip)
                except ScriptError, e:
                    logger.error(e)
                    if not all_ready_msg_script_error:
                        messages.add_message(request, messages.ERROR, e)
                    all_ready_msg_script_error = True
                    error_list.append(id_vip)
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    error_list.append(id_vip)

            msg_error_call, msg_sucess_call, msg_some_error_call = get_error_mesages(
                operation_text)

            if len(error_list_not_validate) > 0:

                msg = ""
                for id_error in error_list_not_validate:
                    msg = msg + id_error + ','

                if operation_text == 'REMOVE':
                    msg = request_vip_messages.get('not_created') % msg[:-1]
                else:
                    msg = request_vip_messages.get(
                        'validate_before') % msg[:-1]
                messages.add_message(request, messages.WARNING, msg)
                have_errors = True

            if len(error_list_created) > 0:

                msg = ""
                for id_error in error_list_created:
                    msg = msg + id_error + ','

                msg = request_vip_messages.get('all_ready_create') % msg[:-1]
                messages.add_message(request, messages.WARNING, msg)
                have_errors = True

            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(
                    request, messages.ERROR, request_vip_messages.get(msg_error_call))

            # If cant remove someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = request_vip_messages.get(msg_some_error_call) % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all has ben removed
            elif have_errors is False:
                messages.add_message(
                    request, messages.SUCCESS, request_vip_messages.get(msg_sucess_call))

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('vip-request.list')


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
        healthcheck_choices = _create_options_pool_as_healthcheck(client, environment_id)

        form = forms.PoolForm(
            environment_choices,
            lb_method_choices,
            servicedownaction_choices,
            healthcheck_choices,
            request.POST
        )

        if form.is_valid():

            param_dic = {}

            pool = dict()
            pool["id"] = pool_id

            servicedownaction = facade_pool.format_servicedownaction(client, form)
            healthcheck = facade_pool.format_healthcheck(request)

            pool["identifier"] = str(form.cleaned_data['identifier'])
            pool["default_port"] = int(form.cleaned_data['default_port'])
            pool["environment"] = int(form.cleaned_data['environment'])
            pool["servicedownaction"] = servicedownaction
            pool["lb_method"] = str(form.cleaned_data['balancing'])
            pool["healthcheck"] = healthcheck
            pool["default_limit"] = int(form.cleaned_data['maxcon'])
            server_pool_members = facade_pool.format_server_pool_members(request, pool["default_limit"])
            pool["server_pool_members"] = server_pool_members

            client.create_pool().save_pool(pool)
            if pool_id:
                param_dic['message'] = pool_messages.get('success_update')
            else:
                param_dic['message'] = pool_messages.get('success_insert')

            return HttpResponse(json.dumps(param_dic), content_type="application/json")

        return render_message_json('<br>'.join(form.errors), messages.ERROR)

    except Exception, e:
        logger.error(e)
        return render_message_json(str(e), messages.ERROR)


##########
# functions
#######
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
    # list of pools
    pool_ids = valid_field_table_dynamic(request.POST.getlist('idsPool'))
    # list of port's ids
    ports_vip_ids = valid_field_table_dynamic(request.POST.getlist('ports_vip_ids'))
    # ports
    ports_vip_ports = valid_field_table_dynamic(request.POST.getlist('ports_vip_ports'))
    # list of l4 protocols
    ports_vip_l4_protocols = valid_field_table_dynamic(request.POST.getlist('ports_vip_l4_protocols'))
    # list of l7 protocols
    ports_vip_l7_protocols = valid_field_table_dynamic(request.POST.getlist('ports_vip_l7_protocols'))

    # valid ports and pools
    lists, is_valid_ports = _valid_ports(lists, ports_vip_ports)
    lists, is_valid_pools = _validate_pools(lists, pool_ids)

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
                except NetworkAPIClientError, e:
                    is_valid = False
                    is_error = True
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)

            if not is_error:

                # l7 rule not implemented yet, set value default
                l7_rule = None
                for l7 in forms_aux['l7_rule']:
                    if l7["nome_opcao_txt"] == "(nenhum)":
                        l7_rule = int(l7["id"])
                        break
                pools = list()
                for i, pool_id in enumerate(pool_ids):
                    pools.append(
                        _pool_dict(
                            ports_vip_ids[i],
                            ports_vip_ports[i],
                            ports_vip_l4_protocols[i],
                            ports_vip_l7_protocols[i],
                            pool_ids[i],
                            l7_rule
                        )
                    )

                if edit:
                    vip = _vip_dict(form_basic, environment_vip, options, ipv4, ipv6, pools, vip_id)
                    vip = client_api.create_api_vip_request().update_vip_request(vip, vip_id)
                    id_vip_created = vip_id
                else:
                    vip = _vip_dict(form_basic, environment_vip, options, ipv4, ipv6, pools, vip_id)
                    vip = client_api.create_api_vip_request().save_vip_request(vip)
                    id_vip_created = vip[0].get("id")

        except NetworkAPIClientError, e:
            is_valid = False
            is_error = True
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)

        finally:
            try:
                if is_error and ipv4_check and ipv4_type == '0' and ipv4 is not None:
                    client_api.create_ip().delete_ip4(ipv4)

                if is_error and ipv6_check and ipv6_type == '0' and ipv6 is not None:
                    client_api.create_api_network_ipv6().delete_ipv6(ipv6)

            except NetworkAPIClientError, e:
                logger.error(e)
    else:
        is_valid = False

    pools_add = list()
    if pool_ids:
        pools_json = client_api.create_api_pool().get_pool_details(';'.join(pool_ids))["server_pools"]
        for index, pool_id in enumerate(pool_ids):
            l4_protocol = [env for env in forms_aux["l4_protocol"] if int(ports_vip_l4_protocols[index]) == int(env["id"])][0]
            l7_protocol = [env for env in forms_aux["l7_protocol"] if int(ports_vip_l7_protocols[index]) == int(env["id"])][0]
            raw_server_pool = {
                "id": ports_vip_ids[index],
                "port": ports_vip_ports[index],
                "options": {
                    "l4_protocol": l4_protocol,
                    "l7_protocol": l7_protocol
                },
                "pools": [{
                    "server_pool": pools_json[index]
                }]
            }
            pools_add.append(raw_server_pool)

    lists['pools_add'] = pools_add
    lists['form_basic'] = form_basic
    lists['form_environment'] = form_environment
    lists['form_option'] = form_option
    lists['form_port_option'] = form_port_option
    lists['form_ip'] = form_ip

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


#######
# ajax request
#######
@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "read": True}, ])
def ajax_list_vips(request):
    '''
        Return list of vip request by search field
    '''

    try:

        # If form was submited
        if request.method == "GET":

            # Get user auth
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            search_form = forms.SearchVipRequestForm(request.GET)

            if search_form.is_valid():

                id_vip = search_form.cleaned_data['id_request']
                ipv4 = search_form.cleaned_data["ipv4"]
                ipv6 = search_form.cleaned_data["ipv6"]
                vip_created = search_form.cleaned_data["vip_created"]

                extends_search = dict()
                if len(ipv4) > 0:
                    if request.GET["oct1"]:
                        extends_search.update({'ipv4__oct1': request.GET["oct1"]})
                    if request.GET["oct2"]:
                        extends_search.update({'ipv4__oct2': request.GET["oct2"]})
                    if request.GET["oct3"]:
                        extends_search.update({'ipv4__oct3': request.GET["oct3"]})
                    if request.GET["oct4"]:
                        extends_search.update({'ipv4__oct4': request.GET["oct4"]})
                elif len(ipv6) > 0:
                    extends_search = dict()
                    if request.GET["oct1"]:
                        extends_search.update({'ipv6__block1__iexact': request.GET["oct1"]})
                    if request.GET["oct2"]:
                        extends_search.update({'ipv6__block2__iexact': request.GET["oct2"]})
                    if request.GET["oct3"]:
                        extends_search.update({'ipv6__block3__iexact': request.GET["oct3"]})
                    if request.GET["oct4"]:
                        extends_search.update({'ipv6__block4__iexact': request.GET["oct4"]})
                    if request.GET["oct5"]:
                        extends_search.update({'ipv6__block5__iexact': request.GET["oct5"]})
                    if request.GET["oct6"]:
                        extends_search.update({'ipv6__block6__iexact': request.GET["oct6"]})
                    if request.GET["oct7"]:
                        extends_search.update({'ipv6__block7__iexact': request.GET["oct7"]})
                    if request.GET["oct8"]:
                        extends_search.update({'ipv6__block8__iexact': request.GET["oct8"]})

                if vip_created:
                    extends_search.update({'created': vip_created})
                if id_vip:
                    extends_search.update({"id": id_vip})

                # Pagination
                column_index_name_map = {
                    0: '',
                    1: 'id',
                    2: 'ipv4',
                    4: 'description',
                    3: 'ipv6',
                    5: 'description',
                    6: 'equipamento',
                    7: 'ambiente',
                    8: 'criado',
                    9: ''}
                dtp = DataTablePaginator(request, column_index_name_map)

                # Make params
                dtp.build_server_side_list()

                # Set params in simple Pagination class
                pagination = Pagination(
                    dtp.start_record,
                    dtp.end_record,
                    dtp.asorting_cols,
                    dtp.searchable_columns,
                    dtp.custom_search)

                # Call API passing all params
                # vips = client.create_vip().list_vip_requests(
                #     id_vip, ip, pag, vip_create)

                data = dict()
                data["start_record"] = pagination.start_record
                data["end_record"] = pagination.end_record
                data["asorting_cols"] = pagination.asorting_cols
                data["searchable_columns"] = pagination.searchable_columns
                data["custom_search"] = pagination.custom_search or ""
                data["extends_search"] = [extends_search] if extends_search else []

                vips = client.create_api_vip_request().search_vip_request_details(data)

                # Returns JSON
                return dtp.build_response(
                    vips["vips"],
                    vips["total"],
                    templates.AJAX_VIPREQUEST_LIST,
                    request
                )

            else:
                # Remake search form
                lists = dict()
                lists["search_form"] = search_form

                # Returns HTML
                response = HttpResponse(
                    loader.render_to_string(
                        templates.SEARCH_FORM_ERRORS,
                        lists,
                        context_instance=RequestContext(request)
                    )
                )
                # Send response status with error
                response.status_code = 412
                return response

    except NetworkAPIClientError, e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')
    except BaseException, e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')
