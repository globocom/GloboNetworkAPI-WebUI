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
import logging
import re
import socket
from time import strftime

from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from networkapiclient.exception import InvalidParameterError
from networkapiclient.exception import NetworkAPIClientError
from networkapiclient.exception import ScriptError
from networkapiclient.exception import UserNotAuthenticatedError
from networkapiclient.exception import VipAllreadyCreateError
from networkapiclient.exception import VipError
from networkapiclient.exception import VipNaoExisteError
from networkapiclient.Pagination import Pagination

from CadVlan import templates
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.forms import CreateForm
from CadVlan.forms import DeleteForm
from CadVlan.forms import RemoveForm
from CadVlan.Ldap.model import Ldap
from CadVlan.Ldap.model import LDAPNotFoundError
from CadVlan.messages import auth_messages
from CadVlan.messages import error_messages
from CadVlan.messages import request_vip_messages
from CadVlan.permissions import POOL_ALTER_SCRIPT
from CadVlan.permissions import POOL_CREATE_SCRIPT
from CadVlan.permissions import POOL_MANAGEMENT
from CadVlan.permissions import POOL_REMOVE_SCRIPT
from CadVlan.permissions import VIP_ALTER_SCRIPT
from CadVlan.permissions import VIP_CREATE_SCRIPT
from CadVlan.permissions import VIP_REMOVE_SCRIPT
from CadVlan.permissions import VIPS_REQUEST
from CadVlan.settings import ACCESS_EXTERNAL_TTL
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.Decorators import has_perm
from CadVlan.Util.Decorators import has_perm_external
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Util.shortcuts import render_message_json
from CadVlan.Util.utility import DataTablePaginator
from CadVlan.Util.utility import is_valid_int_param
from CadVlan.VipRequest import facade
from CadVlan.VipRequest import forms
from CadVlan.VipRequest.encryption import Encryption


logger = logging.getLogger(__name__)

OPERATION = {0: 'DELETE', 1: 'CREATE', 3: 'REMOVE'}

vip_all_permission = {"permission": VIPS_REQUEST, "read": True, "write": True}
pool_all_permission = {"permission": POOL_MANAGEMENT, "read": True, "write": True}
pool_read_permission = {"permission": POOL_MANAGEMENT, "read": True}


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True},
])
def search_list(request):
    try:
        lists = dict()
        lists["delete_form"] = DeleteForm()
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
@has_perm([
    {"permission": VIPS_REQUEST, "read": True},
])
def ajax_view_vip(request, id_vip):
    lists = dict()
    return facade.ajax_shared_view_vip(request, id_vip, lists)


@log
@login_required
@has_perm([
    {"permission": VIP_CREATE_SCRIPT, "write": True}
])
def create_vip(request):
    delete_validate_create_remove(request, 1)
    # Redirect to list_all action
    return redirect('vip-request.list')


