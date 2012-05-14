# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.permissions import EQUIPMENT_MANAGEMENT, ENVIRONMENT_MANAGEMENT, EQUIPMENT_GROUP_MANAGEMENT
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Equipment.business import cache_list_equipment
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.templates import AJAX_AUTOCOMPLETE_LIST, EQUIPMENT_SEARCH_LIST, SEARCH_FORM_ERRORS,\
    AJAX_EQUIP_LIST, EQUIPMENT_FORM, EQUIPMENT_MODELO_AJAX, EQUIPMENT_MODELO
from django.template.context import RequestContext
from CadVlan.forms import DeleteForm
from CadVlan.Equipment.forms import SearchEquipmentForm, EquipForm
from CadVlan.Util.utility import DataTablePaginator
from networkapiclient.Pagination import Pagination
from django.http import HttpResponseServerError, HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import loader
from CadVlan.messages import equip_messages

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def ajax_autocomplete_equips(request):
    try:
        
        equip_list = dict()
        
        # Get user auth
        auth = AuthSession(request.session)
        equipment = auth.get_clientFactory().create_equipamento()
        
        # Get list of equipments from cache
        equip_list = cache_list_equipment(equipment)
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response_ajax(AJAX_AUTOCOMPLETE_LIST, equip_list, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_GROUP_MANAGEMENT, "read": True}])
def ajax_list_equips(request):
    
    try:
        
        # If form was submited
        if request.method == "GET":
            
            # Get user auth
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            # Get all environments from NetworkAPI
            env_list = client.create_ambiente().list_all()
            # Get all equipment types from NetworkAPI
            type_equip_list = client.create_tipo_equipamento().listar()
            # Get all groups from NetworkAPI
            group_list = client.create_grupo_equipamento().listar()
            
            search_form = SearchEquipmentForm(env_list, type_equip_list, group_list, request.GET)
            
            if search_form.is_valid():
                
                name = search_form.cleaned_data["name"]
                iexact = search_form.cleaned_data["iexact"]
                environment = search_form.cleaned_data["environment"]
                equip_type = search_form.cleaned_data["type_equip"]
                group = search_form.cleaned_data["group"]
                ipv4 = search_form.cleaned_data["ipv4"]
                ipv6 = search_form.cleaned_data["ipv6"]
                
                if environment == "0":
                    environment = None
                if equip_type == "0":
                    equip_type = None
                if group == "0":
                    group = None
                
                if len(ipv4) > 0:
                    ip = ipv4
                elif len(ipv6) > 0:
                    ip = ipv6
                else:
                    ip = None
                    
                # Pagination
                columnIndexNameMap = { 0: '', 1: 'nome', 2 : 'tipo_equipamento', 3: 'grupos', 4: 'ip', 5: 'vlan', 6: 'ambiente', 7: '' }
                dtp = DataTablePaginator(request, columnIndexNameMap)
                
                # Make params
                dtp.build_server_side_list()
                
                # Set params in simple Pagination class
                pag = Pagination(dtp.start_record, dtp.end_record, dtp.asorting_cols, dtp.searchable_columns, dtp.custom_search)
                
                # Call API passing all params
                equips = client.create_equipamento().find_equips(name, iexact, environment, equip_type, group, ip, pag)
                
                if not equips.has_key("equipamento"):
                    equips["equipamento"] = []
                    
                # Returns JSON
                return dtp.build_response(equips["equipamento"], equips["total"], AJAX_EQUIP_LIST, request)
            
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
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_GROUP_MANAGEMENT, "read": True}])
def search_list(request):
    
    try:
        
        lists = dict()
        lists["delete_form"] = DeleteForm()
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get all environments from NetworkAPI
        env_list = client.create_ambiente().list_all()
        # Get all equipment types from NetworkAPI
        type_equip_list = client.create_tipo_equipamento().listar()
        # Get all groups from NetworkAPI
        group_list = client.create_grupo_equipamento().listar()
        
        search_form = SearchEquipmentForm(env_list, type_equip_list, group_list)
        
        lists["search_form"] = search_form
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(EQUIPMENT_SEARCH_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_GROUP_MANAGEMENT, "read": True}])
def equip_form(request):
    try:
        
        lists = dict()
        #Enviar listas para formar os Selects do formulário
        forms_aux = dict()
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        #List All - Tipo Equipamento
        forms_aux['tipo_equipamento'] =  client.create_tipo_equipamento().listar().get('tipo_equipamento')
        #List All - Marcas
        forms_aux['marcas'] = client.create_marca().listar().get('marca')
        #List All - Grupos
        forms_aux['grupos'] = client.create_grupo_equipamento().listar().get('grupo')
        #List All - Ambientes
        forms_aux['ambientes'] = client.create_ambiente().listar().get('ambiente')
        
        if request.method == 'POST':
            
            try:
                marca = int(request.POST['marca'])
            except:
                marca = 0
            
            if marca  > 0 :
                forms_aux['modelos'] = client.create_modelo().listar_por_marca(marca).get('modelo')
            else:
                forms_aux['modelos'] = None
                
            form = EquipForm(forms_aux, request.POST)
            
            if form.is_valid():
                
                lists['form'] = form
                
                grupos = form.cleaned_data['grupo']
                ambientes = form.cleaned_data['ambiente']
                nome = form.cleaned_data['nome']
                marca = form.cleaned_data['marca']
                modelo = form.cleaned_data['modelo']
                tipo_equipamento = form.cleaned_data['tipo_equipamento']
                
                grupo_aux = grupos[0]
                
                equip = client.create_equipamento().inserir(nome, tipo_equipamento, modelo, grupo_aux)
                equip = equip.get('equipamento').get('id')
                for g in grupos:
                    if g != grupo_aux:
                        client.create_equipamento().associar_grupo(equip, g)
                        
                for amb in ambientes:
                    client.create_equipamento_ambiente().inserir(equip, amb)
                    
                messages.add_message(request, messages.SUCCESS, equip_messages.get("equip_sucess"))
                
                #redirecionar
                return redirect("equipment.search.list")
                
            else:
                lists['form'] = form
        #get        
        else:
            #Set Form
            forms_aux['modelos'] = None
            
            lists['form'] = EquipForm(forms_aux)
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(EQUIPMENT_FORM,lists,context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_GROUP_MANAGEMENT, "read": True}])
def ajax_modelo_equip(request, id_marca):
    try:
        
        lists = dict()
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
            
        marca = int(id_marca)
            
        if  marca > 0:
            modelos = client.create_modelo().listar_por_marca(marca)
            lists['modelos'] = modelos.get('modelo')
                
            # Returns HTML
            response = HttpResponse(loader.render_to_string(EQUIPMENT_MODELO, lists, context_instance=RequestContext(request)))
            # Send response status with error
            response.status_code = 200
            return response
                
        else:
                
            # Returns HTML
            response = HttpResponse(loader.render_to_string(EQUIPMENT_MODELO, lists, context_instance=RequestContext(request)))
            # Send response status with error
            response.status_code = 200
            return response
        
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    except:
        logger.error('Erro na requição Ajax de Busca de Modelo do Equipamento por Marca') 
    # Returns HTML
    response = HttpResponse(loader.render_to_string(EQUIPMENT_MODELO, lists, context_instance=RequestContext(request)))
    # Send response status with error
    response.status_code = 200
    return response 