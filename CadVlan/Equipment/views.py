# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm, access_external
from CadVlan.permissions import EQUIPMENT_MANAGEMENT, ENVIRONMENT_MANAGEMENT, EQUIPMENT_GROUP_MANAGEMENT, BRAND_MANAGEMENT,\
    VIP_ALTER_SCRIPT
from networkapiclient.exception import NetworkAPIClientError, EquipamentoError, UserNotAuthorizedError
from django.contrib import messages
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Equipment.business import cache_list_equipment
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.templates import AJAX_AUTOCOMPLETE_LIST, EQUIPMENT_SEARCH_LIST, SEARCH_FORM_ERRORS, AJAX_EQUIP_LIST, EQUIPMENT_FORM, EQUIPMENT_MODELO, EQUIPMENT_EDIT, EQUIPMENT_MARCAMODELO_FORM, EQUIPMENT_MARCA,\
    EQUIPMENT_VIEW_AJAX
from django.template.context import RequestContext
from CadVlan.forms import DeleteForm
from CadVlan.Equipment.forms import SearchEquipmentForm, EquipForm, MarcaForm, ModeloForm
from CadVlan.Util.utility import DataTablePaginator, validates_dict
from networkapiclient.Pagination import Pagination
from django.http import HttpResponseServerError, HttpResponse
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from CadVlan.messages import equip_messages, error_messages,\
    request_vip_messages
from CadVlan.Util.converters.util import split_to_array
import json

logger = logging.getLogger(__name__)

@log
@login_required
def ajax_check_real(request, id_vip):

    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get reals related
        vip = client.create_vip().get_by_id(id_vip).get("vip")        
        reals = [vip.get('reals')['real'],] if type(vip.get('reals')['real']) is dict else vip.get('reals')['real']
        
        response_data = {}
        response_data['count'] = len(reals)
            
        return HttpResponse(json.dumps(response_data), content_type="application/json")
        
    except NetworkAPIClientError, e:
        logger.error(e)
        return HttpResponse(json.dumps(e), content_type="application/json")
        

@log
@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "write": True},])
def ajax_view_real(request, id_equip):
    
    lists= dict()
    return ajax_view_real_shared(request, id_equip, lists)
    

def ajax_view_real_shared(request, id_equip, lists):
    
    try:
        
        lists['equip_id'] = id_equip
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get reals related
        vips_reals = client.create_equipamento().get_real_related(id_equip)
        lists['vips'] = [vips_reals.get('vips'),] if type(vips_reals.get('vips')) is dict else vips_reals.get('vips')
        lists['equip_name'] = vips_reals.get('equip_name')
        
        # Returns HTML
        response = HttpResponse(loader.render_to_string(EQUIPMENT_VIEW_AJAX, lists, context_instance=RequestContext(request)))
        response.status_code = 200
        return response
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
         
    # Returns HTML
    response = HttpResponse(loader.render_to_string(EQUIPMENT_VIEW_AJAX, lists, context_instance=RequestContext(request)))
    # Send response status with error
    response.status_code = 412
    return response  

@log
@login_required
@has_perm([{"permission": VIP_ALTER_SCRIPT, "write": True},])
def ajax_remove_real(request, id_vip):
    
    try:
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        lists = dict()
        
        ip        = request.GET['ip']
        port_vip  = request.GET['port_vip']
        port_real = request.GET['port_real']
        equip_id  = request.GET['equip_id']
        real_name = request.GET['real_name']
    
        # Remove all reals related
        if id_vip == '0':
            vips_reals = client.create_equipamento().get_real_related(equip_id).get('vips')
            vips_reals = [vips_reals,] if type(vips_reals) is dict else vips_reals
            vip_ids = list()
            for vip in vips_reals:
                vip_ids.append(vip['id_vip'])
            
            vip_ids = set(vip_ids)
            
            for id in vip_ids:
                lists = remove_reals_from_equip(client, id, lists, ip, port_vip, port_real, real_name, True)
            
        else:
            lists = remove_reals_from_equip(client, id_vip, lists, ip, port_vip, port_real, real_name)
        
        return ajax_view_real_shared(request, equip_id, lists)
    
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

