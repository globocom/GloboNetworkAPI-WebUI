# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import ENVIRONMENT_LIST, ENVIRONMENT_FORM
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.permissions import ENVIRONMENT_MANAGEMENT
from CadVlan.forms import DeleteForm
from CadVlan.Environment.forms import AmbienteLogicoForm,DivisaoDCForm,Grupol3Form,\
    AmbienteForm
from CadVlan.messages import environment_messages
from django.core.urlresolvers import reverse

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def list_all(request):
    
    try:
        
        lists = dict()
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get all scripts from NetworkAPI
        environment = client.create_ambiente().listar()
        
        # Business
        lists['environment'] = environment.get("ambiente")
        lists['form'] = DeleteForm()
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(ENVIRONMENT_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True, "write": True}])
def insert_ambiente(request):
    
    try:
        lists = dict()
        
        # Get User
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get all needs from NetworkAPI
        env_logic = client.create_ambiente_logico().listar()
        division_dc = client.create_divisao_dc().listar()
        group_l3 = client.create_grupo_l3().listar()
        
        # Forms
        lists['ambiente'] = AmbienteForm(env_logic, division_dc, group_l3)
        lists['divisaodc_form'] = DivisaoDCForm()
        lists['grupol3_form'] = Grupol3Form()
        lists['ambientelogico_form'] = AmbienteLogicoForm()
        lists['action'] = reverse("environment.form")
        
        # If form was submited
        if request.method == 'POST':
            
            # Set data in form
            ambiente_form = AmbienteForm(env_logic, division_dc, group_l3, request.POST)
            
            # Validate
            if ambiente_form.is_valid():
                
                divisao_dc = ambiente_form.cleaned_data['divisao']
                ambiente_logico = ambiente_form.cleaned_data['ambiente_logico']
                grupo_l3 = ambiente_form.cleaned_data['grupol3']
                link = ambiente_form.cleaned_data['link']
                
                # Business
                client.create_ambiente().inserir(grupo_l3, ambiente_logico, divisao_dc, link)
                messages.add_message(request, messages.SUCCESS, environment_messages.get("success_insert"))
                
                return redirect('environment.list')
            
            else:
                # If invalid, send all error messages in fields
                lists['ambiente'] = ambiente_form
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True, "write": True}])
def edit(request, id_environment):
    
    try:
        lists = dict()
        
        # Get User
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get all needs from NetworkAPI
        env_logic = client.create_ambiente_logico().listar()
        division_dc = client.create_divisao_dc().listar()
        group_l3 = client.create_grupo_l3().listar()
        
        try:
            env = client.create_ambiente().buscar_por_id(id_environment)
            env = env.get("ambiente")
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')
        
        # Set Environment data
        initial = {"id_env": env.get("id"), "divisao": env.get("id_divisao"),
                   "ambiente_logico": env.get("id_ambiente_logico"),
                   "grupol3": env.get("id_grupo_l3"), "link": env.get("link")}
        env_form = AmbienteForm(env_logic, division_dc, group_l3, initial=initial)
        
        # Forms
        lists['ambiente'] = env_form
        lists['divisaodc_form'] = DivisaoDCForm(initial={"id_env": id_environment})
        lists['grupol3_form'] = Grupol3Form(initial={"id_env": id_environment})
        lists['ambientelogico_form'] = AmbienteLogicoForm(initial={"id_env": id_environment})
        lists['action'] = reverse("environment.edit", args=[id_environment])
        
        # If form was submited
        if request.method == 'POST':
            
            # Set data in form
            ambiente_form = AmbienteForm(env_logic, division_dc, group_l3, request.POST)
            
            # Validate
            if ambiente_form.is_valid():
                
                id_env = ambiente_form.cleaned_data['id_env']
                divisao_dc = ambiente_form.cleaned_data['divisao']
                ambiente_logico = ambiente_form.cleaned_data['ambiente_logico']
                grupo_l3 = ambiente_form.cleaned_data['grupol3']
                link = ambiente_form.cleaned_data['link']
                
                # Business
                client.create_ambiente().alterar(id_env, grupo_l3, ambiente_logico, divisao_dc, link)
                messages.add_message(request, messages.SUCCESS, environment_messages.get("success_edit"))
                
                return redirect('environment.list')
            
            else:
                # If invalid, send all error messages in fields
                lists['ambiente'] = ambiente_form
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True, "write": True}])
def insert_grupo_l3(request):
    
    # If form was submited
    if request.method == 'POST':
        
        try:
            lists = dict()
            
            # Get User
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            lists['grupol3_form'] = Grupol3Form()
            
            # Set data in form
            grupo_l3_form = Grupol3Form(request.POST)
            
            id_env = request.POST['id_env']
            
            # Validate
            if grupo_l3_form.is_valid():
                
                nome_grupo_l3 = grupo_l3_form.cleaned_data['nome']
                
                # Business
                client.create_grupo_l3().inserir(nome_grupo_l3.upper())
                messages.add_message(request, messages.SUCCESS, environment_messages.get("grupo_l3_sucess"))
                
            else:
                # If invalid, send all error messages in fields
                lists['grupol3_form'] = grupo_l3_form
                
        except NetworkAPIClientError, e:
            logger.error(e)
            lists['grupol3_form'] = grupo_l3_form
            messages.add_message(request, messages.ERROR, e)
            
        try:
            # Get all needs from NetworkAPI
            env_logic = client.create_ambiente_logico().listar()
            division_dc = client.create_divisao_dc().listar()
            group_l3 = client.create_grupo_l3().listar()
            
            # Forms
            env_form = AmbienteForm(env_logic, division_dc, group_l3)
            div_form = DivisaoDCForm()
            amb_form = AmbienteLogicoForm()
            action = reverse("environment.form")
            
            # If id_env is set, still in edit
            if id_env:
                env = client.create_ambiente().buscar_por_id(id_env)
                env = env.get("ambiente")
                
                # Set Environment data
                initial = {"id_env": env.get("id"), "divisao": env.get("id_divisao"),
                           "ambiente_logico": env.get("id_ambiente_logico"),
                           "grupol3": env.get("id_grupo_l3"), "link": env.get("link")}
                env_form = AmbienteForm(env_logic, division_dc, group_l3, initial=initial)
                div_form = DivisaoDCForm(initial={"id_env": id_env})
                amb_form = AmbienteLogicoForm(initial={"id_env": id_env})
                action = reverse("environment.edit", args=[id_env])
                
            lists['ambiente'] = env_form
            lists['divisaodc_form'] = div_form
            lists['ambientelogico_form'] = amb_form
            lists['action'] = action
            
            return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))
        
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')
        
    else:
        return redirect("environment.form")
    
