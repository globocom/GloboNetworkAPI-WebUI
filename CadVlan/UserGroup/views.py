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
import codecs
import logging
import re

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from networkapiclient.exception import InvalidParameterError
from networkapiclient.exception import NetworkAPIClientError
from networkapiclient.exception import PermissaoAdministrativaDuplicadaError
from networkapiclient.Pagination import Pagination

from CadVlan import templates
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.constants import SERVERPOOL_OBJ_TYPE
from CadVlan.constants import VIPREQUEST_OBJ_TYPE
from CadVlan.constants import VLAN_OBJ_TYPE
from CadVlan.forms import DeleteForm
from CadVlan.forms import DeleteFormAux
from CadVlan.messages import error_messages
from CadVlan.messages import object_group_perm_gen_messages
from CadVlan.messages import object_group_perm_messages
from CadVlan.messages import perm_group_messages
from CadVlan.messages import user_group_messages
from CadVlan.Net.business import is_valid_ipv4
from CadVlan.Net.business import is_valid_ipv6
from CadVlan.permissions import ADMINISTRATION
from CadVlan.settings import PATH_PERMLISTS
from CadVlan.templates import USERGROUP_AJAX_INDIVIDUAL_PERMISSIONS
from CadVlan.templates import USERGROUP_AJAX_OBJECTS
from CadVlan.templates import USERGROUP_CREATE_INDIVIDUAL_PERMS
from CadVlan.templates import USERGROUP_EDIT_GENERAL_PERMS
from CadVlan.templates import USERGROUP_EDIT_INDIVIDUAL_PERMS
from CadVlan.templates import USERGROUP_INDIVIDUAL_PERMS
from CadVlan.templates import USERGROUP_LIST
from CadVlan.UserGroup import facade
from CadVlan.UserGroup.forms import DeletePermsForm
from CadVlan.UserGroup.forms import GeneralPermsGroupUserEditForm
from CadVlan.UserGroup.forms import HiddenIdsPermsForm
from CadVlan.UserGroup.forms import IndividualPermsGroupUserCreateForm
from CadVlan.UserGroup.forms import IndividualPermsGroupUserEditForm
from CadVlan.UserGroup.forms import PermissionGroupForm
from CadVlan.UserGroup.forms import UserGroupForm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.Decorators import has_perm
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Util.shortcuts import render_message_json
from CadVlan.Util.utility import convert_boolean_to_int
from CadVlan.Util.utility import convert_string_to_boolean
from CadVlan.Util.utility import DataTablePaginator
from CadVlan.Util.utility import validates_dict
logger = logging.getLogger(__name__)


