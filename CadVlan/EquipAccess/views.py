# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import EQUIPMENTACESS_SEARCH_LIST, EQUIPMENTACESS_FORM, EQUIPMENTACESS_EDIT
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, EquipamentoAcessoError, EquipamentoError
from django.contrib import messages
from CadVlan.EquipAccess.forms import EquipAccessForm
from CadVlan.Util.converters.util import replace_id_to_name, split_to_array
from CadVlan.messages import equip_access_messages, error_messages
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from django.utils.datastructures import MultiValueDictKeyError
from CadVlan.forms import DeleteForm, SearchEquipForm

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def search_list(request):
    
    try:
        lists = dict();
        lists['form'] = SearchEquipForm()
        lists['delete_form'] = DeleteForm()
        
        if request.method == "GET":
            
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            if request.GET.__contains__('equip_name'):
                lists['form'] = form = SearchEquipForm(request.GET)
                
                if form.is_valid():
                    
                        #recuperar nome do equipamento pesquisado
                        name_equip = form.cleaned_data['equip_name']
                        
                        id_equip = None
                    
                        #recuperando lista de equipamentos de acesso
                        equip_access_list = client.create_equipamento_acesso().list_by_equip(name_equip)
                        
                        if len(equip_access_list.get('equipamento_acesso')) > 0:
                        
                            id_equip = equip_access_list.get('equipamento_acesso')
                        
                            id_equip = id_equip[0].get("equipamento")
                           
                            access_type = client.create_tipo_acesso().listar()
                    
                            equip_access_list = replace_id_to_name(equip_access_list["equipamento_acesso"], access_type["tipo_acesso"], "tipo_acesso", "id", "protocolo")
                        
                            lists['equip_access_list'] = equip_access_list
                            
                        lists['form'] = form
                        lists['delete_form'] = DeleteForm(initial = {"equip_name":name_equip,"equip_id":id_equip})
                
                return render_to_response(EQUIPMENTACESS_SEARCH_LIST, lists, context_instance=RequestContext(request))
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
           
    return render_to_response(EQUIPMENTACESS_SEARCH_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def search_list_param(request,id_equip):
    
    lists = dict();
    
    try:
            
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            equip = client.create_equipamento().listar_por_id(id_equip)
            
            name_equip = equip.get('equipamento').get('nome')
             
            #recuperando lista de equipamentos de acesso
            equip_access_list = client.create_equipamento_acesso().list_by_equip(name_equip)
            
            access_type = client.create_tipo_acesso().listar()
            
            lists['form'] = SearchEquipForm(initial = {"equip_name":name_equip})
            
            lists['delete_form'] = DeleteForm(initial = {"equip_name":name_equip,"equip_id":id_equip})
                 
            equip_access_list = replace_id_to_name(equip_access_list["equipamento_acesso"], access_type["tipo_acesso"], "tipo_acesso", "id", "protocolo")
                
            lists['equip_access_list'] = equip_access_list
            
            return render_to_response(EQUIPMENTACESS_SEARCH_LIST, lists , context_instance=RequestContext(request))
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    lists['form'] = SearchEquipForm()        
    lists['delete_form'] = DeleteForm()
        
    return render_to_response(EQUIPMENTACESS_SEARCH_LIST,lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def add_form(request):
    lists = dict()
    try :
        if request.method == 'GET':
            
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            if not request.GET.__contains__('equip_name'):
                form = SearchEquipForm()
            else:
                form = SearchEquipForm(request.GET)
            
            if form.is_valid():
                
                name_equip = form.cleaned_data['equip_name']
                
                equip = client.create_equipamento().listar_por_nome(name_equip)
                id_equip = equip.get('equipamento').get('id')
                protocol_list = client.create_tipo_acesso().listar()
                
                lists['formCad'] = formCad = EquipAccessForm(protocol_list)
                formCad.fields['id_equip'].initial = id_equip
                formCad.fields['name_equip'].initial = name_equip
                
            lists['form'] = form    
            return render_to_response(EQUIPMENTACESS_FORM,lists, context_instance=RequestContext(request))
            
            
        if request.method == 'POST':
            
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            form = SearchEquipForm()
            form.fields['equip_name'].initial = request.POST['name_equip']
            
            protocol_list = client.create_tipo_acesso().listar()
            
            formCad = EquipAccessForm(protocol_list, request.POST)
            
            if formCad.is_valid():
                user = formCad.cleaned_data['user']
                host = formCad.cleaned_data['host']
                password = formCad.cleaned_data['password']
                second_password = formCad.cleaned_data['second_password']
                equip = formCad.cleaned_data['id_equip']
                protocol = formCad.cleaned_data['protocol']
                
                try:
                    client.create_equipamento_acesso().inserir(equip, host, user, password, protocol, second_password)
                    messages.add_message(request, messages.SUCCESS, equip_access_messages.get("success_insert"))
                    return search_list_param(request, equip)
                except EquipamentoAcessoError,e:
                    messages.add_message(request, messages.ERROR, equip_access_messages.get("already_association")) 
                except NetworkAPIClientError, e:
                    messages.add_message(request, messages.ERROR, e)
                    
                    
            lists['form'] = form
            lists['formCad'] = formCad      
            return render_to_response(EQUIPMENTACESS_FORM,lists, context_instance=RequestContext(request))  
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except MultiValueDictKeyError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR,equip_access_messages.get("no_equip"))
    lists['form'] = SearchEquipForm()
   
    return render_to_response(EQUIPMENTACESS_FORM,lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def edit(request, id_access):
    try:
        lists = dict()
        if request.method == 'POST':
            
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            protocol_list = client.create_tipo_acesso().listar()
            
            id_acesso = int (id_access)
            
            form = EquipAccessForm(protocol_list, request.POST) 
            
            lists['form'] = form
            lists['id_acesso'] = id_acesso
            
            if form.is_valid():
                user = form.cleaned_data['user']
                host = form.cleaned_data['host']
                password = form.cleaned_data['password']
                second_password = form.cleaned_data['second_password']
                equip = form.cleaned_data['id_equip']
                protocol = form.cleaned_data['protocol']
                
                try:
                    client.create_equipamento_acesso().edit_by_id(id_acesso, protocol, host, user, password, second_password)
                    messages.add_message(request, messages.SUCCESS, equip_access_messages.get("success_edit"))
                    return search_list_param(request, equip)
               
                except NetworkAPIClientError, e:
                    messages.add_message(request, messages.ERROR, e)
                
                    
            equip_access = client.create_equipamento_acesso().get_access(id_acesso)
            lists['id_equip'] = equip_access.get('equipamento_acesso').get('equipamento')
            
            return render_to_response(EQUIPMENTACESS_EDIT,lists,context_instance=RequestContext(request))
        
        #Ao carregar a página pela "primeira vez"
        id_acesso = int(id_access) 
    
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        equip_access_edit = client.create_equipamento_acesso().get_access(id_acesso)
        
        if equip_access_edit is None:
            messages.add_message(request, messages.ERROR, equip_access_messages.get("invalid_equip_acess"))
            return redirect('equip.access.search.list') 
        
        equip_access_edit = equip_access_edit['equipamento_acesso']
        
        protocol_list = client.create_tipo_acesso().listar()
        
        
        form = EquipAccessForm(protocol_list,initial={'password': equip_access_edit.get('password'),
                                                      'second_password':equip_access_edit.get('enable_pass'),
                                                      'user':equip_access_edit.get('user'),
                                                      'protocol':equip_access_edit.get('tipo_acesso'),
                                                      'host':equip_access_edit.get('fqdn'),
                                                      'id_equip':equip_access_edit.get('equipamento')})
        
        lists['form'] = form
        lists['id_acesso'] = id_acesso
        lists['id_equip'] = equip_access_edit.get('equipamento')
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except KeyError, e:
        logger.error(e)
        
    return render_to_response(EQUIPMENTACESS_EDIT,lists,context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def delete(request):
    
    try:
      
        if request.method == 'POST':
        
            form = DeleteForm(request.POST)
        
            id_equip = request.POST['equip_id']
            
            flag = False
        
            if form.is_valid():
            
                # Get user
                auth = AuthSession(request.session)
                equipamento_acesso = auth.get_clientFactory().create_equipamento_acesso()
            
                # All ids to be deleted
                ids = split_to_array(form.cleaned_data['ids'])
            
                # All messages to display
                error_list = list()
            
                # Control others exceptions
                have_errors = False
            
                #return with list with equip
                # For each script selected to remove
                for id_equip_access in ids:
                    try:
                    
                        # Execute in NetworkAPI
                        equip_access = equipamento_acesso.get_access(id_equip_access)
                        equip_access = equip_access.get('equipamento_acesso')
                        equipamento_acesso.remover(equip_access.get('tipo_acesso'),id_equip)
                   
                    
                    except EquipamentoError, e:
                        # If isnt possible, add in error list
                        error_list.append(id_equip_access)
                    
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
                        if not flag:
                            flag = True
                            messages.add_message(request, messages.SUCCESS, equip_access_messages.get("success_remove"))
                    else:
                        messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
     
            else:
                messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
                if id_equip == "":
                    return redirect("equip.access.search.list")
            
            
            if id_equip is not None and id_equip != "":       
                
                return search_list_param(request, id_equip)
            else:
                
                messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
                return search_list_param(request, id_equip)
                
    except KeyError:
        return redirect("equip.access.search.list")