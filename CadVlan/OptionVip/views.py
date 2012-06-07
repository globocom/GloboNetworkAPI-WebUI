# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import OPTIONVIP_LIST, OPTIONVIP_FORM
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.forms import DeleteForm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.messages import error_messages, option_vip_messages
from CadVlan.OptionVip.forms import OptionVipForm
from CadVlan.permissions import OPTION_VIP
from django.core.urlresolvers import reverse

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": OPTION_VIP, "read": True}])
def list_all(request):

    try:

        option_vip_list = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all option vips from NetworkAPI
        option_vip_list = client.create_option_vip().get_all()
        option_vip_list['form'] = DeleteForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(OPTIONVIP_LIST, option_vip_list, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": OPTION_VIP, "write": True}])
def delete_all(request):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_ovip = auth.get_clientFactory().create_option_vip()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each script selected to remove
            for id_option_vip in ids:
                try:

                    # Execute in NetworkAPI
                    client_ovip.remove(id_option_vip);

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
                messages.add_message(request, messages.SUCCESS, option_vip_messages.get("success_remove"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('option-vip.list')

@log
@login_required
@has_perm([{"permission": OPTION_VIP, "write": True}])
def add_form(request):

    try:

        if request.method == "POST":

            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            form = OptionVipForm(request.POST)

            if form.is_valid():
                name_option = form.cleaned_data['name_option']
                type_option = form.cleaned_data['type_option']

                try:
                    client.create_option_vip().add(type_option, name_option);
                    messages.add_message(request, messages.SUCCESS, option_vip_messages.get("success_insert"))

                    return redirect('option-vip.list')

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)                    

        else:

            form = OptionVipForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    action = reverse("option-vip.form")

    return render_to_response(OPTIONVIP_FORM, {'form': form, 'action': action }, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": OPTION_VIP, "write": True}])
def edit_form(request, id_optionvip):

    try:
        lists = dict()

        if request.method == 'POST':

            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            id_ovip = int (id_optionvip)

            form = OptionVipForm(request.POST) 

            lists['form'] = form
            lists['action'] = reverse("option-vip.edit", args=[id_ovip])

            if form.is_valid():
                id_option = form.cleaned_data['id_option']
                name_option = form.cleaned_data['name_option']
                type_option = form.cleaned_data['type_option']

                try:
                    client.create_option_vip().alter(id_option, type_option, name_option)
                    messages.add_message(request, messages.SUCCESS, option_vip_messages.get("success_edit"))
                    return redirect('option-vip.list')

                except NetworkAPIClientError, e:
                    messages.add_message(request, messages.ERROR, e)

            return render_to_response(OPTIONVIP_FORM, lists, context_instance=RequestContext(request))

        id_ovip = int(id_optionvip) 

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        option_vip = client.create_option_vip().search(id_ovip)

        if option_vip is None:
            messages.add_message(request, messages.ERROR, option_vip_messages.get("invalid_option_vip"))
            return redirect('option-vip.list') 

        option_vip = option_vip.get('opcoesvip')

        # Set Option VIP data
        initial = {'id_option':  option_vip.get('id'), 'name_option':  option_vip.get('nome_opcao_txt'), 'type_option':  option_vip.get('tipo_opcao')}
        form = OptionVipForm(initial=initial)

        lists['form'] = form
        lists['action'] = reverse("option-vip.edit", args=[id_ovip])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except KeyError, e:
        logger.error(e)

    return render_to_response(OPTIONVIP_FORM, lists, context_instance=RequestContext(request))