def parse_cad_perms(filename):
    permtree = list()

    with codecs.open(filename, "r", "utf-8") as fl:
        data = fl.read()

        # iterate over cadvlan functions
        for permcad in re.finditer(ur'^(?P<function>[A-Z][^\n]+)\n(?P<resto>(?:\t[a-zA-Z _]+\n\t\t(?:False|True)\n\t\t(?:False|True)\n)+(?:\tapi:\n(?:\t[a-zA-Z]+\n\t[a-zA-Z0-9_\(\)]+\n(?:\t\t[a-zA-Z_]+\n\t\t(?:Leitura|Escrita)\n\t\t(?:True|False)\n\t\t(?:None|Leitura|Escrita|Update_Config)\n)*)+)*)', data, re.MULTILINE | re.UNICODE):
            permcadvlan = dict()
            permcadvlan['function'] = permcad.group('function')
            permcadvlan['perms'] = list()
            permcadvlan['api_calls'] = None

            resto = permcad.group('resto')

            # iterate over cadvlan perms
            for perms_cad in re.finditer('^\t(?P<perm>[a-zA-Z_]+)\n\t\t(?P<read>False|True)\n\t\t(?P<write>False|True)\n', resto, re.MULTILINE):
                new_perm = dict()
                new_perm['perm'] = perms_cad.group('perm')
                new_perm['read'] = perms_cad.group('read')
                new_perm['write'] = perms_cad.group('write')

                permcadvlan['perms'].append(new_perm)

            api_data = re.search(
                '\tapi:\n((?:\t[a-zA-Z]+\n\t[a-zA-Z0-9_\(\)]+\n(?:\t\t[a-zA-Z_]+\n\t\t(?:Leitura|Escrita)\n\t\t(?:True|False)\n\t\t(?:None|Leitura|Escrita|Update_Config)\n)*)+)', resto, re.MULTILINE)
            if api_data is not None:

                permcadvlan['api_calls'] = list()
                api_data = api_data.group(1)

                # iterate over api calls
                for api_call in re.finditer('\t(?P<class>[a-zA-Z0-9]+)\n\t(?P<function>[a-zA-Z0-9_\(\)]+)\n(?P<mais_resto>(?:\t\t[a-zA-Z_]+\n\t\t(?:Leitura|Escrita)\n\t\t(?:True|False)\n\t\t(?:None|Leitura|Escrita|Update_Config)\n)+)*', api_data, re.MULTILINE):
                    perm_api = dict()
                    perm_api['class'] = api_call.group('class')
                    perm_api['function'] = api_call.group('function')

                    # iterate over api function perms
                    resto_perms_api = api_call.group('mais_resto')
                    if resto_perms_api is not None:
                        perm_api['perms'] = list()

                        for api_new_perm in re.finditer('\t\t(?P<perm>[a-zA-Z_]+)\n\t\t(?P<type>Leitura|Escrita)\n\t\t(?P<equip>True|False)\n\t\t(?P<equip_type>None|Leitura|Escrita|Update_Config)\n', resto_perms_api, re.MULTILINE):
                            perm_api_call = dict()
                            perm_api_call['perm'] = api_new_perm.group('perm')
                            perm_api_call['type'] = api_new_perm.group('type')
                            perm_api_call[
                                'equip'] = api_new_perm.group('equip')
                            perm_api_call['equip_type'] = api_new_perm.group(
                                'equip_type')

                            perm_api['perms'].append(perm_api_call)

                    permcadvlan['api_calls'].append(perm_api)

            if permcadvlan['api_calls'] is not None:
                permcadvlan['api_calls'].sort(
                    key=lambda call: (call['class'], call['function']))
            permtree.append(permcadvlan)

    permtree.sort(key=lambda perm: perm['function'])
    return permtree


def parse_api_perms(filename):
    apitree = list()

    with codecs.open(filename, "r", "utf-8") as fl:
        data = fl.read()

        # iterate over api calls
        for api_call in re.finditer('(?P<class>[a-zA-Z0-9]+)\n(?P<function>[a-zA-Z0-9_\(\)]+)\n(?P<mais_resto>(?:\t[a-zA-Z_]+\n\t(?:Leitura|Escrita)\n\t(?:True|False)\n\t(?:None|Leitura|Escrita|Update_Config)\n)+)*', data, re.MULTILINE):
            perm_api = dict()
            perm_api['class'] = api_call.group('class')
            perm_api['function'] = api_call.group('function')

            # iterate over api function perms
            resto_perms_api = api_call.group('mais_resto')
            if resto_perms_api is not None:
                perm_api['perms'] = list()

                for api_new_perm in re.finditer('\t(?P<perm>[a-zA-Z_]+)\n\t(?P<type>Leitura|Escrita)\n\t(?P<equip>True|False)\n\t(?P<equip_type>None|Leitura|Escrita|Update_Config)\n', resto_perms_api, re.MULTILINE):
                    perm_api_call = dict()
                    perm_api_call['perm'] = api_new_perm.group('perm')
                    perm_api_call['type'] = api_new_perm.group('type')
                    perm_api_call['equip'] = api_new_perm.group('equip')
                    perm_api_call['equip_type'] = api_new_perm.group(
                        'equip_type')

                    perm_api['perms'].append(perm_api_call)

            apitree.append(perm_api)

    apitree.sort(key=lambda call: (call['class'], call['function']))
    return apitree


