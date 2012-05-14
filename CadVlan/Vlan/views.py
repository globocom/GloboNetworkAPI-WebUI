# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from networkapiclient.Pagination import Pagination
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, VlanNaoExisteError
from django.contrib import messages
from CadVlan.permissions import VLAN_MANAGEMENT, ENVIRONMENT_MANAGEMENT, NETWORK_TYPE_MANAGEMENT
from CadVlan.forms import DeleteForm
from CadVlan.templates import VLAN_SEARCH_LIST, VLANS_DEETAIL, AJAX_VLAN_LIST, SEARCH_FORM_ERRORS, AJAX_VLAN_AUTOCOMPLETE,\
    VLAN_FORM, VLAN_EDIT, AJAX_SUGGEST_NAME
from CadVlan.Vlan.forms import SearchVlanForm, VlanForm
from CadVlan.Util.converters.util import replace_id_to_name
from CadVlan.Util.utility import DataTablePaginator
from django.http import HttpResponseServerError, HttpResponse,\
    HttpResponseRedirect
from django.template import loader
from CadVlan.Vlan.business import montaIPRede , cache_list_vlans
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.messages import vlan_messages
from django.core.urlresolvers import reverse

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def ajax_list_vlans(request):
    
    try:
        
        # If form was submited
        if request.method == "GET":
            
            # Get user auth
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            # Get all environments from NetworkAPI
            env_list = client.create_ambiente().list_all()
            # Get all network types from NetworkAPI
            net_list = client.create_tipo_rede().listar()
            
            search_form = SearchVlanForm(env_list, net_list, request.GET)
            
            if search_form.is_valid():
                
                number = search_form.cleaned_data["number"]
                name = search_form.cleaned_data["name"]
                iexact = search_form.cleaned_data["iexact"]
                environment = search_form.cleaned_data["environment"]
                net_type = search_form.cleaned_data["net_type"]
                ip_version = search_form.cleaned_data["ip_version"]
                networkv4 = search_form.cleaned_data["networkv4"]
                networkv6 = search_form.cleaned_data["networkv6"]
                subnet = search_form.cleaned_data["subnet"]
                acl = search_form.cleaned_data["acl"]
                
                if environment == "0":
                    environment = None
                if net_type == "0":
                    net_type = None
                
                if len(networkv4) > 0:
                    network = networkv4
                elif len(networkv6) > 0:
                    network = networkv6
                else:
                    network = None
                    
                # Pagination
                columnIndexNameMap = { 0: '', 1: '', 2: 'num_vlan', 3 : 'nome', 4: 'ambiente', 5: 'tipo_rede', 6: 'network', 7: '', 8: 'acl_file_name' }
                dtp = DataTablePaginator(request, columnIndexNameMap)
                
                # Make params
                dtp.build_server_side_list()
                
                # Set params in simple Pagination class
                pag = Pagination(dtp.start_record, dtp.end_record, dtp.asorting_cols, dtp.searchable_columns, dtp.custom_search)
                
                # Call API passing all params
                vlans = client.create_vlan().find_vlans(number, name, iexact, environment, net_type, network, ip_version, subnet, acl, pag)
                
                if not vlans.has_key("vlan"):
                    vlans["vlan"] = []
                    
                # Returns JSON
                return dtp.build_response(vlans["vlan"], vlans["total"], AJAX_VLAN_LIST, request)
            
            else:
                # Remake search form
                lists = dict()
                lists["search_form"] = search_form
                
                # Returns HTML
                response = HttpResponse(loader.render_to_string(SEARCH_FORM_ERRORS, lists, context_instance=RequestContext(request)))
                # Send response status with error
                response.status_code = 412
                return response
            
    except NetworkAPIClientError, e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')
    except BaseException, e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}])
