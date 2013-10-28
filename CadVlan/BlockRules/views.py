# -*- coding:utf-8 -*-

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.Decorators import log, login_required, has_perm
import logging
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.templates import BLOCK_FORM, TAB_BLOCK_FORM, TAB_RULES_FORM,\
    TAB_RULES, RULES_FORM
from django.contrib import messages
from CadVlan.BlockRules.forms import BlockRulesForm, EnvironmentsBlockForm,\
    EnvironmentRules, DeleteForm
from django.core.urlresolvers import reverse
from CadVlan.messages import block_messages, rule_messages, error_messages
from networkapiclient.exception import NetworkAPIClientError
from CadVlan.permissions import VIP_VALIDATION
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.shortcuts import render_to_response_ajax, render_json
import json

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": True, "write": False}])
def rules_list(request, id_env):
    lists = dict()
    
    # Get User
    auth   = AuthSession(request.session)
    client = auth.get_clientFactory()
    
    try:
        lists['env'] = client.create_ambiente().buscar_por_id(id_env).get('ambiente')
        rules = client.create_ambiente().get_all_rules(id_env)
        lists['rules'] = rules.get('rules') if rules else []
        lists['rules'] = lists['rules'] if type(lists['rules']) is list else [lists['rules'],]
        lists['form'] = DeleteForm()
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('environment.list')
    
    return render_to_response(TAB_RULES, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def rule_add_form(request, id_env):
    lists = dict()
    lists['form'] = EnvironmentRules()
    lists['action'] = reverse("block.rules.form", args=[id_env])
    
    # Get User
    auth   = AuthSession(request.session)
    client = auth.get_clientFactory()
    
    try:
        lists['env'] = client.create_ambiente().buscar_por_id(id_env).get('ambiente')
        blocks = client.create_ambiente().get_blocks(id_env)
        lists['blocks'] = blocks.get('blocks') if blocks else []
        
        if request.method=="POST":
            form = EnvironmentRules(request.POST)
            if form.is_valid():
                blocks = request.POST.getlist('blocks')
                client.create_ambiente().save_rule(form.cleaned_data['name'], 
                                                     form.cleaned_data['custom'],
                                                     form.cleaned_data['rule'], blocks, id_env)
                
                messages.add_message(request, messages.SUCCESS, rule_messages.get('success_insert'))
                return redirect('block.rules.list', id_env)

            else:
                # Return form with errors
                lists['form'] = form
        
        return render_to_response(TAB_RULES_FORM, lists, context_instance=RequestContext(request))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('block.rules.list', id_env)


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": True, "write": True}])
def rule_edit_form(request, id_env, id_rule):
    
    # Get User
    auth   = AuthSession(request.session)
    client = auth.get_clientFactory()
    
    try:
        
        # Get rule
        rule = client.create_ambiente().get_rule_by_pk(id_rule).get('rule')
        initial = {'name': rule['name'], 'custom': rule['custom'], 'rule': rule['content']}
    
        lists = {}
        lists['form'] = EnvironmentRules(initial=initial)
        lists['action'] = reverse("block.rules.edit", args=[id_env, id_rule])
        lists['env'] = client.create_ambiente().buscar_por_id(id_env).get('ambiente')
        blocks = client.create_ambiente().get_blocks(id_env)
        lists['blocks'] = blocks.get('blocks') if blocks else []
    
        if request.method=="POST":
            form = EnvironmentRules(request.POST)
            if form.is_valid():
                blocks = request.POST.getlist('blocks')
                client.create_ambiente().update_rule(form.cleaned_data['name'], 
                                                     form.cleaned_data['custom'],
                                                     form.cleaned_data['rule'], blocks, id_env, id_rule)
                
                messages.add_message(request, messages.SUCCESS, rule_messages.get('success_edit'))
                return redirect('block.rules.list', id_env)
    
            else:
                # Return form with errors
                lists['form'] = form
    
        return render_to_response(TAB_RULES_FORM, lists, context_instance=RequestContext(request))
    
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('block.rules.list', id_env)


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def rule_remove(request, id_env):

    # Get User
    auth   = AuthSession(request.session)
    client = auth.get_clientFactory()
    
    try:
        if request.method=="POST":
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
    
                    except NetworkAPIClientError, e:
                        logger.error(e)
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
                    messages.add_message(request, messages.SUCCESS, rule_messages.get("success_remove"))
    
                else:
                    messages.add_message(request, messages.ERROR, error_messages.get("can_not_remove_error"))
    
            else:
                messages.add_message(request, messages.ERROR, error_messages.get("select_one"))


    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return redirect('block.rules.list', id_env)


@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def edit_form(request, id_env):
    
    try:
        lists = dict()
        lists['forms']  = list()
        lists['action'] = reverse("block.edit.form", args=[id_env])
        
        
        # Get User
        auth   = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        try:
            lists['env'] = client.create_ambiente().buscar_por_id(id_env).get('ambiente')
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')
        
        if request.method == 'POST':
            blocks = request.POST.getlist('content')
            if __valid_block(blocks):
                
                client.create_ambiente().update_blocks(id_env, blocks)
                
                messages.add_message(request, messages.SUCCESS, block_messages.get('success_edit'))
            else:
                lists['error_message'] = block_messages.get('required')
        
        else:
            blocks = client.create_ambiente().get_blocks(id_env)
            blocks = blocks.get('blocks') if blocks else []
            blocks = blocks if type(blocks) is list else [blocks,]
            blocks = [block['content'] for block in blocks]
        

        if blocks:
            lists['forms'] = __mount_block_form(blocks)
        else:
            lists['forms'].append(BlockRulesForm())
            
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(TAB_BLOCK_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "read": False, "write": True}])
def rule_form(request):
    
    try:
        lists = dict()
        lists['action'] = reverse("rule.form")
        lists['form'] = EnvironmentRules()
        # Get User
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        env_list = client.create_ambiente().list_all().get('ambiente')
        
        if request.method == 'POST':
            blocks = request.POST.getlist('blocks')
            env = request.POST['envs']
            form_env = EnvironmentsBlockForm(env_list, request.POST)
            lists['form_env'] = form_env
            form = EnvironmentRules(request.POST)
            if form_env.is_valid(): 
                if form.is_valid():
                    client.create_ambiente().save_rule(form.cleaned_data['name'], 
                                                 form.cleaned_data['custom'],
                                                 form.cleaned_data['rule'], blocks, form_env.cleaned_data['envs'])
                    messages.add_message(request, messages.SUCCESS, rule_messages.get('success_insert'))
                    return redirect('block.rules.list', env)
                else:
                    lists['selected_blocks'] = blocks if blocks else []
            else:
                lists['error'] = True
                lists['selected_blocks'] = []

            lists['form'] = form
            lists['form_env'] = form_env

        else:
            lists['form_env'] = EnvironmentsBlockForm(env_list)
        
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    return render_to_response(RULES_FORM, lists, context_instance=RequestContext(request))

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
            lists['blocks'] = blocks if type(blocks) is list else [blocks,]
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException, e:
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
                    
                    messages.add_message(request, messages.SUCCESS, block_messages.get('success_insert'))
                    
                    return redirect('block.edit.form', env)
                else:
                    lists['error_message'] = block_messages.get('required')
            
        else:
            lists['form_env'] = EnvironmentsBlockForm(env_list)
            lists['forms'].append(BlockRulesForm())
        
    
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(BLOCK_FORM, lists, context_instance=RequestContext(request))

def __valid_block(blocks):
    for block in blocks:
        if block == '':
            return False
    return True

def __mount_block_form(blocks):
    blocks = blocks if type(blocks) is list else [blocks,]
    return [BlockRulesForm(initial={'content' : block}) for block in blocks]
    