def list_individ_perms_of_group_user(request, id_ugroup, id_type_obj):

    lists = dict()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['group_name'] = client.create_grupo_usuario().\
            search(id_ugroup)['user_group']['nome']
        lists['object_type'] = client.create_api_object_type().\
            get([id_type_obj])['ots'][0]['name']

        lists['id_ugroup'] = id_ugroup
        lists['id_type_obj'] = id_type_obj
        initial = {'id_ugroup': id_ugroup, 'id_type_obj': id_type_obj}
        lists['delete_form'] = DeletePermsForm(initial=initial)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('home')

    return render_to_response(USERGROUP_INDIVIDUAL_PERMS, lists,
                              context_instance=RequestContext(request))


def edit_individ_perms_of_object(request, id_ugroup, id_type_obj, id_obj):

    try:
        lists = {}

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['id_ugroup'] = id_ugroup
        lists['id_type_obj'] = id_type_obj
        lists['id_obj'] = id_obj

        type_obj = client.create_api_object_type().get(
            [int(id_type_obj)])['ots'][0]['name']

        if type_obj == VIPREQUEST_OBJ_TYPE:
            obj_name = facade.get_vips_request(client, None,
                                               None, id_obj)['objs'][0]['name']

        elif type_obj == SERVERPOOL_OBJ_TYPE:
            obj_name = facade.get_server_pools(client, None,
                                               None, id_obj)['objs'][0]['identifier']

        elif type_obj == VLAN_OBJ_TYPE:
            obj_name = facade.get_vlans(client, None,
                                        None, id_obj)['objs'][0]['name']

        lists['object_name'] = obj_name

        if request.method == 'POST':

            lists['group_name'] = client.create_grupo_usuario(). \
                search(id_ugroup)['user_group']['nome']
            lists['object_type'] = client.create_api_object_type(). \
                get([id_type_obj])['ots'][0]['name']

            form_individ_group_perms = \
                IndividualPermsGroupUserEditForm(request.POST)
            lists['form_individ_perms_group_user'] = form_individ_group_perms

            if form_individ_group_perms.is_valid():
                id = form_individ_group_perms.cleaned_data['id']
                read = form_individ_group_perms.cleaned_data['read']
                write = form_individ_group_perms.cleaned_data['write']
                change_config = form_individ_group_perms.\
                    cleaned_data['change_config']
                delete = form_individ_group_perms.cleaned_data['delete']

                data = {
                    'id': id,
                    'read': read,
                    'write': write,
                    'change_config': change_config,
                    'delete': delete
                }

                client.create_api_object_group_permission().update([data])

                messages.add_message(request, messages.SUCCESS,
                                     object_group_perm_messages.get("success_edit"))

                return redirect('user-group.list-perms-obj', id_ugroup, id_type_obj)

        else:

            data_search = {
                'start_record': 0,
                'end_record': 25,
                'asorting_cols': [],
                'searchable_columns': [],
                'extends_search': [{
                    'user_group': id_ugroup,
                    'object_type': id_type_obj,
                    'object_value': id_obj

                }]
            }
            kind = ['basic']
            fields = ['id', 'read', 'write', 'change_config', 'delete',
                      'user_group__details', 'object_type__details']

            try:
                perms = client.create_api_object_group_permission()\
                    .search(search=data_search, kind=kind, fields=fields)['ogps'][0]
            except IndexError:
                raise NetworkAPIClientError(u'Permission not found')

            lists['group_name'] = perms['user_group']['name']
            lists['object_type'] = perms['object_type']['name']

            lists['form_individ_perms_group_user'] = \
                IndividualPermsGroupUserEditForm(initial=perms)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('home')

    return render_to_response(USERGROUP_EDIT_INDIVIDUAL_PERMS, lists,
                              context_instance=RequestContext(request))


