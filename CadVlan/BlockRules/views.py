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
import logging
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.templates import BLOCK_FORM, TAB_BLOCK_FORM, TAB_RULES_FORM, \
    TAB_RULES, RULES_FORM
from django.contrib import messages
from CadVlan.BlockRules.forms import BlockRulesForm, EnvironmentsBlockForm, \
    EnvironmentRules, DeleteForm, ContentRulesForm
from django.core.urlresolvers import reverse
from CadVlan.messages import block_messages, rule_messages, error_messages
from networkapiclient.exception import NetworkAPIClientError
from CadVlan.permissions import VIP_VALIDATION
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.shortcuts import render_json
import json

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": True, "write": False}])
def rules_list(request, id_env):
    lists = dict()

    # Get User
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        lists['env'] = client.create_ambiente().buscar_por_id(
            id_env).get('ambiente')
        rules = client.create_ambiente().get_all_rules(id_env)
        lists['rules'] = rules.get('rules') if rules else []
        lists['rules'] = lists['rules'] if type(
            lists['rules']) is list else [lists['rules'], ]
        lists['form'] = DeleteForm()

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('environment.list')

    return render_to_response(TAB_RULES,
                              lists,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def rule_add_form(request, id_env):

    try:
        lists = dict()
        lists['form'] = EnvironmentRules()
        lists['action'] = reverse("block.rules.form", args=[id_env])
        lists['contents'] = list()
        lists['id_env'] = id_env

        # Get User
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        lists['env'] = client.create_ambiente().buscar_por_id(
            id_env).get('ambiente')

        blocks = client.create_ambiente().get_blocks(id_env)
        lists['blocks'] = blocks.get('blocks') if blocks else []

        if request.method == "POST":
            form = EnvironmentRules(request.POST)
            blocks = request.POST.getlist('blocks')
            contents = request.POST.getlist('content')
            rule_contents = request.POST.getlist('rule_content')
            if form.is_valid() and __is_valid_contents(contents, request):

                client.create_ambiente().save_rule(form.cleaned_data['name'],
                                                   id_env,
                                                   contents,
                                                   rule_contents)

                messages.add_message(
                    request, messages.SUCCESS, rule_messages.get('success_insert'))
                return redirect('block.rules.list', id_env)

            else:
                lists['form'] = form
                lists['contents'] = __mount_content_rules_form(
                    contents, rule_contents)
        else:
            lists['contents'].append(ContentRulesForm())

        return render_to_response(TAB_RULES_FORM,
                                  lists,
                                  context_instance=RequestContext(request))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('block.rules.list', id_env)


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": True, "write": True}])
def rule_edit_form(request, id_env, id_rule):

    # Get User
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:

        # Get rule
        rule = client.create_ambiente().get_rule_by_pk(id_rule).get('rule')
        initial = {'name': rule['name']}

        lists = {}
        lists['form'] = EnvironmentRules(initial=initial)
        lists['action'] = reverse("block.rules.edit", args=[id_env, id_rule])
        lists['env'] = client.create_ambiente().buscar_por_id(
            id_env).get('ambiente')
        blocks = client.create_ambiente().get_blocks(id_env)
        lists['blocks'] = blocks.get('blocks') if blocks else []
        lists['contents'] = __mount_content_rules_form(
            rule['rule_contents'], rule['rule_blocks'])
        lists['id_env'] = id_env

        if request.method == "POST":
            form = EnvironmentRules(request.POST)
            blocks = request.POST.getlist('blocks')
            contents = request.POST.getlist('content')
            rule_contents = request.POST.getlist('rule_content')

            if form.is_valid() and __is_valid_contents(contents, request):
                client.create_ambiente().update_rule(form.cleaned_data['name'],
                                                     id_env,
                                                     contents,
                                                     rule_contents,
                                                     id_rule)

                messages.add_message(
                    request, messages.SUCCESS, rule_messages.get('success_edit'))
                return redirect('block.rules.list', id_env)

            else:
                # Return form with errors
                lists['form'] = form
                lists['contents'] = __mount_content_rules_form(
                    contents, rule_contents)

        return render_to_response(TAB_RULES_FORM,
                                  lists,
                                  context_instance=RequestContext(request))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('block.rules.list', id_env)


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def rule_remove(request, id_env):

    # Get User
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        if request.method == "POST":
            form = DeleteForm(request.POST)

            if form.is_valid():

                # All ids to be deleted
                ids = split_to_array(form.cleaned_data['ids'])

                # All messages to display
                error_list = list()

                # Control others exceptions
                have_errors = False

                # For each script selected to remove
                for id_rule in ids:

                    try:
                        # Execute in NetworkAPI
                        client.create_ambiente().delete_rule(id_rule)

                    except NetworkAPIClientError as e:
                        logger.error(e)
                        have_errors = True
                        break

                # If cant remove nothing
                if len(error_list) == len(ids):
                    messages.add_message(
                        request, messages.ERROR, error_messages.get(
                            "can_not_remove_all"))

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
                        request, messages.SUCCESS, rule_messages.get(
                            "success_remove"))

                else:
                    messages.add_message(
                        request, messages.ERROR, error_messages.get(
                            "can_not_remove_error"))

            else:
                messages.add_message(
                    request, messages.ERROR, error_messages.get(
                        "select_one"))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect('block.rules.list', id_env)


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def edit_form(request, id_env):

    lists = dict()
    lists['forms'] = list()

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        lists['action'] = reverse("block.edit.form", args=[id_env])

        try:
            lists['env'] = client.create_ambiente().buscar_por_id(
                id_env).get('ambiente')
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')

        if request.method == 'POST':
            blocks = request.POST.getlist('content')
            if __valid_block(blocks):

                client.create_ambiente().update_blocks(id_env, blocks)

                messages.add_message(
                    request, messages.SUCCESS, block_messages.get(
                        'success_edit'))
            else:
                lists['error_message'] = block_messages.get(
                    'required')
        else:
            blocks = client.create_ambiente().get_blocks(id_env)
            blocks = blocks.get('blocks') if blocks else []
            blocks = blocks if type(blocks) is list else [blocks, ]
            blocks = [block['content'] for block in blocks]

        if blocks:
            lists['forms'] = __mount_block_form(blocks)
        else:
            lists['forms'].append(BlockRulesForm())

    except Exception as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(TAB_BLOCK_FORM,
                              lists,
                              context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def rule_form(request):

    lists = dict()

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        lists['action'] = reverse("rule.form")
        lists['form'] = EnvironmentRules()
        lists['contents'] = list()
        lists['id_env'] = 0

        data_env = {
            "start_record": 0,
            "end_record": 5000,
            "asorting_cols": [],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }
        envs = client.create_api_environment().search(search=data_env)
        env_list = envs.get('environments')

        if request.method == 'POST':

            blocks = request.POST.getlist('blocks')
            env = request.POST['envs']
            contents = request.POST.getlist('content')
            rule_contents = request.POST.getlist('rule_content')

            form_env = EnvironmentsBlockForm(env_list, request.POST)
            lists['form_env'] = form_env

            form = EnvironmentRules(request.POST)

            if form_env.is_valid():
                if form.is_valid() and __is_valid_contents(contents, request):

                    client.create_ambiente().save_rule(form.cleaned_data['name'],
                                                       form_env.cleaned_data[
                                                           'envs'],
                                                       contents,
                                                       rule_contents)

                    messages.add_message(
                        request, messages.SUCCESS, rule_messages.get('success_insert'))
                    return redirect('block.rules.list', env)
                else:
                    lists['selected_blocks'] = blocks if blocks else []
                    lists['contents'] = __mount_content_rules_form(
                        contents, rule_contents)
            else:
                lists['error'] = True
                lists['selected_blocks'] = []

            lists['form'] = form
            lists['form_env'] = form_env

        else:
            lists['form_env'] = EnvironmentsBlockForm(env_list)
            lists['contents'].append(ContentRulesForm())

    except Exception as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    return render_to_response(RULES_FORM, lists, context_instance=RequestContext(request))


def __is_valid_contents(contents, request):
    for content in contents:
        if content.isspace() or content == '':
            messages.add_message(
                request, messages.ERROR, rule_messages.get('required'))
            return False
    return True


def __mount_content_rules_form(contents, rule_contents):
    contents = contents if type(contents) is list else [contents, ]
    rule_contents = rule_contents if type(
        rule_contents) is list else [rule_contents, ]

    return [ContentRulesForm(initial={'content': contents[i], 'rule_content':rule_contents[i]}) for i in range(len(contents))]


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def block_ajax(request):
    try:
        lists = {}

        # Get user auth
        auth = AuthSession(request.session)
        environment = auth.get_clientFactory().create_ambiente()

        # Get environment id
        id_env = request.GET['id_env'] if 'id_env' in request.GET else False

        if id_env:
            blocks = environment.get_blocks(id_env)
            blocks = blocks.get('blocks') if blocks else []
            lists['blocks'] = blocks if type(blocks) is list else [blocks, ]

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_json(json.dumps(lists))


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def add_form(request):

    try:

        lists = dict()
        lists['forms'] = list()
        lists['action'] = reverse("block.form")

        # Get User
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        env_list = client.create_ambiente().list_no_blocks().get('ambiente')

        if request.method == 'POST':
            blocks = request.POST.getlist('content')
            env = request.POST['envs']

            form_env = EnvironmentsBlockForm(env_list, request.POST)

            lists['form_env'] = form_env
            lists['forms'] = __mount_block_form(blocks)

            if form_env.is_valid():
                if __valid_block(blocks):

                    client.create_ambiente().save_blocks(env, blocks)

                    messages.add_message(
                        request, messages.SUCCESS, block_messages.get('success_insert'))

                    return redirect('block.edit.form', env)
                else:
                    lists['error_message'] = block_messages.get('required')

        else:
            lists['form_env'] = EnvironmentsBlockForm(env_list)
            lists['forms'].append(BlockRulesForm())

    except Exception as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(BLOCK_FORM, lists, context_instance=RequestContext(request))


def __valid_block(blocks):
    for block in blocks:
        if block == '':
            return False
    return True


def __mount_block_form(blocks):
    blocks = blocks if type(blocks) is list else [blocks, ]
    return [BlockRulesForm(initial={'content': block}) for block in blocks]
