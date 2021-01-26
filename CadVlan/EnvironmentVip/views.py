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
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.EnvironmentVip.form import EnvironmentVipForm
from CadVlan.forms import DeleteForm
from CadVlan.messages import environment_vip_messages
from CadVlan.messages import error_messages
from CadVlan.permissions import ENVIRONMENT_VIP
from CadVlan.templates import ENVIRONMENTVIP_CONF_FORM
from CadVlan.templates import ENVIRONMENTVIP_EDIT
from CadVlan.templates import ENVIRONMENTVIP_FORM
from CadVlan.templates import ENVIRONMENTVIP_LIST
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.Decorators import has_perm
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_VIP, "read": True}])
def list_all(request):

    environment_vip_list = dict()

    # Get user
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        # Get all environment vips from NetworkAPI
        environment_vip_list = client.create_environment_vip().list_all()

        for environment_vip in environment_vip_list.get("environment_vip"):
            environment_vip['is_more'] = str(False)
            option_vip = client.create_option_vip().get_option_vip(
                environment_vip['id'])
            if option_vip is not None:

                ovip = []

                if type(option_vip.get('option_vip')) is dict:
                    option_vip['option_vip'] = [option_vip['option_vip']]

                for option in option_vip['option_vip']:
                    ovip.append(option.get('nome_opcao_txt'))

                if len(ovip) > 3:
                    environment_vip['is_more'] = str(True)

                environment_vip['option_vip'] = ovip

        environment_vip_list['form'] = DeleteForm()

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ENVIRONMENTVIP_LIST,
                              environment_vip_list,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_VIP, "write": True}])
def delete_all(request):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_evip = auth.get_clientFactory().create_environment_vip()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each script selected to remove
            for id_environment_vip in ids:
                try:

                    # Execute in NetworkAPI
                    client_evip.remove(id_environment_vip)

                except NetworkAPIClientError as e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(
                    request, messages.ERROR,
                    error_messages.get("can_not_remove_all"))

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
                    request,
                    messages.SUCCESS,
                    environment_vip_messages.get("success_remove"))

            else:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(
                request,
                messages.ERROR,
                error_messages.get("select_one"))

    return redirect('environment-vip.list')


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_VIP, "write": True}])
def add_form(request):

    lists = dict()

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        lists['action'] = reverse("environment-vip.form")

        options_vip = client.create_option_vip().get_all()
        data_env = {
            "start_record": 0,
            "end_record": 5000,
            "asorting_cols": [],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }
        environmnet_list = client.create_api_environment().search(
            search=data_env)

        if request.method == "POST":

            form = EnvironmentVipForm(options_vip,
                                      environmnet_list,
                                      request.POST)
            lists['form'] = form

            if form.is_valid():

                finality = form.cleaned_data['finality']
                client_vip = form.cleaned_data['client']
                environment_p44 = form.cleaned_data['environment_p44']
                description = form.cleaned_data['description']
                option_vip = form.cleaned_data['option_vip']
                environment = form.cleaned_data['environment']

                environment_vip = client.create_environment_vip().add(
                    finality,
                    client_vip,
                    environment_p44,
                    description
                )

                for opt in option_vip:
                    client.create_option_vip().associate(
                        opt, environment_vip.get('environment_vip').get('id'))

                for env in environment:
                    client.create_ambiente().associate(
                        env, environment_vip.get('environment_vip').get('id')
                    )

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    environment_vip_messages.get("success_insert"))

                return redirect('environment-vip.list')

        else:

            lists['form'] = EnvironmentVipForm(options_vip, environmnet_list)

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ENVIRONMENTVIP_FORM,
                              lists,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_VIP, "write": True}])
def conf_form(request, id_environmentvip):

    lists = dict()

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        lists['id_vip'] = id_environmentvip

        environment_vip = client.create_api_environment_vip().get_environment_vip(
            id_environmentvip,
            fields=['id', 'conf']
        ).get('environments_vip')[0]
        conf = json.loads(environment_vip.get("conf"))

        lists['forms'] = conf.get('conf')

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ENVIRONMENTVIP_CONF_FORM,
                              lists,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_VIP, "write": True}])
def edit_form(request, id_environmentvip):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    lists = dict()
    lists['id_vip'] = id_environmentvip

    try:
        options_vip = client.create_option_vip().get_all()

        data_env = {
            "start_record": 0,
            "end_record": 5000,
            "asorting_cols": [],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }
        environmnet_list = client.create_api_environment().search(
            search=data_env)

        options = client.create_option_vip().get_option_vip(id_environmentvip)
        environment_related_list_dict = client.create_ambiente().get_related_environment_list(
            id_environmentvip)

        options = options.get("option_vip", [])
        environment_related_list_dict = environment_related_list_dict.get(
            'environment_related_list', [])

        if type(options) is dict:
            options = [options]

        if type(environment_related_list_dict) is dict:
            environment_related_list_dict = [environment_related_list_dict]

        environment_id_related_list = [env.get('environment_id')
                                       for env in environment_related_list_dict]

        if request.method == "POST":

            form = EnvironmentVipForm(options_vip, environmnet_list, request.POST)
            lists['form'] = form

            if form.is_valid():

                finality = form.cleaned_data['finality']
                client_vip = form.cleaned_data['client']
                environment_p44 = form.cleaned_data['environment_p44']
                description = form.cleaned_data['description']
                option_vip_ids = form.cleaned_data['option_vip']
                environment_ids_form = form.cleaned_data['environment']

                client.create_environment_vip().alter(
                    id_environmentvip,
                    finality,
                    client_vip,
                    environment_p44,
                    description)

                for opt in options:
                    client.create_option_vip().disassociate(opt.get('id'),
                                                            id_environmentvip)
                for opt_id in option_vip_ids:
                    client.create_option_vip().associate(opt_id, id_environmentvip)

                for related_environment_id in environment_id_related_list:
                    if _need_dissassociate_environment(related_environment_id,
                                                       environment_ids_form):
                        client.create_ambiente().disassociate(related_environment_id,
                                                              id_environmentvip)

                for environment_form_id in environment_ids_form:
                    if not _environment_already_associated(environment_form_id,
                                                           environment_id_related_list):
                        client.create_ambiente().associate(environment_form_id,
                                                           id_environmentvip)

                messages.add_message(
                    request, messages.SUCCESS, environment_vip_messages.get("sucess_edit"))

                return redirect('environment-vip.list')
        else:
            # Build form with environment vip data for id_environmentvip
            environment_vip = client.create_environment_vip().search(id_environmentvip)
            environment_vip = environment_vip.get("environment_vip")

            opts = []

            for opt in options:
                opts.append(opt.get('id'))

            lists['form'] = EnvironmentVipForm(options_vip,
                                               environmnet_list,
                                               initial={
                                                   "id": environment_vip.get("id"),
                                                   "finality": environment_vip.get(
                                                       "finalidade_txt"),
                                                   "client": environment_vip.get(
                                                       "cliente_txt"),
                                                   "environment_p44": environment_vip.get(
                                                       "ambiente_p44_txt"),
                                                   "description": environment_vip.get(
                                                       "description"),
                                                   "option_vip": opts,
                                                   "environment": environment_id_related_list})
    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ENVIRONMENTVIP_EDIT,
                              lists,
                              context_instance=RequestContext(request))


def _need_dissassociate_environment(related_environment_id, form_ids_list):
    need = related_environment_id not in form_ids_list
    return need


def _environment_already_associated(environment_form_id, environment_related_list):
    linked = environment_form_id in environment_related_list
    return linked
