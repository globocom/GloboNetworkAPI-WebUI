# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import GROUP_EQUIPMENT_LIST, GROUP_EQUIPMENT_FORM
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.forms import DeleteForm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.messages import error_messages, group_equip_messages
from CadVlan.GroupEquip.forms import GroupEquipForm
from CadVlan.permissions import ADMINISTRATION
from django.core.urlresolvers import reverse

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def list_all(request):

    try:

        egroup_list = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all  Group Equipament from NetworkAPI
        egroup_list = client.create_grupo_equipamento().listar()
        egroup_list['form'] = DeleteForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(GROUP_EQUIPMENT_LIST, egroup_list, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def delete_all(request):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_egroup = auth.get_clientFactory().create_grupo_equipamento()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each equipment group selected to remove
            for id_egroup in ids:
                try:

                    # Execute in NetworkAPI
                    client_egroup.remover(id_egroup)

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If can't remove nothing
            if len(error_list) == len(ids):
                messages.add_message(request, messages.ERROR, error_messages.get("can_not_remove_all"))

            # If can't remove some
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = error_messages.get("can_not_remove") % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all have been removed
            elif have_errors == False:
                messages.add_message(request, messages.SUCCESS, group_equip_messages.get("success_remove"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('group-equip.list')

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def add_form(request):

    try:

        if request.method == "POST":

            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            form = GroupEquipForm(request.POST)

            if form.is_valid():
                name = form.cleaned_data['name']

                try:
                    client.create_grupo_equipamento().inserir(name)
                    messages.add_message(request, messages.SUCCESS, group_equip_messages.get("success_insert"))

                    return redirect('group-equip.list')

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)                    

        else:

            form = GroupEquipForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    action = reverse("group-equip.form")

    return render_to_response(GROUP_EQUIPMENT_FORM, {'form': form, 'action': action }, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def edit_form(request, id_group_equipament):

    try:
        lists = dict()

        if request.method == 'POST':

            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            id_egroup = int (id_group_equipament)

            form = GroupEquipForm(request.POST) 

            lists['form'] = form
            lists['action'] = reverse("group-equip.edit", args=[id_egroup])

            if form.is_valid():
                id = form.cleaned_data['id']
                name = form.cleaned_data['name']

                try:
                    client.create_grupo_equipamento().alterar(id, name)
                    messages.add_message(request, messages.SUCCESS, group_equip_messages.get("success_edit"))
                    return redirect('group-equip.list')

                except NetworkAPIClientError, e:
                    messages.add_message(request, messages.ERROR, e)

            return render_to_response(GROUP_EQUIPMENT_FORM, lists, context_instance=RequestContext(request))

        id_egroup = int(id_group_equipament) 

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        egroup = client.create_grupo_equipamento().search(id_egroup)

        if egroup is None:
            messages.add_message(request, messages.ERROR, group_equip_messages.get("invalid_group_equipament"))
            return redirect('group-equip.list') 

        egroup = egroup.get('group_equipament')

        # Set Group Equipament data
        initial = {'id':  egroup.get('id'), 'name':  egroup.get('nome')}
        form = GroupEquipForm(initial=initial)

        lists['form'] = form
        lists['action'] = reverse("group-equip.edit", args=[id_egroup])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except KeyError, e:
        logger.error(e)

    return render_to_response(GROUP_EQUIPMENT_FORM, lists, context_instance=RequestContext(request))