def ajax_autocomplete_vlans(request):
    try:
        
        vlan_list = dict()
        
        # Get user auth
        auth = AuthSession(request.session)
        vlan = auth.get_clientFactory().create_vlan()
        
        # Get list of equipments from cache
        vlan_list = cache_list_vlans(vlan)
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response_ajax(AJAX_VLAN_AUTOCOMPLETE, vlan_list, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def search_list(request):
    
    try:
        
        lists = dict()
        lists["delete_form"] = DeleteForm()
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get all environments from NetworkAPI
        env_list = client.create_ambiente().list_all()
        # Get all network types from NetworkAPI
        net_list = client.create_tipo_rede().listar()
        
        lists["search_form"] = SearchVlanForm(env_list, net_list)
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(VLAN_SEARCH_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "read": True}])
def list_by_id(request, id_vlan):
    
    lists = dict()
    listaIps = []
    lista = []
    
    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        #recuperando lista de vlans
        vlans = client.create_vlan().get(id_vlan)
        
        #recuperando ambientes
        environment = client.create_ambiente().listar()
        environment = environment.get('ambiente')
        vlans = vlans.get('vlan')
        
        for ambiente in environment:
            if vlans.get('ambiente') == ambiente.get('id'):
                vlans['ambiente'] = ambiente.get('nome_divisao')+ ' - ' + ambiente.get('nome_ambiente_logico') + ' - ' + ambiente.get('nome_grupo_l3')
                break
            
        #FE - PORTAL - CORE/DENSIDADE
        lists['vlan'] = vlans
        lists['idvlan'] = id_vlan
        
        vlans = None
        
        vlans = client.create_vlan().get(id_vlan)
        
        vlans = vlans.get('vlan')
        
        redesIPV4 = vlans["redeipv4"]
        if len(redesIPV4) > 0:
            listaIps.append(montaIPRede(redesIPV4))
            
        redesIPV6 = vlans.get("redeipv6")
        if  len(redesIPV6) > 0:
            listaIps.append(montaIPRede(redesIPV6,False))
            
        for item in listaIps:
            for i in item:
                lista.append(i)
                
        tipo_rede = client.create_tipo_rede().listar()
        
        lista = replace_id_to_name(lista, tipo_rede['tipo_rede'], "network_type", "id", "nome")
        
        lists['net_vlans'] = lista
        
        return render_to_response(VLANS_DEETAIL, lists , context_instance=RequestContext(request))
    
    except VlanNaoExisteError, e:
        logger.error(e)
        return redirect('vlan.search.list') 
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except TypeError,e:
        logger.error(e)
        messages.add_message(request,messages.ERROR,e)
        
    return render_to_response(VLANS_DEETAIL,lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def vlan_form(request):
    
    lists = dict()
    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        environment = client.create_ambiente().list_all()
        
        if request.method == 'POST':
            
            form = VlanForm(environment,request.POST)
            
            lists['form'] = form
            
            if form.is_valid():
                
                name = form.cleaned_data['name'] 
                acl_file = form.cleaned_data['acl_file']
                description = form.cleaned_data['description']
                number = form.cleaned_data['number']
                environment_id = form.cleaned_data['environment']
                
                #Salva a Vlan
                vlan = client.create_vlan().insert_vlan(environment_id, name, number, description, acl_file)
                messages.add_message(request, messages.SUCCESS, vlan_messages.get("vlan_sucess"))
                id_vlan = vlan.get('vlan').get('id')
                #redireciona para a listagem de vlans
                return HttpResponseRedirect(reverse('vlan.list.by.id', args=[id_vlan]))
        #Get
        if request.method == 'GET':
            lists['form'] = VlanForm(environment)
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VLAN_FORM,lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def vlan_edit(request,id_vlan):
    
    lists = dict()
    lists['id_vlan'] = id_vlan
    
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        try:
            vlan = client.create_vlan().get(id_vlan)
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list') 
        
        
        if request.method == 'GET':
            
            environment = client.create_ambiente().list_all()
            vlan = vlan.get("vlan")
            
            lists['acl_valida'] = vlan.get("acl_valida")       
            lists['form'] = VlanForm(environment,initial={'name':vlan.get('nome'),"number":vlan.get('num_vlan'),"environment":vlan.get("ambiente"),"description":vlan.get('descricao'),"acl_file":vlan.get('acl_file_name')})
        
        if request.method == 'POST':
           
            environment = client.create_ambiente().list_all()
            form = VlanForm(environment,request.POST)
            lists['form'] = form
            vlan = vlan.get('vlan')
            lists['acl_valida'] = vlan.get("acl_valida")
            
            if form.is_valid():
                
                nome = form.cleaned_data['name']
                numero = form.cleaned_data['number']
                acl_file = form.cleaned_data['acl_file']
                descricao = form.cleaned_data['description']
                ambiente = form.cleaned_data['environment']
                
                #client.editar
                client.create_vlan().edit_vlan(ambiente, nome, numero, descricao, acl_file, id_vlan)
                messages.add_message(request, messages.SUCCESS, vlan_messages.get("vlan_edit_sucess"))
                
                return HttpResponseRedirect(reverse('vlan.list.by.id', args=[id_vlan]))
             
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(VLAN_EDIT,lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def ajax_acl_name_suggest(request):
    lists = dict()
    try:    
            
            nome = request.GET['nome']
            id_ambiente = request.GET['id_ambiente']
            
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            environment = client.create_ambiente().buscar_por_id(id_ambiente).get('ambiente')
            
            suggest_name = nome+environment['nome_ambiente_logico']
            lists['suggest_name'] = suggest_name
            
            # Returns HTML
            response = HttpResponse(loader.render_to_string(AJAX_SUGGEST_NAME, lists, context_instance=RequestContext(request)))
            # Send response status with error
            response.status_code = 200
            return response
            
    except:
        
        lists['suggest_name'] = ''
        # Returns HTML
        response = HttpResponse(loader.render_to_string(AJAX_SUGGEST_NAME, lists, context_instance=RequestContext(request)))
        # Send response status with error
        response.status_code = 200
        return response
        
@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])           
def ajax_validate_acl(request):
    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        vlan = request.GET['vlan']
        
        client.create_vlan().validar(vlan)
        
        messages.add_message(request, messages.SUCCESS, vlan_messages.get("acl_file_sucess"))
        
        # Returns HTML
        response = HttpResponse()
        # Send response status with error
        response.status_code = 200
        return response
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        # Returns HTML
        response = HttpResponse()
        # Send response status with error
        response.status_code = 412
        return response
        