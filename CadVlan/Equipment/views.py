# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.permissions import EQUIPMENT_MANAGEMENT, ENVIRONMENT_MANAGEMENT, EQUIPMENT_GROUP_MANAGEMENT,\
    BRAND_MANAGEMENT
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Equipment.business import cache_list_equipment
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.templates import AJAX_AUTOCOMPLETE_LIST, EQUIPMENT_SEARCH_LIST, SEARCH_FORM_ERRORS,\
    AJAX_EQUIP_LIST, EQUIPMENT_FORM, EQUIPMENT_MODELO_AJAX, EQUIPMENT_MODELO,\
    EQUIPMENT_EDIT, EQUIPMENT_MARCAMODELO_FORM, EQUIPMENT_MARCA
from django.template.context import RequestContext
from CadVlan.forms import DeleteForm
from CadVlan.Equipment.forms import SearchEquipmentForm, EquipForm, MarcaForm,\
    ModeloForm
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
        lists['marcas'] = marcas.get('marca')
                
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
    
    #DADOS NECESSÁRIOS PARA AMMBAS REQUISIÇÕES - GET / POST
    lists = dict()
    lists['equip_id'] = id_equip
    # Get user
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
     
    #controlar erro no post para remontar formulario
    not_aut = False
    
    list_errors = []
    
    forms_aux = dict()
    #List All - Tipo Equipamento
    forms_aux['tipo_equipamento'] =  client.create_tipo_equipamento().listar().get('tipo_equipamento')
    #List All - Marcas
    forms_aux['marcas'] = client.create_marca().listar().get('marca')
    #List All - Grupos
    forms_aux['grupos'] = client.create_grupo_equipamento().listar().get('grupo')
    #List All - Ambientes 
    forms_aux['ambientes'] = client.create_ambiente().listar().get('ambiente')
    
    #VERIFICAR SE EQUIPAMENTO EXISTE, SENAO, RETORNAR A LISTAGEM
    try:
        equip = client.create_equipamento().listar_por_id(id_equip)
        equip = equip.get('equipamento')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect("equipment.search.list")
    
    
    ambientes = client.create_ambiente().listar_por_equip(id_equip)
    if (ambientes is not None):
        ambientes = ambientes.get('ambiente')
    else:
        ambientes = []      
    
    # Recuperar Grupos
    grupos = client.create_grupo_equipamento().listar_por_equip(id_equip)
    if (grupos is not None):
        grupos = grupos.get('grupo')
    else:
        grupos = []
    
    #LISTA PARA AUXILIAR FORM COM GRUPOS E AMBIENTES JA SELECIONADOS
    list_grupos = []
    list_ambientes = []
      
    try:
        
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
            
            lists['form'] = form
            
            if form.is_valid():
                
                grupos_escolhidos = form.cleaned_data['grupo']
                ambientes_escolhidos = form.cleaned_data['ambiente']
                nome = form.cleaned_data['nome']
                modelo = form.cleaned_data['modelo']
                tipo_equipamento = form.cleaned_data['tipo_equipamento']
                
                #Equipamento orquestração
                orquestracao = 1
                list_unremoved = []
                servidor_virtual = 10
                
                remove_group_cont = 0
                insert_group_cont = 0
                
                if str(orquestracao) in grupos_escolhidos and int(tipo_equipamento) != servidor_virtual:
                    messages.add_message(request, messages.ERROR, equip_messages.get("orquestracao_error"))
                    raise Exception
                else:
                    client.create_equipamento().edit(id_equip, nome, tipo_equipamento, modelo)
                    
                
                if (type(ambientes) == list):
                    for ambiente in ambientes:
                        client.create_equipamento_ambiente().remover(id_equip, ambiente['id'])
                else:
                    client.create_equipamento_ambiente().remover(id_equip, ambientes['id'])
                
                
                for ambiente in ambientes_escolhidos:
                    client.create_equipamento_ambiente().inserir(id_equip, ambiente)
                
                if (type(grupos)== list):
                    for grupo in grupos:
                        try:
                            client.create_grupo_equipamento().remove(id_equip, grupo['id'])
                            remove_group_cont = remove_group_cont + 1
                        except NetworkAPIClientError, e:
                            logger.error(e)
                            list_unremoved.append(grupo['id'])
                else:
                    try:
                        client.create_grupo_equipamento().remove(id_equip, grupos['id'])
                        remove_group_cont = remove_group_cont + 1
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        list_unremoved.append(grupos['id'])
                    
                if orquestracao in grupos_escolhidos:
                    if orquestracao not in list_unremoved:
                        try:                           
                            client.create_grupo_equipamento().associa_equipamento(id_equip, 1) 
                            insert_group_cont = insert_group_cont + 1                           
                        except NetworkAPIClientError, e:
                            logger.error(e)
                            messages.add_message(request, messages.ERROR, e)
                    
                for grupo in grupos_escolhidos:
                    if grupo != orquestracao:
                        if grupo not in list_unremoved:
                            try:
                                client.create_grupo_equipamento().associa_equipamento(id_equip, grupo)
                                insert_group_cont = insert_group_cont + 1
                            except NetworkAPIClientError, e:
                                not_aut = True
                                list_errors.append(e)
                try:
                    if remove_group_cont > 0 and insert_group_cont <= 0:
                        if  grupos is list:
                            for grupo in grupos:
                                client.create_grupo_equipamento().associa_equipamento(id_equip, grupo['id'])
                        else:
                            client.create_grupo_equipamento().associa_equipamento(id_equip, grupos['id'])
                except NetworkAPIClientError, e:
                    logger.error(e)
                        
                if not_aut:
                    
                    messages.add_message(request, messages.ERROR, list_errors[0])
                    
                    raise Exception
                        
                messages.add_message(request, messages.SUCCESS, equip_messages.get("equip_edit_sucess"))
                
                #redirecionar
                return redirect("equipment.search.list")
            
            #form invalido    
            else:    
                
                ips =  client.create_ip().find_ips_by_equip(id_equip)
                if ips.get('ips') is not None:
                    ips4 = ips.get('ips').get('ipv4')
                    ips6 = ips.get('ips').get('ipv6')
                        
                    if ips4 is not None:
                        if type(ips4) == list:
                                lists['ips4'] = ips4
                        else:
                                lists['ips4'] = [ips4]
                            
                    if ips6 is not None:
                        if type(ips6) == list:
                                lists['ips6'] = ips6
                        else:
                                lists['ips6'] = [ips6]
        
        #GET REQUEST
        else:
            try:
                ips =  client.create_ip().find_ips_by_equip(id_equip)
                if ips.get('ips') is not None:
                    ips4 = ips.get('ips').get('ipv4')
                    ips6 = ips.get('ips').get('ipv6')
                        
                    if ips4 is not None:
                        if type(ips4) == list:
                                lists['ips4'] = ips4
                        else:
                                lists['ips4'] = [ips4]
                            
                    if ips6 is not None:
                        if type(ips6) == list:
                                lists['ips6'] = ips6
                        else:
                                lists['ips6'] = [ips6]
               
                if type(grupos) == list:
                    for grupo in grupos:
                        list_grupos.append(grupo['id'])
                else:
                    list_grupos.append(grupos['id'])
                
              
                if (ambientes != None):
                    if type(ambientes) == list:
                        for ambiente in ambientes:
                            list_ambientes.append(ambiente['id'])
                    else:
                        list_ambientes.append(ambientes['id'])
                                       
                #Set Form
                modelos = client.create_modelo().listar_por_marca(equip.get('id_marca'))
                forms_aux['modelos'] = modelos.get('modelo')   
                lists['form'] = EquipForm(forms_aux,initial={"nome":equip.get('nome'),"tipo_equipamento":equip.get('id_tipo_equipamento'),"marca":equip.get('id_marca'),"modelo":equip.get('id_modelo'),"grupo":list_grupos,"ambiente":list_ambientes})
        
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
               
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        ips =  client.create_ip().find_ips_by_equip(id_equip)
        if ips.get('ips') is not None:
            ips4 = ips.get('ips').get('ipv4')
            ips6 = ips.get('ips').get('ipv6')
                        
            if ips4 is not None:
                if type(ips4) == list:
                    lists['ips4'] = ips4
                else:
                    lists['ips4'] = [ips4]
                            
                if ips6 is not None:
                    if type(ips6) == list:
                        lists['ips6'] = ips6
                    else:
                        lists['ips6'] = [ips6]
        
    except Exception, e:
        logger.error(e)
        ips =  client.create_ip().find_ips_by_equip(id_equip)
        if ips.get('ips') is not None:
            ips4 = ips.get('ips').get('ipv4')
            ips6 = ips.get('ips').get('ipv6')
                        
            if ips4 is not None:
                if type(ips4) == list:
                    lists['ips4'] = ips4
                else:
                    lists['ips4'] = [ips4]
                            
                if ips6 is not None:
                    if type(ips6) == list:
                        lists['ips6'] = ips6
                    else:
                        lists['ips6'] = [ips6]
        
  
        
             
    return render_to_response(EQUIPMENT_EDIT,lists,context_instance=RequestContext(request))

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
        
        