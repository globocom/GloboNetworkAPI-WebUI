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
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from networkapiclient.exception import AmbienteError, AmbienteNaoExisteError, \
    DataBaseError, \
    DetailedEnvironmentError
from networkapiclient.exception import InvalidParameterError, \
    NetworkAPIClientError, XMLError
from networkapiclient.Pagination import Pagination

from CadVlan import templates
from CadVlan.Acl.acl import get_templates
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Environment.forms import AmbienteForm, AmbienteLogicoForm, \
    DivisaoDCForm, Grupol3Form, IpConfigForm
from CadVlan.forms import DeleteForm
from CadVlan.messages import environment_messages
from CadVlan.permissions import ENVIRONMENT_MANAGEMENT
from CadVlan.templates import AJAX_AUTOCOMPLETE_LIST, ENVIRONMENT_FORM, \
    ENVIRONMENT_LIST, AJAX_CHILDREN_ENV
from CadVlan.Util.Decorators import has_perm, log, login_required
from CadVlan.Util.git import GITCommandError
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.Util.utility import DataTablePaginator

logger = logging.getLogger(__name__)


def ajax_view_env(request, env_id):
    """
    :param request:
    :return:
    """

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(AJAX_CHILDREN_ENV, lists,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True}])
def ajax_list_all(request, search_term=None):
    """
    :param request:
    :return: 
    """

    try:

        lists = dict()
        lists['form'] = DeleteForm()

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        column_index_name_map = {
            0: '',
            1: 'id',
            2: 'divisao_dc__nome',
            3: 'vrf',
            4: 'dcroom__dc__dcname',
            5: ''
        }

        dtp = DataTablePaginator(request, column_index_name_map)

        dtp.build_server_side_list()

        dtp.searchable_columns = [
            'grupo_l3__nome',
            'ambiente_logico__nome',
            'divisao_dc__nome',
            'vrf',
            'dcroom__dc__dcname',
            'dcroom__name'
        ]

        dtp.end_record = 10000

        fields = [
            "divisao_dc__nome__icontains",
            "ambiente_logico__nome__icontains",
            "grupo_l3__nome__icontains"
        ]

        extends_search_dict = dict()

        if search_term:
            term = search_term.split("+")
            term_len = len(term)
            if term_len > 1:
                for i in xrange(len(term)):
                    extends_search_dict.update({fields[i]: term[i]})
            else:
                dtp.custom_search = term[0]

        pagination = Pagination(
            dtp.start_record,
            dtp.end_record,
            dtp.asorting_cols,
            dtp.searchable_columns,
            dtp.custom_search
        )

        data = dict()
        data["start_record"] = pagination.start_record
        data["end_record"] = pagination.end_record
        data["asorting_cols"] = ['divisao_dc__nome',
                                 'ambiente_logico__nome',
                                 'grupo_l3__nome']
        data["searchable_columns"] = pagination.searchable_columns
        data["custom_search"] = pagination.custom_search or ""
        data["extends_search"] = [extends_search_dict] if extends_search_dict else []

        environment = client.create_api_environment().search(fields=['id',
                                                                     'children__basic',
                                                                     'vrf',
                                                                     'name',
                                                                     'configs__details',
                                                                     'dcroom__details'],
                                                             search=data)

        lists['envs'] = json.dumps(environment.get("environments"))

        return render_to_response(ENVIRONMENT_LIST, lists,
                                  context_instance=RequestContext(request))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True}])
def list_all(request):
    """
    :param request:
    :return:
    """

    lists = dict()

    try:

        lists['form'] = DeleteForm()
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        column_index_name_map = {
            0: '',
            1: 'id',
            2: 'divisao_dc__nome',
            3: 'vrf',
            4: 'dcroom__dc__dcname',
            5: ''
        }

        dtp = DataTablePaginator(request, column_index_name_map)

        dtp.build_server_side_list()

        dtp.searchable_columns = [
            'grupo_l3__nome',
            'ambiente_logico__nome',
            'divisao_dc__nome',
            'vrf',
            'dcroom__dc__dcname',
            'dcroom__name'
        ]

        dtp.end_record = 10000

        pagination = Pagination(
            dtp.start_record,
            dtp.end_record,
            dtp.asorting_cols,
            dtp.searchable_columns,
            dtp.custom_search
        )

        extends_search = dict()
        extends_search["father_environment__isnull"] = True

        data = dict()
        data["start_record"] = pagination.start_record
        data["end_record"] = pagination.end_record
        data["asorting_cols"] = ['divisao_dc__nome',
                                 'ambiente_logico__nome',
                                 'grupo_l3__nome']
        data["searchable_columns"] = pagination.searchable_columns
        data["custom_search"] = pagination.custom_search or ""
        data["extends_search"] = [extends_search] if extends_search else []

        environment = client.create_api_environment().search(fields=['id',
                                                                     'children__basic',
                                                                     'vrf',
                                                                     'name',
                                                                     'configs__details',
                                                                     'vxlan'],
                                                             search=data)

        lists['envs'] = json.dumps(environment.get("environments"))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    return render_to_response(ENVIRONMENT_LIST, lists,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True,
            "write": True}])
