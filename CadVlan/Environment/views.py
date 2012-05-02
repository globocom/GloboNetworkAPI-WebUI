# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import ENVIRONMENT_LIST, ENVIRONMENT_FORM
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.permissions import ENVIRONMENT_MANAGEMENT
from CadVlan.forms import DeleteForm
from CadVlan.Environment.forms import AmbienteLogicoForm,DivisaoDCForm,Grupol3Form,\
    AmbienteForm
from CadVlan.messages import environment_messages

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def list_all(request):
    
    try:
        
        lists = dict();
        
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
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def insert_ambiente(request):
    try:
        lists = dict()
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        ambientes_logico = client.create_ambiente_logico().listar()
        divisoes_dc = client.create_divisao_dc().listar()
        grupos_l3 = client.create_grupo_l3().listar()
        ambiente = dict()
        ambiente['divisoes'] = divisoes_dc.get("divisao_dc")
        ambiente['ambientesl'] = ambientes_logico.get("ambiente_logico")
        ambiente['gruposl3'] = grupos_l3.get("grupo_l3")
        lists['ambiente'] = AmbienteForm(ambiente)
        
        if request.method == 'POST':
            
            ambiente_form = AmbienteForm(ambiente,request.POST)
            
            if ambiente_form.is_valid():
                
                divisao_dc = ambiente_form.cleaned_data['divisao']
                ambiente_logico = ambiente_form.cleaned_data['ambiente_logico']
                grupo_l3 = ambiente_form.cleaned_data['grupol3']
                link = ambiente_form.cleaned_data['link']
                client.create_ambiente().inserir(grupo_l3, ambiente_logico, divisao_dc, link)
        
        lists['divisaodc_form'] = DivisaoDCForm()
        lists['grupol3_form'] = Grupol3Form()
        lists['ambientelogico_form'] = AmbienteLogicoForm()
       
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))
    
@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def insert_grupo_l3(request):
    lists = dict()
    lists['divisaodc_form'] = DivisaoDCForm()
    lists['grupol3_form'] = Grupol3Form()
    lists['ambientelogico_form'] = AmbienteLogicoForm()
    
    try:
         
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        ambientes_logico = client.create_ambiente_logico().listar()
        grupos_layer3 = client.create_grupo_l3.listar()
        divisoes_dc = client.create_divisao_dc().listar()
        
        lists['ambiente'] = AmbienteForm(divisoes_dc,ambientes_logico,grupos_layer3)
     
        if request.method == 'POST':
        
            grupo_l3_form = Grupol3Form(request.POST)
            lists['ambientelogico_form'] = grupo_l3_form
        
            if grupo_l3_form.is_valid():
                
                nome_grupo_l3 = grupo_l3_form.cleaned_data['nome']
                client.create_grupo_l3().inserir(nome_grupo_l3.upper())
                messages.add_message(request, messages.SUCCESS, environment_messages.get("grupo_l3_sucess"))
                lists['grupol3_form'] = Grupol3Form()
                ambientes_logico = client.create_ambiente_logico().listar()
                grupos_layer3 = client.create_grupo_l3.listar()
                divisoes_dc = client.create_divisao_dc().listar()
                lists['ambiente'] = AmbienteForm(divisoes_dc,ambientes_logico,grupos_layer3) 
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def insert_divisao_dc(request):
   
    lists = dict()
    #lists['environment'] = Formulario de Cadastro do Ambiente
    lists['divisaodc_form'] = DivisaoDCForm()
    lists['grupol3_form'] = Grupol3Form()
    lists['ambientelogico_form'] = AmbienteLogicoForm()
    
    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        ambientes_logico = client.create_ambiente_logico().listar()
        grupos_layer3 = client.create_grupo_l3.listar()
        divisoes_dc = client.create_divisao_dc().listar()
        
        lists['ambiente'] = AmbienteForm(divisoes_dc,ambientes_logico,grupos_layer3)
     
        if request.method == 'POST':
        
            divisao_dc_form = AmbienteLogicoForm(request.POST)
            lists['divisaodc_form'] = divisao_dc_form
        
            if divisao_dc_form.is_valid():
                
                nome_divisao_dc = divisao_dc_form.cleaned_data['nome']
                client.create_divisao_dc().inserir(nome_divisao_dc.upper())
                messages.add_message(request, messages.SUCCESS, environment_messages.get("divisao_dc_sucess"))
                lists['divisaodc_form'] = DivisaoDCForm()
                ambientes_logico = client.create_ambiente_logico().listar()
                grupos_layer3 = client.create_grupo_l3.listar()
                divisoes_dc = client.create_divisao_dc().listar()
                
                lists['ambiente'] = AmbienteForm(divisoes_dc,ambientes_logico,grupos_layer3)    
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def insert_ambiente_logico(request):
    lists = dict()
    #lists['environment'] = Formulario de Cadastro do Ambiente
    lists['divisaodc_form'] = DivisaoDCForm()
    lists['grupol3_form'] = Grupol3Form()
    lists['ambientelogico_form'] = AmbienteLogicoForm()
    
    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        ambientes_logico = client.create_ambiente_logico().listar()
        grupos_layer3 = client.create_grupo_l3.listar()
        divisoes_dc = client.create_divisao_dc().listar()
        
        lists['ambiente'] = AmbienteForm(divisoes_dc,ambientes_logico,grupos_layer3)
     
        if request.method == 'POST':
        
            ambiente_logico_form = AmbienteLogicoForm(request.POST)
            lists['ambientelogico_form'] = ambiente_logico_form
        
            if ambiente_logico_form.is_valid():
                
                nome_ambiente_logico = ambiente_logico_form.cleaned_data['nome']
                client.create_ambiente_logico().inserir(nome_ambiente_logico.upper())
                messages.add_message(request, messages.SUCCESS, environment_messages.get("ambiente_log_sucess"))
                lists['ambientelogico_form'] = AmbienteLogicoForm()
                ambientes_logico = client.create_ambiente_logico().listar()
                grupos_layer3 = client.create_grupo_l3.listar()
                divisoes_dc = client.create_divisao_dc().listar()
                lists['ambiente'] = AmbienteForm(divisoes_dc,ambientes_logico,grupos_layer3)  
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(ENVIRONMENT_FORM, lists, context_instance=RequestContext(request))