def remove_reals_from_equip(client, id_vip, lists, ip = '', port_vip = '', port_real = '', real_name = '', remove_all = False):
    try:
        vip = client.create_vip().get_by_id(id_vip).get("vip")        
    
        reals    = [vip.get('reals')['real'],] if type(vip.get('reals')['real']) is dict else vip.get('reals')['real']
        priority = [vip.get('reals_prioritys')['reals_priority'],] if type(vip.get('reals_prioritys')['reals_priority']) is unicode else vip.get('reals_prioritys')['reals_priority']
        weight   = [vip.get('reals_weights')['reals_weight'],] if type(vip.get('reals_weights')['reals_weight']) is unicode else vip.get('reals_weights')['reals_weight']
        
        index_to_remove = list()
        
        if remove_all:
            for i in range(len(reals)):
                if reals[i]['real_name'] == real_name:
                    index_to_remove.append(i)
        else:
            for i in range(len(reals)):
                if reals[i]['real_ip'] == ip and reals[i]['port_vip'] == port_vip and reals[i]['port_real'] == port_real and reals[i]['real_name'] == real_name:
                    index_to_remove.append(i)
        
        for index in reversed(index_to_remove):
            del reals[index]
            del priority[index]
            del weight[index]
            
        
        client.create_vip().edit_reals(id_vip, 'method_bal', reals, priority, weight, 0)
        
        lists['message'] = request_vip_messages.get('real_remove')
        lists['msg_type'] = 'success'
    
    except Exception, e:
        lists['msg_type'] = 'error'
        lists['message'] = e
    
    
    return lists

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