def remove_environment(request, environment_id=None):
    """
    :param request:
    :return:
    """

    ids = list()
    error_not_found = list()
    error_associated = list()
    have_errors = False

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    if environment_id:
        env_id = int(environment_id)
    else:
        ids = request.POST.getlist('ids[]')
        env_id = ';'.join(str(id) for id in ids)

    try:
        client.create_api_environment().delete_environment(env_id)
    except DetailedEnvironmentError as e:
        # Detailed message for VLAN errors
        logger.error(e)
        have_errors = True
        messages.add_message(request, messages.ERROR, e)
    except AmbienteNaoExisteError as e:
        # Environment doesn't exist.
        logger.error(e)
        have_errors = True
        error_not_found.append(ids)
    except AmbienteError as e:
        # Environment associated to equipment and/or VLAN that
        # couldn't be removed.
        logger.error(e)
        have_errors = True
        error_associated.append(ids)
    except InvalidParameterError as e:
        # Environment id is null or invalid.
        logger.error(e)
        have_errors = True
        messages.add_message(
            request, messages.ERROR, environment_messages.get("invalid_id"))
    except DataBaseError as e:
        # NetworkAPI fail to access database.
        logger.error(e)
        have_errors = True
        messages.add_message(request, messages.ERROR, e)
    except XMLError as e:
        # NetworkAPI fail generating XML response.
        logger.error(e)
        have_errors = True
        messages.add_message(request, messages.ERROR, e)
    except Exception as e:
        # Other errors
        logger.error(e)
        have_errors = True
        messages.add_message(request, messages.ERROR, e)

    # Build not found message
    if len(error_not_found) > 0:
        msg = ''
        for id_error in error_not_found[0:-1]:
            msg = msg + id_error + ','
        if len(error_not_found) > 1:
            msg = msg[:-1] + ' e ' + error_not_found[-1]
        else:
            msg = error_not_found[0]

        msg = environment_messages.get("env_not_found") % msg
        messages.add_message(request, messages.ERROR, msg)

    # Build associated error message
    if len(error_associated) > 0:
        msg = ''
        for id_error in error_associated[0:-1]:
            msg = msg + id_error + ','
        if len(error_associated) > 1:
            msg = msg[:-1] + ' e ' + error_associated[-1]
        else:
            msg = error_associated[0]

        msg = environment_messages.get("env_associated") % msg
        messages.add_message(request, messages.ERROR, msg)

    # Success message
    if not have_errors:
        messages.add_message(
            request, messages.SUCCESS,
            environment_messages.get("success_delete_all"))

    return redirect('environment.list')


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True,
            "write": True}])
def ajax_autocomplete_acl_path(request):
    """
    :param request:
    :return:
    """

    path_list = dict()

    try:
        # Get user auth
        auth = AuthSession(request.session)
        environment = auth.get_clientFactory().create_ambiente()

        paths = environment.list_acl_path().get(
            "acl_paths") if environment.list_acl_path() else list()
        path_list['list'] = paths

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(AJAX_AUTOCOMPLETE_LIST, path_list,
                                   context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True,
            "write": True}])