def edit_gen_perms_of_type_obj(request, id_ugroup, id_type_obj):

    try:
        lists = {}

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['id_ugroup'] = id_ugroup
        lists['id_type_obj'] = id_type_obj

        if request.method == 'POST':

            lists['group_name'] = client.create_grupo_usuario(). \
                search(id_ugroup)['user_group']['nome']
            lists['object_type'] = client.create_api_object_type(). \
                get([id_type_obj])['ots'][0]['name']

            form_gen_group_perms = GeneralPermsGroupUserEditForm(request.POST)
            lists['form_gen_perms_group_user'] = form_gen_group_perms

            if form_gen_group_perms.is_valid():
                id = form_gen_group_perms.cleaned_data['id']
                read = form_gen_group_perms.cleaned_data['read']
                write = form_gen_group_perms.cleaned_data['write']
                change_config = form_gen_group_perms.\
                    cleaned_data['change_config']
                delete = form_gen_group_perms.cleaned_data['delete']

                data = {
                    'read': read,
                    'write': write,
                    'change_config': change_config,
                    'delete': delete
                }

                if id is not None:
                    data['id'] = id
                    client.create_api_object_group_permission_general().\
                        update([data])

                else:
                    data['user_group'] = int(id_ugroup)
                    data['object_type'] = int(id_type_obj)

                    client.create_api_object_group_permission_general().\
                        create([data])

                messages.add_message(request,
                                     messages.SUCCESS,
                                     object_group_perm_gen_messages.get("success_edit"))

                return redirect('user-group.list', id_ugroup, 1)

        else:

            data_search = {
                'start_record': 0,
                'end_record': 25,
                'asorting_cols': [],
                'searchable_columns': [],
                'extends_search': [{
                    'user_group': id_ugroup,
                    'object_type': id_type_obj,
                }]
            }
            kind = ['basic']
            fields = ['id', 'read', 'write', 'change_config', 'delete',
                      'user_group__details', 'object_type__details']

            try:
                perms = client.create_api_object_group_permission_general() \
                    .search(search=data_search, kind=kind, fields=fields)['ogpgs'][0]

                lists['group_name'] = perms['user_group']['name']
                lists['object_type'] = perms['object_type']['name']

                lists['form_gen_perms_group_user'] = \
                    GeneralPermsGroupUserEditForm(initial=perms)

            except IndexError:
                lists['group_name'] = client.create_grupo_usuario(). \
                    search(id_ugroup)['user_group']['nome']
                lists['object_type'] = client.create_api_object_type(). \
                    get([id_type_obj])['ots'][0]['name']

                lists['form_gen_perms_group_user'] = \
                    GeneralPermsGroupUserEditForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('home')

    return render_to_response(USERGROUP_EDIT_GENERAL_PERMS, lists,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def create_individ_perms_of_object(request):

    try:

        lists = dict()

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        group_users = client.create_grupo_usuario().listar()['user_group']

        object_types = client.create_api_object_type().search()['ots']

        fields = {
            'user_group': group_users,
            'object_type': object_types
        }

        if request.method == 'POST':

            form_individ_group_perms = \
                IndividualPermsGroupUserCreateForm(fields, request.POST)
            lists['form_individ_perms_group_user'] = form_individ_group_perms

            lists['form_hidden_ids'] = HiddenIdsPermsForm(request.POST)

            if form_individ_group_perms.is_valid():
                read = form_individ_group_perms.cleaned_data['read']
                write = form_individ_group_perms.cleaned_data['write']
                change_config = form_individ_group_perms.\
                    cleaned_data['change_config']
                delete = form_individ_group_perms.cleaned_data['delete']

                user_group = form_individ_group_perms.cleaned_data['user_group']
                object_type = form_individ_group_perms.cleaned_data['object_type']
                object_value = form_individ_group_perms.cleaned_data['id_obj']

                data = {
                    'user_group': int(user_group),
                    'object_type': int(object_type),
                    'object_value': int(object_value),
                    'read': read,
                    'write': write,
                    'change_config': change_config,
                    'delete': delete
                }

                client.create_api_object_group_permission().create([data])

                messages.add_message(request,
                                     messages.SUCCESS,
                                     object_group_perm_messages.get("success_create"))

                return redirect('user-group.list-perms-obj', user_group, object_type)

        else:
            id_ugroup = group_users[0]['id']
            id_type_obj = object_types[0]['id']

            initial_form = {
                'user_group': int(id_ugroup),
                'object_type': int(id_type_obj)
            }

            lists['form_individ_perms_group_user'] = IndividualPermsGroupUserCreateForm(
                fields, initial=initial_form)

            initial_ids = {
                'id_ugroup': int(id_ugroup),
                'id_type_obj': int(id_type_obj)
            }

            lists['form_hidden_ids'] = HiddenIdsPermsForm(initial=initial_ids)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(USERGROUP_CREATE_INDIVIDUAL_PERMS, lists,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def delete_individ_perms_of_object(request):

    try:
        if request.method == 'POST':

            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            form = DeletePermsForm(request.POST)

            if form.is_valid():

                ids_perms = split_to_array(form.cleaned_data['ids_perms'])

                id_ugroup = form.cleaned_data['id_ugroup']
                id_type_obj = form.cleaned_data['id_type_obj']

                client.create_api_object_group_permission().delete(ids_perms)

                messages.add_message(
                    request, messages.SUCCESS, object_group_perm_messages.
                    get('success_delete'))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('user-group.list-perms-obj', id_ugroup, id_type_obj)


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def ajax_get_individual_permissions(request, id_ugroup, id_type_obj):

    try:
        # If form was submited
        if request.method == "GET":

            # Get user auth
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            column_index_name_map = {
                0: '',
                1: 'id',
                2: 'read',
                3: 'write',
                4: 'change_config',
                5: 'delete',
                6: ''
            }

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

            data_search = {
                'start_record': pagination.start_record,
                'end_record': pagination.end_record,
                'asorting_cols': pagination.asorting_cols,
                'searchable_columns': pagination.searchable_columns,
                'custom_search': pagination.custom_search,
                'extends_search': [{
                    'user_group': int(id_ugroup),
                    'object_type': int(id_type_obj)
                }]
            }

            kind = ['basic']
            fields = ['id', 'read', 'write', 'change_config', 'delete',
                      'object_value']

            perms = client. \
                create_api_object_group_permission(). \
                search(search=data_search, kind=kind, fields=fields)
            lists = dict()
            lists['id_ugroup'] = id_ugroup
            lists['id_type_obj'] = id_type_obj
            lists['type_obj'] = client.create_api_object_type().get(
                [id_type_obj])['ots'][0]['name']

            # Returns JSON
            return dtp.build_response(
                perms['ogps'],
                perms['total'],
                USERGROUP_AJAX_INDIVIDUAL_PERMISSIONS,
                request,
                lists
            )

    except NetworkAPIClientError, error:
        logger.error(error)
        return HttpResponseServerError(error, mimetype='application/javascript')
    except BaseException, error:
        logger.error(error)
        return HttpResponseServerError(error, mimetype='application/javascript')


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def ajax_get_objects(request):

    try:

        # If form was submited
        if request.method == "GET":

            # Get user auth
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            column_index_name_map = {
                0: '',
                1: 'id',
                2: 'name'
            }

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

            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            search = request.GET.get('search')

            if not search:
                raise Exception(u'Empty search')

            id_type_obj = [request.GET.get('id_type_obj')]

            type_obj = client.create_api_object_type(). \
                get(id_type_obj)['ots'][0]['name']

            lists = dict()
            if type_obj == VIPREQUEST_OBJ_TYPE:
                objs = facade.get_vips_request(client, search, pagination, None)

            elif type_obj == SERVERPOOL_OBJ_TYPE:
                objs = facade.get_server_pools(client, search, pagination, None)

            elif type_obj == VLAN_OBJ_TYPE:
                objs = facade.get_vlans(client, search, pagination, None)

            lists['type_obj'] = type_obj

            # Returns JSON
            return dtp.build_response(
                objs['objs'],
                objs['total'],
                templates.USERGROUP_AJAX_OBJECTS,
                request,
                lists
            )

    except NetworkAPIClientError, error:
        logger.error(error)
        return HttpResponseServerError(error, mimetype='application/javascript')
    except BaseException, error:
        logger.error(error)
        return HttpResponseServerError(error, mimetype='application/javascript')


def load_list(request, lists, id_ugroup, tab):

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        data_search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'user_group': id_ugroup

            }]
        }
        kind = ['details']
        fields = ['id', 'read', 'write', 'change_config', 'delete',
                  'user_group', 'object_type__details']
        lists['object_perms'] = client.\
            create_api_object_group_permission_general().\
            search(search=data_search, kind=kind, fields=fields)['ogpgs']

        fields = ['id', 'name']

        ots = map(lambda x: x['object_type'], lists['object_perms'])

        ots_all = client.create_api_object_type().search(fields=fields)['ots']

        for ot in ots_all:
            if ot not in ots:
                perm_fake = {'change_config': False, 'read': False, 'write': False,
                             'user_group': False, 'delete': False}
                perm_fake['object_type'] = ot
                perm_fake['id'] = ot['id']
                lists['object_perms'].append(perm_fake)

        lists['users'] = validates_dict(
            client.create_usuario().list_by_group(id_ugroup), 'users')

        if 'ugroup' not in lists:
            lists['ugroup'] = client.create_grupo_usuario().search(
                id_ugroup).get('user_group')

        if 'form_users' not in lists:
            lists['form_users'] = UserGroupForm(
                client.create_usuario().list_by_group_out(id_ugroup))

        lists['perms'] = validates_dict(
            client.create_permissao_administrativa().list_by_group(id_ugroup),
            'perms')

        if 'form_perms' not in lists:
            function_list = validates_dict(
                client.create_permission().list_all(), 'perms')
            lists['form_perms'] = PermissionGroupForm(function_list)

        if 'action_edit_perms' not in lists:
            lists['action_edit_perms'] = reverse(
                "user-group-perm.form", args=[id_ugroup])

        lists['form'] = DeleteForm()
        lists['form_aux'] = DeleteFormAux()
        lists['tab'] = '0' if tab == '0' else '1' if tab == '1' else '2'

        lists['action_new_users'] = reverse(
            "user-group.form", args=[id_ugroup])
        lists['action_new_perms'] = reverse(
            "user-group-perm.form", args=[id_ugroup])

        lists['cadperms'] = parse_cad_perms(PATH_PERMLISTS + "/cadperms.txt")
        lists['apiperms'] = parse_api_perms(PATH_PERMLISTS + "/apiperms.txt")

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return lists