@csrf_exempt
@access_external()
@log
def ajax_autocomplete_equips_external(request, form_acess, client):
    try:
        
        equip_list = dict()
        equipment = client.create_equipamento()
        
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
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_GROUP_MANAGEMENT, "read": True}])
def equip_form(request):
    try:
        equip = None
        
        lists = dict()
        #Enviar listas para formar os Selects do formulário
        forms_aux = dict()
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        #List All - Tipo Equipamento
        forms_aux['tipo_equipamento'] =  client.create_tipo_equipamento().listar().get('equipment_type')
        #List All - Brands
        forms_aux['marcas'] = client.create_marca().listar().get('brand')
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
                forms_aux['modelos'] = client.create_modelo().listar_por_marca(marca).get('model')
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
                        client.create_grupo_equipamento().associa_equipamento(equip, g)
                        
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
        if equip is not None:
            client.create_equipamento().remover(equip)
        
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
            lists['modelos'] = modelos.get('model')
                
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

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_GROUP_MANAGEMENT, "read": True}])
def ajax_marca_equip(request):
    try:
        
        lists = dict()
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        marcas = client.create_marca().listar()
        lists['marcas'] = marcas.get('brand')
                
        # Returns HTML
        response = HttpResponse(loader.render_to_string(EQUIPMENT_MARCA, lists, context_instance=RequestContext(request)))
        # Send response status with error
        response.status_code = 200
        return response
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    except:
        logger.error('Erro na requição Ajax de Atualização de Marcas') 
    # Returns HTML
    response = HttpResponse(loader.render_to_string(EQUIPMENT_MARCA, lists, context_instance=RequestContext(request)))
    # Send response status with error
    response.status_code = 200
    return response

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_GROUP_MANAGEMENT, "read": True}])
def equip_edit(request,id_equip):
    
    lists = dict()
    lists['equip_id'] = id_equip
    
    # Get user
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
     
    is_error = False
    
    forms_aux = dict()
    forms_aux['tipo_equipamento'] =  client.create_tipo_equipamento().listar().get('equipment_type')
    forms_aux['marcas'] = client.create_marca().listar().get('brand')
    forms_aux['grupos'] = client.create_grupo_equipamento().listar().get('grupo')
    forms_aux['ambientes'] = client.create_ambiente().listar().get('ambiente')
    
    try:
        equip = client.create_equipamento().listar_por_id(id_equip).get('equipamento')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect("equipment.search.list")
    
    environments = client.create_ambiente().listar_por_equip(id_equip)
    
    if (environments is not None):
        environments= validates_dict(environments, 'ambiente')
    else:
        environments = []      
    
    groups = client.create_grupo_equipamento().listar_por_equip(id_equip)
    
    if (groups is not None):
        groups = validates_dict(groups, 'grupo')
    else:
        groups = []
    
    list_groups = []
    list_environments = []
      
    try:
        
        if request.method == 'POST':
            
            try:
                marca = int(request.POST['marca'])
            except:
                marca = 0
            
            if marca  > 0 :
                forms_aux['modelos'] = client.create_modelo().listar_por_marca(marca).get('model')
            else:
                forms_aux['modelos'] = None
                
            form = EquipForm(forms_aux, request.POST)
            
            lists['form'] = form
            
            if form.is_valid():
                
                groups_chosen = form.cleaned_data['grupo']
                environments_chosen = form.cleaned_data['ambiente']
                name = form.cleaned_data['nome']
                model = form.cleaned_data['modelo']
                type_equipment = form.cleaned_data['tipo_equipamento']
                
                #Equipment orquestração
                orquestracao = 1
                server_virtual = 10
                
                if str(orquestracao) in groups_chosen and int(type_equipment) != server_virtual:
                    messages.add_message(request, messages.ERROR, equip_messages.get("orquestracao_error"))
                    raise Exception
                    
                    
                #diff environments
                environments_list = []
                for environment in environments:
                    environments_list.append(environment['id'])
                    
                environments_rm = list( set(environments_list) - set(environments_chosen) )
                environments_add = list( set(environments_chosen) - set(environments_list) )
                
                #Remove environment
                for env in environments_rm:
                    try:
                        client.create_equipamento_ambiente().remover(id_equip, env)
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        is_error = True
                        messages.add_message(request, messages.ERROR, e)
              
                #ADD environment
                for env in environments_add:
                    try:
                        client.create_equipamento_ambiente().inserir(id_equip, env)
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        is_error = True
                        messages.add_message(request, messages.ERROR, e)                    

                #diff groups
                groups_list = []
                for group in groups:
                    groups_list.append(group['id'])
                    
                groups_rm = list( set(groups_list) - set(groups_chosen) )
                groups_add = list( set(groups_chosen) - set(groups_list) )
                
                # Add groups before because the equipment cannot be groupless
                for group in groups_add:
                    try:
                        client.create_grupo_equipamento().associa_equipamento(id_equip, group)
                    except UserNotAuthorizedError, e:
                        logger.error(e)
                        is_error = True
                        
                        for grp in forms_aux['grupos']:
                            if grp["id"] == group:
                                messages.add_message(request, messages.ERROR, equip_messages.get("error_associate_group") % grp["nome"] )
                                raise Exception
                                break
                    
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        is_error = True

                # Remove groups
                for group in groups_rm:
                    try:
                        client.create_grupo_equipamento().remove(id_equip, group)
                    except UserNotAuthorizedError, e:
                        logger.error(e)
                        is_error = True
                        
                        for grp in forms_aux['grupos']:
                            if grp["id"] == group:
                                messages.add_message(request, messages.ERROR, equip_messages.get("error_disassociate_group") % grp["nome"] )
                            
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        is_error = True
                
                # edit name
                client.create_equipamento().edit(id_equip, name, type_equipment, model)        
                        
                if is_error:
                    raise Exception
                
                messages.add_message(request, messages.SUCCESS, equip_messages.get("equip_edit_sucess"))
                
                return redirect("equipment.search.list")
            
            #form invalid    
            else:    
                
                lists = list_ips_edit_equip(lists, id_equip, client)
                
        #GET REQUEST
        else:
            try:
                
                lists = list_ips_edit_equip(lists, id_equip, client)
           
                for group in groups:
                    list_groups.append(group['id'])
                
              
                if (environments != None):
                    for environment in environments:
                        list_environments.append(environment['id'])
                
                #Set Form
                modelos = client.create_modelo().listar_por_marca(equip.get('id_marca'))
                forms_aux['modelos'] = modelos.get('model')   
                lists['form'] = EquipForm(forms_aux,initial={"nome":equip.get('nome'),"tipo_equipamento":equip.get('id_tipo_equipamento'),"marca":equip.get('id_marca'),"modelo":equip.get('id_modelo'),"grupo":list_groups, "ambiente":list_environments})
        
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
               
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists = list_ips_edit_equip(lists, id_equip, client)
        
    except Exception, e:
        logger.error(e)
        lists = list_ips_edit_equip(lists, id_equip, client)
             
    return render_to_response(EQUIPMENT_EDIT,lists,context_instance=RequestContext(request))