def add_configuration(request, id_environment):
    """
    :param request:
    :return:
    """

    context = dict()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        net_type_list = client.create_tipo_rede().listar()

        form = IpConfigForm(net_type_list, request.POST or None)

        # Get user auth
        auth = AuthSession(request.session)
        environment_client = auth.get_clientFactory().create_ambiente()

        environment_dict = environment_client.buscar_por_id(id_environment)
        environment = environment_dict.get('ambiente')

        context["form"] = form
        context["action"] = reverse(
            'environment.configuration.add', args=[id_environment])
        context["environment"] = environment

        if form.is_valid():
            network = form.cleaned_data['network_validate']
            prefix = form.cleaned_data['prefix']
            ip_version = form.cleaned_data['ip_version']
            network_type = form.cleaned_data['net_type']

            environment_client.configuration_save(
                id_environment, network, prefix, ip_version, network_type)
            messages.add_message(request, messages.SUCCESS,
                                 environment_messages.get(
                                     "success_configuration_insert"))
            context["form"] = IpConfigForm(net_type_list)

    except AmbienteNaoExisteError as e:
        messages.add_message(request, messages.ERROR, e)
        return redirect('environment.list')

    except InvalidParameterError as e:
        messages.add_message(request, messages.ERROR, e)

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(templates.ENVIRONMENT_CIDR, context,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True,
            "write": True}])
def remove_configuration(request, environment_id, configuration_id):
    """
    :param request:
    :return:
    """

    try:

        auth = AuthSession(request.session)
        environment_client = auth.get_clientFactory().create_api_environment_cidr()

        environment_client.delete(cidr_id=[configuration_id])

        messages.add_message(request,
                             messages.SUCCESS,
                             environment_messages.get(
                                 "success_configuration_remove"))

        return redirect('environment.edit', environment_id)

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('environment.list')


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True,
            "write": True}])
def insert_ambiente(request):
    """
    :param request:
    :return:
    """

    # lists = dict()
    # config_forms = list()
    #
    # try:
    #
    #     # Get User
    #     auth = AuthSession(request.session)
    #     client = auth.get_clientFactory()
    #
    #     # Get all needs from NetworkAPI
    #     env_logic = client.create_ambiente_logico().listar()
    #     division_dc = client.create_divisao_dc().listar()
    #     group_l3 = client.create_grupo_l3().listar()
    #     filters = client.create_filter().list_all()
    #     try:
    #         templates = get_templates(auth.get_user(), True)
    #     except GITCommandError as e:
    #         logger.error(e)
    #         messages.add_message(request, messages.ERROR, e)
    #         templates = {
    #             'ipv4': list(),
    #             'ipv6': list()
    #         }
    #
    #     ipv4 = templates.get("ipv4")
    #     ipv6 = templates.get("ipv6")
    #     envs = client.create_ambiente().listar().get('ambiente')
    #     vrfs = client.create_api_vrf().search()['vrfs']
    #     # Forms
    #     lists['ambiente'] = AmbienteForm(
    #         env_logic, division_dc, group_l3, filters, ipv4, ipv6, envs, vrfs)
    #     lists['divisaodc_form'] = DivisaoDCForm()
    #     lists['grupol3_form'] = Grupol3Form()
    #     lists['ambientelogico_form'] = AmbienteLogicoForm()
    #
    #     lists['action'] = reverse("environment.form")
    #
    #     # If form was submited
    #     if request.method == 'POST':
    #
    #         # Set data in form
    #         ambiente_form = AmbienteForm(
    #             env_logic, division_dc, group_l3, filters, ipv4, ipv6, envs, vrfs, request.POST)
    #
    #         # Return data to form in case of error
    #         lists['ambiente'] = ambiente_form
    #
    #         # Validate
    #         if ambiente_form.is_valid():
    #
    #             divisao_dc = ambiente_form.cleaned_data['divisao']
    #             ambiente_logico = ambiente_form.cleaned_data['ambiente_logico']
    #             grupo_l3 = ambiente_form.cleaned_data['grupol3']
    #             filter_ = ambiente_form.cleaned_data['filter']
    #             link = ambiente_form.cleaned_data['link']
    #             acl_path = ambiente_form.cleaned_data['acl_path']
    #             vrf = ambiente_form.cleaned_data['vrf']
    #             if str(vrf) == str(None):
    #                 vrf = None
    #             father_environment = ambiente_form.cleaned_data['father_environment']
    #
    #             ipv4_template = ambiente_form.cleaned_data.get(
    #                 'ipv4_template', None)
    #             ipv6_template = ambiente_form.cleaned_data.get(
    #                 'ipv6_template', None)
    #
    #             min_num_vlan_1 = ambiente_form.cleaned_data.get(
    #                 'min_num_vlan_1', None)
    #             max_num_vlan_1 = ambiente_form.cleaned_data.get(
    #                 'max_num_vlan_1', None)
    #             min_num_vlan_2 = ambiente_form.cleaned_data.get(
    #                 'min_num_vlan_2', None)
    #             max_num_vlan_2 = ambiente_form.cleaned_data.get(
    #                 'max_num_vlan_2', None)
    #
    #             vrf_internal = dict(ambiente_form.fields['vrf'].choices)[int(vrf)]
    #
    #             # Business
    #             dict_env = {
    #                 "id": None,
    #                 "grupo_l3": int(grupo_l3),
    #                 "ambiente_logico": int(ambiente_logico),
    #                 "divisao_dc": int(divisao_dc),
    #                 "filter": int(filter_) if filter_ else None,
    #                 "acl_path": acl_path,
    #                 "ipv4_template": ipv4_template,
    #                 "ipv6_template": ipv6_template,
    #                 "link": link,
    #                 "min_num_vlan_1": min_num_vlan_1,
    #                 "max_num_vlan_1": max_num_vlan_1,
    #                 "min_num_vlan_2": min_num_vlan_2,
    #                 "max_num_vlan_2": max_num_vlan_2,
    #                 "default_vrf": int(vrf),
    #                 "father_environment": int(father_environment) if father_environment else None,
    #                 'vrf': vrf_internal
    #             }
    #             client.create_api_environment().create_environment(dict_env)
    #             messages.add_message(
    #                 request, messages.SUCCESS, environment_messages.get("success_insert"))
    #
    #             return redirect('environment.list')
    #
    #         else:
    #             # If invalid, send all error messages in fields
    #             lists['ambiente'] = ambiente_form
    #
    #     auth = AuthSession(request.session)
    #     client = auth.get_clientFactory()
    #     net_type_list = client.create_tipo_rede().listar()
    #
    #     config_forms.append(IpConfigForm(net_type_list))
    #
    #     lists['config_forms'] = config_forms
    #
    # except NetworkAPIClientError as e:
    #     logger.error(e)
    #     messages.add_message(request, messages.ERROR, e)
    #
    # return render_to_response(ENVIRONMENT_FORM, lists,
    # context_instance=RequestContext(request))
    return HttpResponseBadRequest("Bad request. Example: "
                                  "/environment/form/environment_id/.",
                                  status=400)