def convert_array(a):
    return a['object_type']


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def list_all(request, id_ugroup, tab):
    return render_to_response(USERGROUP_LIST, load_list(request, dict(), id_ugroup, tab), context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True}])
def delete_user(request, id_ugroup):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_ugroup = auth.get_clientFactory().create_usuario_grupo()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each users selected to remove
            for id_user in ids:
                try:

                    # Execute in NetworkAPI
                    client_ugroup.remover(id_user, id_ugroup)

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(
                    request, messages.ERROR, error_messages.get("can_not_remove_all"))

            # If cant remove someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = error_messages.get("can_not_remove") % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all has ben removed
            elif have_errors is False:
                messages.add_message(
                    request, messages.SUCCESS, user_group_messages.get("success_remove"))

            else:
                messages.add_message(
                    request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('user-group.list', id_ugroup, 0)


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def add_form_user(request, id_ugroup):

    try:

        lists = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get Group User by ID from NetworkAPI
        lists['ugroup'] = client.create_grupo_usuario().search(
            id_ugroup).get('user_group')

        if request.method == "POST":

            form = UserGroupForm(
                client.create_usuario().list_by_group_out(id_ugroup), request.POST)
            lists['form_users'] = form

            if form.is_valid():

                user_list = form.cleaned_data['users']

                try:

                    client_ugroup = client.create_usuario_grupo()

                    for id_user in user_list:
                        client_ugroup.inserir(id_user, id_ugroup)

                    messages.add_message(
                        request, messages.SUCCESS, user_group_messages.get("success_insert"))

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
            else:
                lists['open_form'] = str(True)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists = load_list(request, lists, id_ugroup, '0')

    return render_to_response(USERGROUP_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def delete_perm(request, id_ugroup):

    if request.method == 'POST':

        form = DeleteFormAux(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_perm = auth.get_clientFactory(
            ).create_permissao_administrativa()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids_aux'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each perms selected to remove
            for id_perm in ids:
                try:

                    # Execute in NetworkAPI
                    client_perm.remover(id_perm)

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(
                    request, messages.ERROR, error_messages.get("can_not_remove_all"))

            # If cant remove someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = error_messages.get("can_not_remove") % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all has ben removed
            elif have_errors is False:
                messages.add_message(
                    request, messages.SUCCESS, perm_group_messages.get("success_remove"))

            else:
                messages.add_message(
                    request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('user-group.list', id_ugroup, 1)


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def add_form_perm(request, id_ugroup):

    try:

        lists = dict()

        # Get user
        auth = AuthSession(request.session)
        client_perm = auth.get_clientFactory(
        ).create_permissao_administrativa()

        # Get Group User by ID from NetworkAPI
        lists['ugroup'] = auth.get_clientFactory().create_grupo_usuario().search(
            id_ugroup).get('user_group')

        function_list = validates_dict(
            auth.get_clientFactory().create_permission().list_all(), 'perms')

        if request.method == "POST":

            form = PermissionGroupForm(function_list, request.POST)
            lists['form_perms'] = form

            if form.is_valid():

                function = form.cleaned_data['function']
                read = convert_boolean_to_int(form.cleaned_data['read'])
                write = convert_boolean_to_int(form.cleaned_data['write'])

                client_perm.inserir(function, read, write, id_ugroup)

                messages.add_message(
                    request, messages.SUCCESS, perm_group_messages.get("success_insert"))

                return redirect('user-group.list', id_ugroup, 1)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists['open_form'] = str(True)
    lists = load_list(request, lists, id_ugroup, '1')

    return render_to_response(USERGROUP_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def edit_form_perm(request, id_ugroup, id_perm):

    try:

        lists = dict()
        lists['edit_perms'] = True
        lists['action_edit_perms'] = reverse(
            "user-group-perm.edit", args=[id_ugroup, id_perm])

        # Get user
        auth = AuthSession(request.session)
        client_perm = auth.get_clientFactory(
        ).create_permissao_administrativa()

        # Get Group User by ID from NetworkAPI
        lists['ugroup'] = auth.get_clientFactory().create_grupo_usuario().search(
            id_ugroup).get('user_group')

        function_list = validates_dict(
            auth.get_clientFactory().create_permission().list_all(), 'perms')

        perm = client_perm.search(id_perm).get("perm")

        if request.method == "POST":

            form = PermissionGroupForm(function_list, request.POST)
            lists['form_perms'] = form

            if form.is_valid():

                id_perm = form.cleaned_data['id_group_perms']
                function = form.cleaned_data['function']
                read = convert_boolean_to_int(form.cleaned_data['read'])
                write = convert_boolean_to_int(form.cleaned_data['write'])

                client_perm.alterar(id_perm, function, read, write, id_ugroup)

                messages.add_message(
                    request, messages.SUCCESS, perm_group_messages.get("success_edit"))

                return redirect('user-group.list', id_ugroup, 1)

        # GET
        else:
            initial = {"id_group_perms": perm.get("id"), "function": perm.get("permission"), "read": convert_string_to_boolean(
                perm.get("leitura")), "write": convert_string_to_boolean(perm.get("escrita"))}
            lists['form_perms'] = PermissionGroupForm(
                function_list, initial=initial)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists['open_form'] = str(True)
    lists = load_list(request, lists, id_ugroup, '1')

    return render_to_response(USERGROUP_LIST, lists, context_instance=RequestContext(request))
