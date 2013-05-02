# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.templates import ENVIRONMENT_LIST, ENVIRONMENT_FORM
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, AmbienteNaoExisteError, AmbienteError, InvalidParameterError, DataBaseError, XMLError, DetailedEnvironmentError
from django.contrib import messages
from CadVlan.permissions import ENVIRONMENT_MANAGEMENT
from CadVlan.forms import DeleteForm
from CadVlan.Environment.forms import AmbienteLogicoForm,DivisaoDCForm,Grupol3Form, AmbienteForm
from CadVlan.messages import environment_messages, vlan_messages
from django.core.urlresolvers import reverse
from CadVlan.Acl.acl import mkdir_divison_dc, deleteAclCvs, checkAclCvs
from CadVlan.Util.cvs import CVSCommandError, CVSError
from CadVlan.Util.Enum import NETWORK_TYPES
from CadVlan.Util.utility import acl_key

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
        
        # Get all environments from NetworkAPI
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
def remove_environment(request):
    
    if request.method == 'POST':
        
        form = DeleteForm(request.POST)
        
        if form.is_valid():
            # Get user
            auth = AuthSession(request.session)
            client_env = auth.get_clientFactory().create_ambiente()
            client_vlan = auth.get_clientFactory().create_vlan()

            # All ids to be removed
            ids = split_to_array(form.cleaned_data['ids'])
            
            # List of ids not found
            error_not_found = list()
            # List of environment id's who have associated VLANs or equipments that can't be removed
            error_associated = list()
            
            have_errors = False
            
            # For each environment
            for id_env in ids:
            
                try:
                    
                    #Get VLANs to remove ACLs
                    vlans = client_vlan.listar_por_ambiente(id_env).get("vlan")
                    environment = client_env.buscar_por_id(id_env).get("ambiente")
                    
                    #Remove environment and its dependencies
                    client_env.remover(id_env)
                    
                    #Remove acl's
                    user = auth.get_user()
                    for vlan in vlans:
                        
                        key_acl_v4 =  acl_key(NETWORK_TYPES.v4)
                        key_acl_v6 =  acl_key(NETWORK_TYPES.v6)
    
                        try:
                            if vlan.get(key_acl_v4) is not None:
                                if checkAclCvs(vlan.get(key_acl_v4), environment, NETWORK_TYPES.v4 , user):
                                    deleteAclCvs(vlan.get(key_acl_v4), environment, NETWORK_TYPES.v4, user)
        
                            if vlan.get(key_acl_v6) is not None:
                                if checkAclCvs(vlan.get(key_acl_v6), environment, NETWORK_TYPES.v6 , user):
                                    deleteAclCvs(vlan.get(key_acl_v6), environment, NETWORK_TYPES.v6, user)
                                    
                        except CVSError, e:
                            messages.add_message(request, messages.WARNING, vlan_messages.get("vlan_cvs_error"))
                    
                except DetailedEnvironmentError, e:
                    #Detailed message for VLAN errors
                    logger.error(e)
                    have_errors = True
                    messages.add_message(request, messages.ERROR, e)
                except AmbienteNaoExisteError, e:
                    #Environment doesn't exist. 
                    logger.error(e)
                    have_errors = True
                    error_not_found.append(id_env)
                except AmbienteError, e:
                    #Environment associated to equipment and/or VLAN that couldn't be removed.
                    logger.error(e)
                    have_errors = True
                    error_associated.append(id_env)
                except InvalidParameterError, e:
                    #Environment id is null or invalid.
                    logger.error(e)
                    have_errors = True
                    messages.add_message(request, messages.ERROR, environment_messages.get("invalid_id"))
                except DataBaseError, e:
                    #NetworkAPI fail to access database.
                    logger.error(e)
                    have_errors = True
                    messages.add_message(request, messages.ERROR, e)
                except XMLError, e:
                    #NetworkAPI fail generating XML response. 
                    logger.error(e)
                    have_errors = True
                    messages.add_message(request, messages.ERROR, e)
                except Exception, e:
                    #Other errors
                    logger.error(e)
                    have_errors = True
                    messages.add_message(request, messages.ERROR, e)
            
            # Build not found message
            if len(error_not_found) > 0:
                msg = ''
                for id_error in error_not_found[0:-1]:
                    msg = msg + id_error + ','
                if len(error_not_found) > 1:
                    msg = msg[:-1] + ' e ' + error_not_found[-1]
                else:
                    msg = error_not_found[0]
                
                msg = environment_messages.get("env_not_found") % msg
                messages.add_message(request, messages.ERROR, msg)
            
            # Build associated error message
            if len(error_associated) > 0:
                msg = ''
                for id_error in error_associated[0:-1]:
                    msg = msg + id_error + ','
                if len(error_associated) > 1:
                    msg = msg[:-1] + ' e ' + error_associated[-1]
                else:
                    msg = error_associated[0]
                
                msg = environment_messages.get("env_associated") % msg
                messages.add_message(request, messages.ERROR, msg)
                
            # Success message
            if not have_errors:
                messages.add_message(request, messages.SUCCESS, environment_messages.get("success_delete_all"))
    
    # Redirect to list_all action
    return redirect('environment.list')
    

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
        filters = client.create_filter().list_all()
        
        # Forms
        lists['ambiente'] = AmbienteForm(env_logic, division_dc, group_l3, filters)
        lists['divisaodc_form'] = DivisaoDCForm()
        lists['grupol3_form'] = Grupol3Form()
        lists['ambientelogico_form'] = AmbienteLogicoForm()
        lists['action'] = reverse("environment.form")
        
        # If form was submited
        if request.method == 'POST':
            
            # Set data in form
            ambiente_form = AmbienteForm(env_logic, division_dc, group_l3, filters, request.POST)
            
            # Validate
            if ambiente_form.is_valid():
                
                divisao_dc = ambiente_form.cleaned_data['divisao']
                ambiente_logico = ambiente_form.cleaned_data['ambiente_logico']
                grupo_l3 = ambiente_form.cleaned_data['grupol3']
                filter_ = ambiente_form.cleaned_data['filter']
                if str(filter_) == str(None):
                    filter_ = None
                link = ambiente_form.cleaned_data['link']
                
                # Business
                client.create_ambiente().inserir(grupo_l3, ambiente_logico, divisao_dc, link, filter_)
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
        filters = client.create_filter().list_all()
        
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
                   "grupol3": env.get("id_grupo_l3"),
                   "filter": env.get("id_filter"),
                   "link": env.get("link")}
        env_form = AmbienteForm(env_logic, division_dc, group_l3, filters, initial=initial)
        
        # Forms
        lists['ambiente'] = env_form
        lists['divisaodc_form'] = DivisaoDCForm(initial={"id_env": id_environment})
        lists['grupol3_form'] = Grupol3Form(initial={"id_env": id_environment})
        lists['ambientelogico_form'] = AmbienteLogicoForm(initial={"id_env": id_environment})
        lists['action'] = reverse("environment.edit", args=[id_environment])
        
        # If form was submited
        if request.method == 'POST':
            
            # Set data in form
            ambiente_form = AmbienteForm(env_logic, division_dc, group_l3, filters, request.POST)
            
            # Validate
            if ambiente_form.is_valid():
                
                id_env = ambiente_form.cleaned_data['id_env']
                divisao_dc = ambiente_form.cleaned_data['divisao']
                ambiente_logico = ambiente_form.cleaned_data['ambiente_logico']
                grupo_l3 = ambiente_form.cleaned_data['grupol3']
                filter_ = ambiente_form.cleaned_data['filter']
                if str(filter_) == str(None):
                    filter_ = None
                link = ambiente_form.cleaned_data['link']
                
                # Business
                client.create_ambiente().alterar(id_env, grupo_l3, ambiente_logico, divisao_dc, link, filter_)
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
            filters = client.create_filter().list_all()
            
            # Forms
            env_form = AmbienteForm(env_logic, division_dc, group_l3, filters)
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
                           "grupol3": env.get("id_grupo_l3"),
                           "filter": env.get("id_filter"),
                           "link": env.get("link")}
                env_form = AmbienteForm(env_logic, division_dc, group_l3, filters, initial=initial)
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
                
                mkdir_divison_dc(nome_divisao_dc, AuthSession(request.session).get_user())
                
                # Business
                client.create_divisao_dc().inserir(nome_divisao_dc.upper())
                messages.add_message(request, messages.SUCCESS, environment_messages.get("divisao_dc_sucess"))
                
            else:
                # If invalid, send all error messages in fields
                lists['divisaodc_form'] = divisao_dc_form
                
        except (NetworkAPIClientError, CVSCommandError), e:
            logger.error(e)
            lists['divisaodc_form'] = divisao_dc_form
            messages.add_message(request, messages.ERROR, e)
            
        try:
            # Get all needs from NetworkAPI
            env_logic = client.create_ambiente_logico().listar()
            division_dc = client.create_divisao_dc().listar()
            group_l3 = client.create_grupo_l3().listar()
            filters = client.create_filter().list_all()
            
            # Forms
            env_form = AmbienteForm(env_logic, division_dc, group_l3, filters)
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
                           "grupol3": env.get("id_grupo_l3"),
                           "filter": env.get("id_filter"),
                           "link": env.get("link")}
                env_form = AmbienteForm(env_logic, division_dc, group_l3, filters, initial=initial)
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
            filters = client.create_filter().list_all()
            
            # Forms
            env_form = AmbienteForm(env_logic, division_dc, group_l3, filters)
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
                           "grupol3": env.get("id_grupo_l3"),
                           "filter": env.get("id_filter"),
                           "link": env.get("link")}
                env_form = AmbienteForm(env_logic, division_dc, group_l3, filters, initial=initial)
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
    