@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True,
            "write": True}])
def edit(request, id_environment):
    """
    :param request:
    :return:
    """

    lists = dict()

    try:

        # Get User
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        data = {
            "start_record": 0,
            "end_record": 1000,
            "asorting_cols": ["nome"],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }
        env_logic = client.create_api_environment_logic().search(search=data)
        division_dc = client.create_api_environment_dc().search(search=data)
        group_l3 = client.create_api_environment_l3().search(search=data)
        filters = client.create_filter().list_all()

        cidr = client.create_api_environment_cidr().\
            get_by_env(env_id=[id_environment])

        lists['configurations_prefix'] = cidr.get('cidr')

        try:
            templates = get_templates(auth.get_user(), True)
        except GITCommandError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            templates = {
                'ipv4': list(),
                'ipv6': list()
            }

        ipv4 = templates.get("ipv4")
        ipv6 = templates.get("ipv6")

        envs = client.create_ambiente().listar().get('ambiente')
        vrfs = client.create_api_vrf().search()['vrfs']

        try:
            env = client.create_api_environment().get_environment(id_environment)
            env = env.get("environments")[0]
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')

        lists['id_environment'] = env.get("id")

        # Set Environment data
        initial = {
            "id_env": env.get("id"),
            "divisao": env.get("divisao_dc"),
            "ambiente_logico": env.get("ambiente_logico"),
            "grupol3": env.get("grupo_l3"),
            "filter": env.get("filter"),
            "acl_path": env.get("acl_path"),
            "ipv4_template": env.get("ipv4_template"),
            "ipv6_template": env.get("ipv6_template"),
            "min_num_vlan_1": env.get("min_num_vlan_1"),
            "max_num_vlan_1": env.get("max_num_vlan_1"),
            "min_num_vlan_2": env.get("min_num_vlan_2"),
            "max_num_vlan_2": env.get("max_num_vlan_2"),
            'link': env.get('link'),
            'father_environment': env.get('father_environment'),
            'vrf': env.get('default_vrf'),
            'vxlan': 1 if env.get('vxlan') else 0
        }

        env_form = AmbienteForm(
            env_logic, division_dc, group_l3, filters, ipv4, ipv6, envs, vrfs, initial=initial)

        # Forms
        lists['ambiente'] = env_form
        lists['vxlan'] = env.get('vxlan', False)
        lists['divisaodc_form'] = DivisaoDCForm(
            initial={"id_env": id_environment}
        )
        lists['grupol3_form'] = Grupol3Form(initial={"id_env": id_environment})
        lists['ambientelogico_form'] = AmbienteLogicoForm(
            initial={"id_env": id_environment})
        lists['action'] = reverse("environment.edit", args=[id_environment])

        # If form was submited
        if request.method == 'POST':

            # Set data in form
            ambiente_form = AmbienteForm(
                env_logic, division_dc, group_l3, filters, ipv4, ipv6, envs, vrfs, request.POST)

            # Return data to form in case of error
            lists['ambiente'] = ambiente_form

            vxlan = True if request.POST.get('is_vxlan') else False

            # Validate
            if ambiente_form.is_valid():

                id_env = ambiente_form.cleaned_data['id_env']
                divisao_dc = ambiente_form.cleaned_data['divisao']
                ambiente_logico = ambiente_form.cleaned_data['ambiente_logico']
                grupo_l3 = ambiente_form.cleaned_data['grupol3']
                filter_ = ambiente_form.cleaned_data['filter']
                link = ambiente_form.cleaned_data['link']
                vrf = ambiente_form.cleaned_data['vrf']
                acl_path = ambiente_form.cleaned_data['acl_path']
                father_environment = ambiente_form.cleaned_data['father_environment']

                ipv4_template = ambiente_form.cleaned_data.get(
                    'ipv4_template', None)
                ipv6_template = ambiente_form.cleaned_data.get(
                    'ipv6_template', None)

                min_num_vlan_1 = ambiente_form.cleaned_data.get(
                    'min_num_vlan_1', None)
                max_num_vlan_1 = ambiente_form.cleaned_data.get(
                    'max_num_vlan_1', None)
                min_num_vlan_2 = ambiente_form.cleaned_data.get(
                    'min_num_vlan_2', None)
                max_num_vlan_2 = ambiente_form.cleaned_data.get(
                    'max_num_vlan_2', None)

                vrf_internal = dict(ambiente_form.fields['vrf'].choices)[int(vrf)]

                # Business
                dict_env = {
                    "id": int(id_env),
                    "grupo_l3": int(grupo_l3),
                    "ambiente_logico": int(ambiente_logico),
                    "divisao_dc": int(divisao_dc),
                    "filter": int(filter_) if filter_ else None,
                    "acl_path": acl_path,
                    "ipv4_template": ipv4_template,
                    "ipv6_template": ipv6_template,
                    "link": link,
                    "min_num_vlan_1": min_num_vlan_1,
                    "max_num_vlan_1": max_num_vlan_1,
                    "min_num_vlan_2": min_num_vlan_2,
                    "max_num_vlan_2": max_num_vlan_2,
                    "default_vrf": int(vrf),
                    "father_environment": int(father_environment) if father_environment else None,
                    'vrf': vrf_internal,
                    'vxlan': vxlan
                }
                client.create_api_environment().update_environment(dict_env, id_env)

                messages.add_message(
                    request, messages.SUCCESS, environment_messages.get("success_edit"))

                return redirect('environment.list')

            else:
                # If invalid, send all error messages in fields
                lists['ambiente'] = ambiente_form

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True,
            "write": True}])
