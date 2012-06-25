# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.permissions import  ADMINISTRATION
from CadVlan.templates import GROUPUSER_LIST
from CadVlan.forms import DeleteForm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.messages import error_messages, group_user_messages

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION , "read": True}])
def list_all(request):
    
    try:    
            
        lists = dict()
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all script_types from NetworkAPI
        user_groups = client.create_grupo_usuario().listar()
        lists['form'] = DeleteForm()
        lists['grupos'] = user_groups.get("grupo")
        
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(GROUPUSER_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True}])
def delete_all(request):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_group_user = auth.get_clientFactory().create_grupo_usuario()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each script selected to remove
            for id_group_user in ids:
                try:

                    # Execute in NetworkAPI
                    client_group_user.remover(id_group_user);

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(request, messages.ERROR, error_messages.get("can_not_remove_all"))

            # If cant remove someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = error_messages.get("can_not_remove") % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all has ben removed
            elif have_errors == False:
                messages.add_message(request, messages.SUCCESS, group_user_messages.get("success_remove"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('group-user.list')