def list_ips_edit_equip(lists, id_equip, client):
    try:
        
        ips =  client.create_ip().find_ips_by_equip(id_equip)
        if ips.get('ips') is not None:
            
            ips4 = validates_dict(ips.get('ips'), 'ipv4')
            ips6 = validates_dict(ips.get('ips'), 'ipv6')
            
            if ips4 is not None:
                    lists['ips4'] = ips4
            if ips6 is not None:
                    lists['ips6'] = ips6

    except Exception, e:
        logger.error(e)
        
    return lists
        

@log
@login_required
@has_perm([{"permission": BRAND_MANAGEMENT, "write": True}])
def marca_form(request):
    
    lists = dict()
    
    #Primeira aba de cadastro de marcas
    lists['aba'] = 0

    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        marcas = client.create_marca().listar()
        
        lists['form_modelo'] = ModeloForm(marcas)
        lists['form_marca'] = MarcaForm()  
        
        if request.method == 'POST':
            
            form = MarcaForm(request.POST)
            
            if form.is_valid():
                
                nome = form.cleaned_data['nome']
                
                client.create_marca().inserir(nome)
        
                messages.add_message(request, messages.SUCCESS, equip_messages.get("marca_sucess"))
                
                return render_to_response(EQUIPMENT_MARCAMODELO_FORM,lists,context_instance=RequestContext(request))
            
            #Form Invalid
            else:
                lists['form_marca'] = form
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(EQUIPMENT_MARCAMODELO_FORM,lists,context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": BRAND_MANAGEMENT, "write": True}])
def modelo_form(request):
    
    lists = dict()
    #Segunda aba de cadastro de modelos
    lists['aba'] = 1
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        marcas = client.create_marca().listar()
        
        lists['form_modelo'] = ModeloForm(marcas)
        lists['form_marca'] = MarcaForm()
        
        if request.method == 'POST':
            
            form = ModeloForm(marcas,request.POST)
        
            if form.is_valid():
                
                marca = form.cleaned_data['marca']
                nome = form.cleaned_data['nome']
                
                client.create_modelo().inserir(marca, nome)
                
                messages.add_message(request, messages.SUCCESS, equip_messages.get("modelo_sucess"))
                
                return render_to_response(EQUIPMENT_MARCAMODELO_FORM,lists,context_instance=RequestContext(request))
            
            #Form Invalid
            else:
                lists['form_modelo'] = form
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(EQUIPMENT_MARCAMODELO_FORM,lists,context_instance=RequestContext(request))
    

        
@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_GROUP_MANAGEMENT, "read": True}])
def delete_all(request):
    
    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_equip = auth.get_clientFactory().create_equipamento()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])
            
            delete_equipments_shared(request, client_equip, ids)
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('equipment.search.list')

def delete_equipments_shared(request, client_equip, ids):
    # All messages to display
    error_list = list()

    # Control others exceptions
    have_errors = False

    # For each equip selected to remove
    for id_equip in ids:
        try:

            # Execute in NetworkAPI
            client_equip.remover(id_equip);
            
        except EquipamentoError, e:
            error_list.append(id_equip)

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
        messages.add_message(request, messages.SUCCESS, equip_messages.get("success_remove"))

    else:
        messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_GROUP_MANAGEMENT, "read": True}])
def delete_equipment(request, id_equip):
    """
    Method called from modal of equipment's reals
    """
    
    # Get user
    auth = AuthSession(request.session)
    client_equip = auth.get_clientFactory().create_equipamento()
    
    delete_equipments_shared(request, client_equip, [id_equip,])

    # Redirect to list_all action
    return redirect('equipment.search.list')
