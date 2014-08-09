# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.GroupUser.forms import GroupUserForm
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.forms import DeleteForm
from CadVlan.messages import error_messages, group_user_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import GROUPUSER_LIST, GROUPUSER_FORM
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError
import logging

logger = logging.getLogger(__name__)

PERMISSION = {True: 'S', False: 'N'}


def get_permission(value):
    for key in PERMISSION.iterkeys():
        if value == PERMISSION.get(key):
            return key

    return PERMISSION.get(False)


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def list_all(request):

    try:

        lists = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all user groups from NetworkAPI
        user_groups = client.create_grupo_usuario().listar()
        lists['form'] = DeleteForm()
        lists['grupos'] = user_groups.get("user_group")

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(GROUPUSER_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
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
                    client_group_user.remover(id_group_user)

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
                    request, messages.SUCCESS, group_user_messages.get("success_remove"))

            else:
                messages.add_message(
                    request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('group-user.list')


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def add_form(request):

    try:

        if request.method == "POST":

            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            form = GroupUserForm(request.POST)

            if form.is_valid():
                name = form.cleaned_data['name']
                read = PERMISSION.get(form.cleaned_data['read'])
                write = PERMISSION.get(form.cleaned_data['write'])
                edition = PERMISSION.get(form.cleaned_data['edition'])
                delete = PERMISSION.get(form.cleaned_data['delete'])

                try:
                    client.create_grupo_usuario().inserir(
                        name, read, write, edition, delete)
                    messages.add_message(
                        request, messages.SUCCESS, group_user_messages.get("success_insert"))

                    return redirect('group-user.list')

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)

        else:

            form = GroupUserForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    action = reverse("group-user.form")

    return render_to_response(GROUPUSER_FORM, {'form': form, 'action': action}, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def edit_form(request, id_group_user):

    try:
        lists = dict()
        lists['form'] = GroupUserForm()

        if request.method == 'POST':

            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            id_group = int(id_group_user)

            form = GroupUserForm(request.POST)

            lists['form'] = form
            lists['action'] = reverse("group-user.edit", args=[id_group])

            if form.is_valid():
                id_group_user = form.cleaned_data['id_group_user']
                name = form.cleaned_data['name']
                read = PERMISSION.get(form.cleaned_data['read'])
                write = PERMISSION.get(form.cleaned_data['write'])
                edition = PERMISSION.get(form.cleaned_data['edition'])
                delete = PERMISSION.get(form.cleaned_data['delete'])

                try:
                    client.create_grupo_usuario().alterar(
                        id_group_user, name, read, write, edition, delete)
                    messages.add_message(
                        request, messages.SUCCESS, group_user_messages.get("success_edit"))
                    return redirect('group-user.list')

                except NetworkAPIClientError, e:
                    messages.add_message(request, messages.ERROR, e)

            return render_to_response(GROUPUSER_FORM, lists, context_instance=RequestContext(request))

        id_group = int(id_group_user)

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        group_user = client.create_grupo_usuario().search(id_group)

        if group_user is None:
            messages.add_message(
                request, messages.ERROR, group_user_messages.get("invalid_group_user"))
            return redirect('group-user.list')

        group_user = group_user.get('user_group')

        # Set Group User data
        initial = {'id_group_user':  group_user.get('id'), 'name':  group_user.get('nome'), 'read': get_permission(group_user.get('leitura')), 'write': get_permission(
            group_user.get('escrita')), 'edition': get_permission(group_user.get('edicao')), 'delete': get_permission(group_user.get('exclusao'))}
        form = GroupUserForm(initial=initial)

        lists['form'] = form
        lists['action'] = reverse("group-user.edit", args=[id_group])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except KeyError, e:
        logger.error(e)

    return render_to_response(GROUPUSER_FORM, lists, context_instance=RequestContext(request))