def insert_grupo_l3(request):
    """
    :param request:
    :return:
    """

    lists = dict()
    id_env = None

    if request.method == 'POST':

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['grupol3_form'] = Grupol3Form()
        grupo_l3_form = Grupol3Form(request.POST)

        try:
            id_env = request.POST['id_env']

            if grupo_l3_form.is_valid():
                nome_grupo_l3 = grupo_l3_form.cleaned_data['nome']
                env = dict(name=nome_grupo_l3.upper())

                client.create_api_environment_l3().create([env])
                messages.add_message(
                    request, messages.SUCCESS, environment_messages.get(
                        "grupo_l3_sucess"))

            else:
                # If invalid, send all error messages in fields
                lists['grupol3_form'] = grupo_l3_form

        except NetworkAPIClientError as e:
            logger.error(e)
            lists['grupol3_form'] = grupo_l3_form
            messages.add_message(request, messages.ERROR, e)

        try:
            data = {
                "start_record": 0,
                "end_record": 1000,
                "asorting_cols": ["nome"],
                "searchable_columns": [],
                "custom_search": "",
                "extends_search": []
            }
            env_logic = client.create_api_environment_logic().search(search=data)
            division_dc = client.create_api_environment_dc().search(search=data)
            group_l3 = client.create_api_environment_l3().search(search=data)
            filters = client.create_filter().list_all()

            try:
                templates = get_templates(auth.get_user(), True)
            except GITCommandError as e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                templates = {
                    'ipv4': list(),
                    'ipv6': list()
                }

            ipv4 = templates.get("ipv4")
            ipv6 = templates.get("ipv6")
            envs = client.create_ambiente().listar().get('ambiente')
            vrfs = client.create_api_vrf().search()['vrfs']
            # Forms
            env_form = AmbienteForm(
                env_logic, division_dc, group_l3, filters, ipv4, ipv6, envs, vrfs)
            div_form = DivisaoDCForm()
            amb_form = AmbienteLogicoForm()
            action = reverse("environment.form")

            # If id_env is set, still in edit
            if id_env:
                env = client.create_ambiente().buscar_por_id(id_env)
                env = env.get("ambiente")

                # Set Environment data
                initial = {"id_env": env.get("id"),
                           "divisao": env.get("id_divisao"),
                           "ambiente_logico": env.get("id_ambiente_logico"),
                           "grupol3": env.get("id_grupo_l3"),
                           "filter": env.get("id_filter"),
                           "link": env.get("link")}
                env_form = AmbienteForm(
                    env_logic, division_dc, group_l3, filters, ipv4, ipv6,
                    envs, vrfs, initial=initial)
                div_form = DivisaoDCForm(initial={"id_env": id_env})
                amb_form = AmbienteLogicoForm(initial={"id_env": id_env})
                action = reverse("environment.edit", args=[id_env])

            lists['ambiente'] = env_form
            lists['divisaodc_form'] = div_form
            lists['ambientelogico_form'] = amb_form
            lists['action'] = action

            return render_to_response(ENVIRONMENT_FORM, lists,
                                      context_instance=RequestContext(request))

        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')

    else:
        return redirect("environment.form")


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True,
            "write": True}])
