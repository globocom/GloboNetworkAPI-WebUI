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
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import SCRIPT_LIST, SCRIPT_FORM
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, RoteiroError, NomeRoteiroDuplicadoError
from django.contrib import messages
from CadVlan.messages import error_messages, script_messages
from CadVlan.Util.converters.util import split_to_array, replace_id_to_name
from CadVlan.permissions import SCRIPT_MANAGEMENT
from CadVlan.forms import DeleteForm
from CadVlan.Script.forms import ScriptForm

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": SCRIPT_MANAGEMENT, "read": True}])
def list_all(request):

    try:

        lists = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all scripts from NetworkAPI
        script_list = client.create_roteiro().listar()
        # Get all script_types from NetworkAPI
        script_type_list = client.create_tipo_roteiro().listar()

        # Business
        lists['scripts'] = replace_id_to_name(
            script_list["script"], script_type_list["script_type"], "tipo_roteiro", "id", "tipo")
        lists['form'] = DeleteForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(SCRIPT_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": SCRIPT_MANAGEMENT, "write": True}])
def delete_all(request):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            roteiro = auth.get_clientFactory().create_roteiro()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each script selected to remove
            for id_script in ids:
                try:

                    # Execute in NetworkAPI
                    roteiro.remover(id_script)

                except RoteiroError, e:
                    # If isnt possible, add in error list
                    error_list.append(id_script)

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
                    request, messages.SUCCESS, script_messages.get("success_remove"))

            else:
                messages.add_message(
                    request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect("script.list")


@log
@login_required
@has_perm([{"permission": SCRIPT_MANAGEMENT, "read": True, "write": True}])
def add_form(request):

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Enviar listas para formar os Selects do formulário
        forms_aux = dict()

        # List All - Brands
        forms_aux['marcas'] = client.create_marca().listar().get('brand')
        # Get all script_types from NetworkAPI
        forms_aux['tipo_roteiro'] = client.create_tipo_roteiro().listar()

        # If form was submited
        if request.method == 'POST':

            form = ScriptForm(forms_aux, request.POST)

            if form.is_valid():

                # Data
                name = form.cleaned_data['name']
                script_type = form.cleaned_data['script_type']
                modelo = form.cleaned_data['modelo']
                description = form.cleaned_data['description']

                try:
                    # Business
                    client.create_roteiro().inserir(script_type, name, modelo, description)
                    messages.add_message(request, messages.SUCCESS, script_messages.get("success_insert"))
                    return redirect('script.list')
                except NomeRoteiroDuplicadoError, e:
                    messages.add_message(request, messages.ERROR, e)

        else:
            forms_aux['modelos'] = None
            form = ScriptForm(forms_aux)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(SCRIPT_FORM, {'form': form}, context_instance=RequestContext(request))