@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True, "write": True}])
def insert_divisao_dc(request):
    
    # If form was submited
    if request.method == 'POST':
        
        try:
            lists = dict()
            
            # Get User
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            lists['divisaodc_form'] = DivisaoDCForm()
            
            # Set data in form
            divisao_dc_form = DivisaoDCForm(request.POST)
            
            id_env = request.POST['id_env']
            
            # Validate
            if divisao_dc_form.is_valid():
                
                nome_divisao_dc = divisao_dc_form.cleaned_data['nome']
                
                # Business
                client.create_divisao_dc().inserir(nome_divisao_dc.upper())
                messages.add_message(request, messages.SUCCESS, environment_messages.get("divisao_dc_sucess"))
                
            else:
                # If invalid, send all error messages in fields
                lists['divisaodc_form'] = divisao_dc_form
                
        except NetworkAPIClientError, e:
            logger.error(e)
            lists['divisaodc_form'] = divisao_dc_form
            messages.add_message(request, messages.ERROR, e)
            
        try:
            # Get all needs from NetworkAPI
            env_logic = client.create_ambiente_logico().listar()
            division_dc = client.create_divisao_dc().listar()
            group_l3 = client.create_grupo_l3().listar()
            
            # Forms
            env_form = AmbienteForm(env_logic, division_dc, group_l3)
            gro_form = Grupol3Form()
            amb_form = AmbienteLogicoForm()
            action = reverse("environment.form")
            
            # If id_env is set, still in edit
            if id_env:
                env = client.create_ambiente().buscar_por_id(id_env)
                env = env.get("ambiente")
                
                # Set Environment data
                initial = {"id_env": env.get("id"), "divisao": env.get("id_divisao"),
                           "ambiente_logico": env.get("id_ambiente_logico"),
                           "grupol3": env.get("id_grupo_l3"), "link": env.get("link")}
                env_form = AmbienteForm(env_logic, division_dc, group_l3, initial=initial)
                gro_form = Grupol3Form(initial={"id_env": id_env})
                amb_form = AmbienteLogicoForm(initial={"id_env": id_env})
                action = reverse("environment.edit", args=[id_env])
                
            lists['ambiente'] = env_form
            lists['grupol3_form'] = gro_form
            lists['ambientelogico_form'] = amb_form
            lists['action'] = action
            
            return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))
        
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')
        
    else:
        return redirect("environment.form")
    
@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True, "write": True}])
def insert_ambiente_logico(request):
    
    # If form was submited
    if request.method == 'POST':
        
        try:
            lists = dict()
            
            # Get User
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            lists['ambientelogico_form'] = AmbienteLogicoForm()
            
            # Set data in form
            ambiente_logico_form = AmbienteLogicoForm(request.POST)
            
            id_env = request.POST['id_env']
            
            # Validate
            if ambiente_logico_form.is_valid():
                
                nome_ambiente_logico = ambiente_logico_form.cleaned_data['nome']
                
                # Business
                client.create_ambiente_logico().inserir(nome_ambiente_logico.upper())
                messages.add_message(request, messages.SUCCESS, environment_messages.get("ambiente_log_sucess"))
                
            else:
                # If invalid, send all error messages in fields
                lists['ambientelogico_form'] = ambiente_logico_form
                
        except NetworkAPIClientError, e:
            logger.error(e)
            lists['ambientelogico_form'] = ambiente_logico_form
            messages.add_message(request, messages.ERROR, e)
            
        try:
            # Get all needs from NetworkAPI
            env_logic = client.create_ambiente_logico().listar()
            division_dc = client.create_divisao_dc().listar()
            group_l3 = client.create_grupo_l3().listar()
            
            # Forms
            env_form = AmbienteForm(env_logic, division_dc, group_l3)
            div_form = DivisaoDCForm()
            gro_form = Grupol3Form()
            action = reverse("environment.form")
            
            # If id_env is set, still in edit
            if id_env:
                env = client.create_ambiente().buscar_por_id(id_env)
                env = env.get("ambiente")
                
                # Set Environment data
                initial = {"id_env": env.get("id"), "divisao": env.get("id_divisao"),
                           "ambiente_logico": env.get("id_ambiente_logico"),
                           "grupol3": env.get("id_grupo_l3"), "link": env.get("link")}
                env_form = AmbienteForm(env_logic, division_dc, group_l3, initial=initial)
                div_form = DivisaoDCForm(initial={"id_env": id_env})
                gro_form = Grupol3Form(initial={"id_env": id_env})
                action = reverse("environment.edit", args=[id_env])
                
            lists['ambiente'] = env_form
            lists['divisaodc_form'] = div_form
            lists['grupol3_form'] = gro_form
            lists['action'] = action
            
            return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))
        
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('environment.list')
        
    else:
        return redirect("environment.form")
    