def insert_divisao_dc(request):
    """
    :param request:
    :return:
    """

    lists = dict()
    id_env = None

    if request.method == 'POST':

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['divisaodc_form'] = DivisaoDCForm()
        divisao_dc_form = DivisaoDCForm(request.POST)

        try:
            id_env = request.POST['id_env']

            if divisao_dc_form.is_valid():

                nome_divisao_dc = divisao_dc_form.cleaned_data['nome']

                env = dict(name=nome_divisao_dc.upper())

                client.create_api_environment_dc().create([env])
                messages.add_message(
                    request, messages.SUCCESS, environment_messages.get(
                        "divisao_dc_sucess"))

            else:
                # If invalid, send all error messages in fields
                lists['divisaodc_form'] = divisao_dc_form

        except (NetworkAPIClientError, GITCommandError) as e:
            logger.error(e)
            lists['divisaodc_form'] = divisao_dc_form
            messages.add_message(request, messages.ERROR, e)

        try:
            data = {
                "start_record": 0,
                "end_record": 1000,
                "asorting_cols": ["nome"],
                "searchable_columns": [],
                "custom_search": "",
                "extends_search": []
            }
            env_logic = client.create_api_environment_logic().search(search=data)
            division_dc = client.create_api_environment_dc().search(search=data)
            group_l3 = client.create_api_environment_l3().search(search=data)
            filters = client.create_filter().list_all()
            try:
                templates = get_templates(auth.get_user(), True)
            except GITCommandError as e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                templates = {
                    'ipv4': list(),
                    'ipv6': list()
                }

            ipv4 = templates.get("ipv4")
            ipv6 = templates.get("ipv6")
            envs = client.create_ambiente().listar().get('ambiente')
            vrfs = client.create_api_vrf().search()['vrfs']

            # Forms
            env_form = AmbienteForm(
                env_logic, division_dc, group_l3, filters, ipv4, ipv6, envs, vrfs)
            gro_form = Grupol3Form()
            amb_form = AmbienteLogicoForm()
            action = reverse("environment.form")

            # If id_env is set, still in edit
            if id_env:
                env = client.create_ambiente().buscar_por_id(id_env)
                env = env.get("ambiente")

                # Set Environment data
                initial = {"id_env": env.get("id"),
                           "divisao": env.get("id_divisao"),
                           "ambiente_logico": env.get("id_ambiente_logico"),
                           "grupol3": env.get("id_grupo_l3"),
                           "filter": env.get("id_filter"),
                           "link": env.get("link")}
                env_form = AmbienteForm(
                    env_logic, division_dc, group_l3, filters, ipv4, ipv6,
                    envs, vrfs, initial=initial)
                gro_form = Grupol3Form(initial={"id_env": id_env})
                amb_form = AmbienteLogicoForm(initial={"id_env": id_env})
                action = reverse("environment.edit", args=[id_env])

            lists['ambiente'] = env_form
            lists['grupol3_form'] = gro_form
            lists['ambientelogico_form'] = amb_form
            lists['action'] = action

            return render_to_response(ENVIRONMENT_FORM, lists,
                                      context_instance=RequestContext(request))

        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')

    else:
        return redirect("environment.form")


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT,
            "read": True,
            "write": True}])
