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


from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.forms import DeleteForm
from CadVlan.messages import error_messages, environment_vip_messages
from CadVlan.permissions import ENVIRONMENT_VIP
from CadVlan.templates import ENVIRONMENTVIP_LIST, ENVIRONMENTVIP_FORM, ENVIRONMENTVIP_EDIT
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError
import logging
from CadVlan.EnvironmentVip.form import EnvironmentVipForm

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_VIP, "read": True}])
def list_all(request):

    try:

        environment_vip_list = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

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

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ENVIRONMENTVIP_LIST, environment_vip_list, context_instance=RequestContext(request))


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
            elif have_errors == False:
                messages.add_message(
                    request, messages.SUCCESS, environment_vip_messages.get("success_remove"))

            else:
                messages.add_message(
                    request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('environment-vip.list')


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_VIP, "write": True}])
def add_form(request):

    try:

        lists = dict()
        lists['action'] = reverse("environment-vip.form")
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        options_vip = client.create_option_vip().get_all()

        if request.method == "POST":

            form = EnvironmentVipForm(options_vip, request.POST)
            lists['form'] = form

            if form.is_valid():

                finality = form.cleaned_data['finality']
                client_vip = form.cleaned_data['client']
                environment_p44 = form.cleaned_data['environment_p44']
                option_vip = form.cleaned_data['option_vip']

                environment_vip = client.create_environment_vip().add(
                    finality, client_vip, environment_p44)

                for opt in option_vip:
                    client.create_option_vip().associate(
                        opt, environment_vip.get('environment_vip').get('id'))

                messages.add_message(
                    request, messages.SUCCESS, environment_vip_messages.get("success_insert"))

                return redirect('environment-vip.list')

        else:

            lists['form'] = EnvironmentVipForm(options_vip)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ENVIRONMENTVIP_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ENVIRONMENT_VIP, "write": True}])
def edit_form(request, id_environmentvip):

    try:

        lists = dict()
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['id_vip'] = id_environmentvip

        options_vip = client.create_option_vip().get_all()

        options = client.create_option_vip().get_option_vip(id_environmentvip)

        if options is not None:
            options = options.get("option_vip")

        if type(options) is dict:
            options = [options]

        if request.method == "POST":

            form = EnvironmentVipForm(options_vip, request.POST)
            lists['form'] = form

            if form.is_valid():

                finality = form.cleaned_data['finality']
                client_vip = form.cleaned_data['client']
                environment_p44 = form.cleaned_data['environment_p44']
                option_vip = form.cleaned_data['option_vip']

                client.create_environment_vip().alter(
                    id_environmentvip, finality, client_vip, environment_p44)

                if options is not None:
                    for opt in options:
                        client.create_option_vip().disassociate(
                            opt.get('id'), id_environmentvip)

                for opt in option_vip:
                    client.create_option_vip().associate(
                        opt, id_environmentvip)

                messages.add_message(
                    request, messages.SUCCESS, environment_vip_messages.get("sucess_edit"))

                return redirect('environment-vip.list')
        # GET
        else:
            # Build form with environment vip data for id_environmentvip
            environment_vip = client.create_environment_vip().search(
                id_environmentvip)
            environment_vip = environment_vip.get("environment_vip")

            opts = []

            if options is not None:
                for opt in options:
                    opts.append(opt.get('id'))

            lists['form'] = EnvironmentVipForm(options_vip, initial={"id": environment_vip.get("id"),
                                                                     "finality": environment_vip.get("finalidade_txt"),
                                                                     "client": environment_vip.get("cliente_txt"),
                                                                     "environment_p44": environment_vip.get("ambiente_p44_txt"),
                                                                     "option_vip": opts})
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ENVIRONMENTVIP_EDIT, lists, context_instance=RequestContext(request))