@log
@login_required
@has_perm([
    {"permission": VIP_REMOVE_SCRIPT, "write": True}
])
def remove_vip(request):
    delete_validate_create_remove(request, 3)
    # Redirect to list_all action
    return redirect('vip-request.list')


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "write": True}
])
def delete_vip(request):
    delete_validate_create_remove(request, 0)
    # Redirect to list_all action
    return redirect('vip-request.list')


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_client_external(request, form_acess, client):
    return facade.popular_client_shared(request, client)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def ajax_popular_client(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return facade.popular_client_shared(request, client_api)


@log
@login_required
@has_perm([
    {"permission": VIP_ALTER_SCRIPT, "read": True},
])
def tab_pools(request, id_vip):

    lists = dict()
    lists['idt'] = id_vip
    lists['status_form'] = DeleteForm()

    try:
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()

        vip = client_api.create_api_vip_request().get(ids=[id_vip], kind='details')['vips'][0]
        lists['vip'] = vip

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    if vip.get('created') is not True:
        return redirect(reverse('vip-request.edit', args=[id_vip]))

    return render_to_response(
        templates.VIPREQUEST_TAB_POOLS,
        lists,
        context_instance=RequestContext(request)
    )


@log
@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "read": True}, ])
def tab_vip_edit(request, id_vip):

    lists = dict()
    lists['idt'] = id_vip
    lists["action"] = reverse('vip-request.tab.edit', args=[id_vip])
    lists['status_form'] = DeleteForm()
    # form_option = None
    try:
        forms_aux = dict()
        forms_aux['pools'] = list()

        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()

        vip = client_api.create_api_vip_request()\
            .get(ids=[id_vip], kind='details',
                 include=['groups_permissions'])['vips'][0]

        group_users_list = client_api.create_grupo_usuario().listar()
        forms_aux['group_users'] = group_users_list

        if vip.get('created') is not True:
            return redirect(reverse('vip-request.edit', args=[id_vip]))

        lists['vip'] = vip

        options_list = facade._get_optionsvip_by_environmentvip(vip.get('environmentvip').get('id'), client_api)

        pools = client_api.create_api_pool().pool_by_environmentvip(vip.get('environmentvip').get('id'))

        forms_aux['timeout'] = [vip.get('options').get('timeout')]
        forms_aux['persistence'] = options_list['persistence']
        forms_aux['trafficreturn'] = [vip.get('options').get('traffic_return')]
        forms_aux['caches'] = [vip.get('options').get('cache_group')]
        forms_aux['l4_protocol'] = options_list['l4_protocol']
        forms_aux['l7_protocol'] = options_list['l7_protocol']
        forms_aux['l7_rule'] = options_list['l7_rule']
        forms_aux['pools'] = pools
        forms_aux['overwrite'] = False

        initial_form_request_vip_option = {
            "environment_vip": vip.get('environmentvip').get('id'),
            "timeout": vip.get('options').get('timeout').get('id')
            if vip.get('options').get('timeout') else None,
            "persistence": vip.get('options').get('persistence').get('id')
            if vip.get('options').get('persistence') else None,
            "trafficreturn": vip.get('options').get('traffic_return').get('id')
            if vip.get('options').get('traffic_return') else None,
            "caches": vip.get('options').get('cache_group').get('id')
            if vip.get('options').get('cache_group') else None
        }

        if request.method == 'POST':
            lists, is_valid, id_vip = facade._valid_form_and_submit_update(
                forms_aux,
                vip,
                request,
                lists,
                client_api,
                id_vip
            )

            lists['form_option'] = forms.RequestVipOptionVipEditForm(
                forms_aux,
                request.POST,
                initial=initial_form_request_vip_option
            )

            if is_valid:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    request_vip_messages.get("success_edit")
                )

                return redirect('vip-request.list')
        else:

            group_users_list_selected = []
            for group in vip["groups_permissions"]:
                group_users_list_selected.append(group["user_group"]["id"])

            lists['form_basic'] = forms.RequestVipBasicForm(
                forms_aux,
                initial={
                    "business": vip.get("business"),
                    "service": vip.get("service"),
                    "name": vip.get("name"),
                    "created": vip.get("created")
                }
            )

            lists['form_group_users'] = forms.RequestVipGroupUsersForm(
                forms_aux,
                edit=True,
                initial={
                    "group_users": group_users_list_selected
                }

            )

            lists['form_option'] = forms.RequestVipOptionVipEditForm(
                forms_aux,
                initial=initial_form_request_vip_option
            )

            lists['form_port_option'] = forms.RequestVipPortOptionVipForm(forms_aux)

            pools_add = vip.get("ports")
            lists['pools_add'] = pools_add

    except VipNaoExisteError, e:
        logger.error(e)
        messages.add_message(
            request, messages.ERROR, request_vip_messages.get("invalid_vip"))
        return redirect('vip-request.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(
        templates.VIPREQUEST_TAB_VIP_EDIT,
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
                    client, client_user = facade.validate_user_networkapi(
                        user, form.cleaned_data['is_ldap_user'])
                    user_ldap_client = client_user.get('user')
                    user_ldap_ass = user_ldap_client['user_ldap']
                else:
                    client_user = None
            else:
                # Valid User
                client, client_user = facade.validate_user_networkapi(
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


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def external_load_pool_for_copy(request, form_acess, client):
    return facade.shared_load_pool(request, client, form_acess, external=True)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def load_pool_for_copy(request):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    return facade.shared_load_pool(request, client)


@log
@csrf_exempt
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def external_load_options_pool(request, form_acess, client):

    return facade.shared_load_options_pool(request, client, form_acess, external=True)


@log
@login_required
@has_perm([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def load_options_pool(request):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    return facade.shared_load_options_pool(request, client)


@csrf_exempt
@log
@has_perm_external([
    {"permission": VIPS_REQUEST, "read": True, "write": True},
    {"permission": POOL_MANAGEMENT, "read": True},
])
def external_pool_member_items(request, form_acess, client):

    return facade.shared_pool_member_items(
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

    return facade.shared_pool_member_items(request, client)


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
    return facade.edit_form_shared(request, id_vip, client_api)


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
    return facade.popular_environment_shared(request, client_api)


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
    return facade.add_form_shared(request, client_api)


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
    return facade.popular_options_shared(request, client_api)


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
    return facade.shared_load_new_pool(request, client)


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
    return facade.shared_save_pool(request, client)


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
    return facade.edit_form_shared(request, id_vip, client, form_acess, True)


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
    return facade.popular_options_shared(request, client)


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
    return facade.popular_environment_shared(request, client)


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
    return facade.add_form_shared(request, client, form_acess, True)


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
    return facade.shared_load_new_pool(request, client, form_acess, external=True)


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
    return facade.shared_save_pool(request, client, form_acess, external=True)


@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "read": True}, ])
def delete_validate_create_remove(request, operation):

    operation_text = OPERATION.get(int(operation))

    if request.method == 'POST':

        form = DeleteForm(request.POST) if operation_text == 'DELETE'\
            else CreateForm(request.POST) if operation_text == 'CREATE'\
            else RemoveForm(request.POST)

        id = 'ids' if operation_text == 'DELETE' else 'ids_create'\
            if operation_text == 'CREATE' else 'ids_remove'

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
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

            msg_error_call, msg_sucess_call, msg_some_error_call = facade.get_error_mesages(
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
                vip_with_onwer = search_form.cleaned_data["vip_with_onwer"]
                hostname = search_form.cleaned_data["hostname"]

                extends_search = dict()
                if hostname:
                    extends_search.update(prepare_hostname(hostname))
                elif len(ipv4) > 0:
                    if request.GET["oct1"]:
                        extends_search.update({'ipv4__oct1': request.GET["oct1"]})
                    if request.GET["oct2"]:
                        extends_search.update({'ipv4__oct2': request.GET["oct2"]})
                    if request.GET["oct3"]:
                        extends_search.update({'ipv4__oct3': request.GET["oct3"]})
                    if request.GET["oct4"]:
                        extends_search.update({'ipv4__oct4': request.GET["oct4"]})
                elif len(ipv6) > 0:
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
                if vip_with_onwer:
                    user = auth.get_user().get_id()
                    extends_search.update({'viprequestgrouppermission__user_group__usuario': user})

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

                vips = client.create_api_vip_request().search(
                    search=data,
                    kind='details',
                    fields=['id', 'name', 'environmentvip', 'ipv4',
                            'ipv6', 'equipments', 'created'])

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

    except NetworkAPIClientError, error:
        logger.error(error)
        return HttpResponseServerError(error, mimetype='application/javascript')
    except BaseException, error:
        logger.error(error)
        return HttpResponseServerError(error, mimetype='application/javascript')


def prepare_hostname(hostname):
    try:
        ip = socket.gethostbyname(hostname).split('.')
        octs = {
            'ipv4__oct1': ip[0],
            'ipv4__oct2': ip[1],
            'ipv4__oct3': ip[2],
            'ipv4__oct4': ip[3]
        }

        return octs

    except:
        raise Exception('IP not found!')
