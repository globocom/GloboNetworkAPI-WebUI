# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import SCRIPTTYPE_LIST, SCRIPTTYPE_FORM
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import TipoRoteiroError, NetworkAPIClientError
from django.contrib import messages
from CadVlan.forms import DeleteForm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.messages import error_messages, script_type_messages
from CadVlan.ScriptType.forms import ScriptTypeForm
from networkapiclient.exception import NomeTipoRoteiroDuplicadoError
from CadVlan.permissions import SCRIPT_MANAGEMENT

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": SCRIPT_MANAGEMENT, "read": True}])
def list_all(request):

    try:

        script_type_list = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all script_types from NetworkAPI
        script_type_list = client.create_tipo_roteiro().listar()
        script_type_list['form'] = DeleteForm()

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(
        SCRIPTTYPE_LIST,
        script_type_list,
        context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": SCRIPT_MANAGEMENT, "write": True}])
def delete_all(request):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            tipo_roteiro = auth.get_clientFactory().create_tipo_roteiro()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each script selected to remove
            for id_script_type in ids:
                try:

                    # Execute in NetworkAPI
                    tipo_roteiro.remover(id_script_type)

                except TipoRoteiroError as e:
                    # If isnt possible, add in error list
                    error_list.append(id_script_type)

                except NetworkAPIClientError as e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(
                    request,
                    messages.ERROR,
                    error_messages.get("can_not_remove_all"))

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
                    request,
                    messages.SUCCESS,
                    script_type_messages.get("success_remove"))

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

    # Redirect to list_all action
    return redirect("script.type.list")


@log
@login_required
@has_perm([{"permission": SCRIPT_MANAGEMENT, "write": True}])
def show_form(request):

    try:

        if request.method == "POST":

            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            # Um form com os dados de POST
            form = ScriptTypeForm(request.POST)

            if form.is_valid():
                tipo = form.cleaned_data['script_type']
                descricao = form.cleaned_data['description']
                try:
                    client.create_tipo_roteiro().inserir(
                        tipo.upper(),
                        descricao)
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        script_type_messages.get("success_insert"))

                    return redirect('script.type.list')
                except NomeTipoRoteiroDuplicadoError as e:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        script_type_messages.get("error_equal_name") %
                        tipo)

        else:

            form = ScriptTypeForm()

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(
        SCRIPTTYPE_FORM, {
            'form': form}, context_instance=RequestContext(request))