def insert_ambiente_logico(request):
    """
    :param request:
    :return:
    """

    lists = dict()
    id_env = None

    if request.method == 'POST':

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['ambientelogico_form'] = AmbienteLogicoForm()
        ambiente_logico_form = AmbienteLogicoForm(request.POST)

        try:
            id_env = request.POST['id_env']

            if ambiente_logico_form.is_valid():

                nome_ambiente_logico = ambiente_logico_form.cleaned_data['nome']
                env = dict(name=nome_ambiente_logico.upper())
                client.create_api_environment_logic().create([env])

                messages.add_message(
                    request, messages.SUCCESS, environment_messages.get(
                        "ambiente_log_sucess"))
            else:
                # If invalid, send all error messages in fields
                lists['ambientelogico_form'] = ambiente_logico_form

        except NetworkAPIClientError as e:
            logger.error(e)
            lists['ambientelogico_form'] = ambiente_logico_form
            messages.add_message(request, messages.ERROR, e)

        try:
            data = {
                "start_record": 0,
                "end_record": 1000,
                "asorting_cols": ["nome"],
                "searchable_columns": [],
                "custom_search": "",
                "extends_search": []
            }
            env_logic = client.create_api_environment_logic().search(search=data)
            division_dc = client.create_api_environment_dc().search(search=data)
            group_l3 = client.create_api_environment_l3().search(search=data)
            filters = client.create_filter().list_all()
            try:
                templates = get_templates(auth.get_user(), True)
            except GITCommandError as e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                templates = {
                    'ipv4': list(),
                    'ipv6': list()
                }

            ipv4 = templates.get("ipv4")
            ipv6 = templates.get("ipv6")
            envs = client.create_ambiente().listar().get('ambiente')
            vrfs = client.create_api_vrf().search()['vrfs']

            # Forms
            env_form = AmbienteForm(
                env_logic, division_dc, group_l3, filters, ipv4, ipv6,
                envs, vrfs)
            div_form = DivisaoDCForm()
            gro_form = Grupol3Form()
            action = reverse("environment.form")

            # If id_env is set, still in edit
            if id_env:
                env = client.create_ambiente().buscar_por_id(id_env)
                env = env.get("ambiente")

                # Set Environment data
                initial = {"id_env": env.get("id"),
                           "divisao": env.get("id_divisao"),
                           "ambiente_logico": env.get("id_ambiente_logico"),
                           "grupol3": env.get("id_grupo_l3"),
                           "filter": env.get("id_filter"),
                           "link": env.get("link")}
                env_form = AmbienteForm(
                    env_logic, division_dc, group_l3, filters, ipv4, ipv6,
                    envs, vrfs, initial=initial)
                div_form = DivisaoDCForm(initial={"id_env": id_env})
                gro_form = Grupol3Form(initial={"id_env": id_env})
                action = reverse("environment.edit", args=[id_env])

            lists['ambiente'] = env_form
            lists['divisaodc_form'] = div_form
            lists['grupol3_form'] = gro_form
            lists['action'] = action

            return render_to_response(ENVIRONMENT_FORM, lists,
                                      context_instance=RequestContext(request))

        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')

    else:
        return redirect("environment.form")
