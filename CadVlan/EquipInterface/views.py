# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import EQUIPMENT_INTERFACE_SEARCH_LIST, EQUIPMENT_INTERFACE_FORM, EQUIPMENT_INTERFACE_SEVERAL_FORM,\
    EQUIPMENT_INTERFACE_EDIT_FORM, EQUIPMENT_INTERFACE_CONNECT_FORM
from CadVlan.settings import PATCH_PANEL_ID
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, InterfaceNaoExisteError, NomeInterfaceDuplicadoParaEquipamentoError
from django.contrib import messages
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.forms import DeleteForm, SearchEquipForm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.messages import error_messages, equip_interface_messages
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from CadVlan.EquipInterface.forms import AddInterfaceForm, AddSeveralInterfaceForm,\
    ConnectForm
from CadVlan.EquipInterface.business import make_initials_and_params
from CadVlan.Util.extends.formsets import formset_factory


logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def search_list(request):
    
    try:
        
        lists = dict();
        lists['search_form'] = SearchEquipForm()
        lists['del_form'] = DeleteForm()
        
        if request.method == "GET":
            
            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            if request.GET.__contains__('equip_name'):
                lists['search_form'] = search_form = SearchEquipForm(request.GET)
                
                if search_form.is_valid():
                    
                    # Get equip name in form
                    name_equip = search_form.cleaned_data['equip_name']
                    
                    # Get equipment by name from NetworkAPI
                    equipment = client.create_equipamento().listar_por_nome(name_equip)['equipamento']
                    
                    # Get all interfaces by equipment id
                    equip_interface_list = client.create_interface().list_all_by_equip(equipment['id'])
                    
                    init_map = {'equip_name': equipment['nome'], 'equip_id': equipment['id']}
                    
                    # New form
                    del_form = DeleteForm(initial=init_map)
                    
                    # Send to template
                    lists['del_form'] = del_form
                    lists['search_form'] = search_form
                    
                    if equip_interface_list.has_key('interfaces'):
                        lists['equip_interface'] = equip_interface_list['interfaces']
                    if equipment['id_tipo_equipamento'] == str(PATCH_PANEL_ID):
                        lists['pp'] = "1"
                    
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(EQUIPMENT_INTERFACE_SEARCH_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def delete_all(request):
    
    equip_nam = request.POST['equip_name']
    
    if request.method == 'POST':
        
        form = DeleteForm(request.POST)
        
        if form.is_valid():
            
            # Get user
            auth = AuthSession(request.session)
            equip_interface = auth.get_clientFactory().create_interface()
            
            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])
            equip_nam = form.cleaned_data['equip_name']
            
            # Control others exceptions
            have_errors = False
            
            # For each interface selected
            for id_es in ids:
                try:
                    
                    # Remove in NetworkAPI
                    equip_interface.remover(id_es)
                    
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break
                    
            # If all has ben removed
            if have_errors == False:
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_remove"))
                
            else:
                messages.add_message(request, messages.WARNING, error_messages.get("can_not_remove_error"))
                
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
            
    # Redirect to list_all action
    url_param = reverse("equip.interface.search.list")
    if len(equip_nam) > 2:
        url_param = url_param + "?equip_name=" + equip_nam
    return HttpResponseRedirect(url_param)

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def add_form(request, equip_name):
    
    lists = dict()
    
    # Get user
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    
    try:
        equip = client.create_equipamento().listar_por_nome(equip_name)
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('equip.interface.search.list')
    
    equip = equip.get('equipamento')
    
    brand = equip['id_marca'] if equip['id_tipo_equipamento'] != "2" else "0"
    
    lists['equip_type'] = equip['id_tipo_equipamento']
    lists['brand'] = brand
    lists['form'] = AddInterfaceForm(brand, 0, initial={'equip_name': equip['nome'], 'equip_id': equip['id']})
    
    # If form was submited
    if request.method == "POST":
        
        form = AddInterfaceForm(brand, 0, request.POST)
        
        try:
            
            if form.is_valid():
                
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                protected = form.cleaned_data['protected']
                
                client.create_interface().inserir(name, protected, description, None, None, equip['id'])
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_insert"))
                
                # Redirect to list_all action
                url_param = reverse("equip.interface.search.list")
                if len(equip_name) > 2:
                    url_param = url_param + "?equip_name=" + equip_name
                return HttpResponseRedirect(url_param)
            
            else:
                lists['form'] = form
                
        except NetworkAPIClientError, e:
                logger.error(e)
                lists['form'] = form
                messages.add_message(request, messages.ERROR, e)
            
    return render_to_response(EQUIPMENT_INTERFACE_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def add_several_forms(request,equip_name):
    
    lists = dict()
    
    #Get User
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    
    try:
        equip = client.create_equipamento().listar_por_nome(equip_name)
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('equip.interface.search.list')
    
    equip = equip.get('equipamento')
    
    brand = equip['id_marca'] if equip['id_tipo_equipamento'] != "2" else "0"
    divisor = "/" if (brand == '3' or brand == '5') else ":" if brand == "0" else "." if brand == '4' else ""
    
    list_brands = [2,3,4,5]
    
    if int(brand) not in list_brands:
        # Redirect to list_all action
        messages.add_message(request, messages.ERROR, equip_interface_messages.get("brand_error"))
        url_param = reverse("equip.interface.search.list")
        if len(equip_name) > 2:
            url_param = url_param + "?equip_name=" + equip_name
        return HttpResponseRedirect(url_param)
    
    if request.method == 'POST':
        
        form = AddSeveralInterfaceForm(brand,request.POST)
        lists['form'] = form
            
        if form.is_valid():
            
            name = form.cleaned_data['name']
            last_piece_name = form.cleaned_data['last_piece_name']
            last_piece_name2 = form.cleaned_data['last_piece_name2']
            description = form.cleaned_data['description']
            protected = form.cleaned_data['protected']
            campos = form.cleaned_data['campos']
            combo = form.cleaned_data['combo']
            
            if (last_piece_name > last_piece_name2):
                messages.add_message(request, messages.ERROR, equip_interface_messages.get("name_error"))
                return render_to_response(EQUIPMENT_INTERFACE_SEVERAL_FORM, lists, context_instance=RequestContext(request))
            
            cont = 0
            #Nao cadastrados
            evilCont = 0
            #Cadastrados com sucesso
            goodCont = 0
            erro = []
            
            #Separar o nome para mudar apenas o numero final, de acordo com campos e marca
            div_aux = False
            if int(campos) < 2:
                divisor_aux = combo
                div_aux = True
            else:
                divisor_aux = divisor
            
            for interface_number in range(last_piece_name,last_piece_name2+1):
                cont = cont + 1
                
                name_aux = name.split(divisor_aux)
                length = len(name_aux)
                name_aux[length - 1] = interface_number
                if div_aux:
                    name = divisor_aux
                else:
                    name = ""
                for x in range(0,length):
                    if (x == 0):
                        if (int(brand) == 2 or int(brand) == 4):
                            name = name +" "+str(name_aux[x])
                        else:
                            name = name+str(name_aux[x])
                    else:
                        if div_aux:
                            name = name +str(name_aux[x])
                        else:
                            name = name +divisor_aux+str(name_aux[x])
                
                msg_erro = ""
                erro_message = None
                contador = 0
                api_error = False
                
                try:
                    client.create_interface().inserir(name.strip(), protected, description, None, None, equip.get('id'))
                    goodCont = goodCont + 1
                except NomeInterfaceDuplicadoParaEquipamentoError, e:
                    logger.error(e)
                    erro.append(name)
                    evilCont = evilCont + 1
                          
                except NetworkAPIClientError, e:
                    logger.error(e)
                    erro_message = e
                    api_error = True
                    
            if not api_error:       
                for e in erro:
                        contador = contador + 1
                        if contador == len(erro):
                            msg_erro = msg_erro + e
                        else:
                            msg_erro = msg_erro + e + ', '  
            
                        
                if cont == goodCont:
                    messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("several_sucess"))
                    url_param = reverse("equip.interface.search.list")
                    if len(equip_name) > 2:
                        url_param = url_param + "?equip_name=" + equip_name
                    return HttpResponseRedirect(url_param)
                elif goodCont > 0 and evilCont > 0:
                    url_param = reverse("equip.interface.search.list")
                    messages.add_message(request, messages.WARNING, equip_interface_messages.get("several_warning") % (msg_erro))
                    if len(equip_name) > 2:
                        url_param = url_param + "?equip_name=" + equip_name
                    return HttpResponseRedirect(url_param)
                else:
                    
                    messages.add_message(request, messages.ERROR, equip_interface_messages.get("several_error") % (msg_erro))
            
            else:
                messages.add_message(request, messages.ERROR, e)    
            
        else:
            messages.add_message(request, messages.ERROR, equip_interface_messages.get("validation_error"))

    else:
        lists['form'] = AddSeveralInterfaceForm(brand, initial={'equip_name': equip['nome'], 'equip_id': equip['id']})
        
    lists['equip_type'] = equip['id_tipo_equipamento']
    lists['brand'] = brand
    lists['divisor'] = divisor
    
    return render_to_response(EQUIPMENT_INTERFACE_SEVERAL_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def edit_form(request, equip_name, id_interface):
    
    lists = dict()
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get equipment
        equip = client.create_equipamento().listar_por_nome(equip_name)
        equip = equip.get('equipamento')
        
        # Get interface
        interface = client.create_interface().get_by_id(id_interface)
        interface = interface.get('interface')
        if interface is None:
            raise InterfaceNaoExisteError("Interface não cadastrada")
        
        # Get related interfaces
        related_list = client.create_interface().list_connections(interface["interface"], equip["id"])
        
        # Join
        related_list = related_list['interfaces']
        related_list.append(interface)
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
        # Redirect to list_all action with the equipment selected
        url_param = reverse("equip.interface.search.list")
        if len(equip_name) > 2:
            url_param = url_param + "?equip_name=" + equip_name
        return HttpResponseRedirect(url_param)
    
    initials, params, equip_types, up, down, front_or_back = make_initials_and_params(related_list)
    
    AddInterfaceFormSet = formset_factory(AddInterfaceForm, params=params, equip_types=equip_types, up=up, down=down, front_or_back=front_or_back, extra=len(related_list), max_num=len(related_list))
    
    lists['equip_name'] = equip_name
    lists['id_interface'] = id_interface
    
    if request.method == "POST":
        
        form_set = AddInterfaceFormSet(request.POST)
        
        if form_set.is_valid():
            
            for form in form_set:
                
                idt = form.cleaned_data['inter_id']
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                protected = form.cleaned_data['protected']
                
                old_interf = client.create_interface().get_by_id(idt)['interface']
                
                try:
                    client.create_interface().alterar(idt, name, protected, description, old_interf['ligacao_front'], old_interf['ligacao_back'])
                    messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_edit"))
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    
            
            
            return redirect("equip.interface.edit.form", equip_name, id_interface)
        
        else:
            lists['formset'] = form_set
    else:
        lists['formset'] = AddInterfaceFormSet(initial=initials)
        
    return render_to_response(EQUIPMENT_INTERFACE_EDIT_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def connect(request, id_interface, front_or_back):
    
    lists = dict();
    
    if not (front_or_back == "0" or front_or_back == "1"):
        raise Http404
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        lists['id_interface'] = id_interface
        lists['front_or_back'] = front_or_back
        lists['search_form'] = SearchEquipForm()
        
        if request.method == "GET":
            
            if request.GET.__contains__('equip_name'):
                
                lists['search_form'] = search_form = SearchEquipForm(request.GET)
                
                if search_form.is_valid():
                    
                    # Get equip name in form
                    name_equip = search_form.cleaned_data['equip_name']
                    
                    # Get equipment by name from NetworkAPI
                    equipment = client.create_equipamento().listar_por_nome(name_equip)['equipamento']
                    # Get interfaces related to equipment selected
                    interf_list = client.create_interface().list_all_by_equip(equipment['id'])
                    
                    #Remove interface that is being added to the combobox
                    i = []
                    for inter in interf_list['interfaces']:
                        
                        if id_interface != inter['id']:
                            i.append(inter)

                    interf_list = {}
                    interf_list['interfaces'] = i

                    lists['connect_form'] = ConnectForm(equipment, interf_list['interfaces'], initial={'equip_name': equipment['nome'], 'equip_id': equipment['id']})
                    lists['equipment'] = equipment
                    
        elif request.method == "POST":
            
            equip_id = request.POST['equip_id']
            
            # Get equipment by name from NetworkAPI
            equipment = client.create_equipamento().listar_por_id(equip_id)['equipamento']
            # Get interfaces related to equipment selected
            interf_list = client.create_interface().list_all_by_equip(equipment['id'])
            
            form = ConnectForm(equipment, interf_list['interfaces'], request.POST)
            
            if form.is_valid():
                
                front = form.cleaned_data['front']
                back = form.cleaned_data['back']
                
                # Get interface to link
                interface_client = client.create_interface()
                interface = interface_client.get_by_id(id_interface)
                interface = interface.get("interface")
                if interface['protegida'] == "True":
                    interface['protegida'] = 1
                else:
                    interface['protegida'] = 0
                    
                if len(front) > 0:
                    # Get front interface selected
                    inter_front = interface_client.get_by_id(front)
                    inter_front = inter_front.get("interface")
                    if inter_front['protegida'] == "True":
                        inter_front['protegida'] = 1
                    else:
                        inter_front['protegida'] = 0
                        
                    related_list = client.create_interface().list_connections(inter_front["interface"], inter_front["equipamento"])
                    for i in related_list.get('interfaces'):
                        
                        if i['equipamento'] == interface['equipamento']:
                            lists['connect_form'] = form
                            lists['equipment'] = equipment
                            raise Exception('Configuração inválida. Loop detectado nas ligações entre patch-panels')                   
                    
                    # Business Rules
                    interface_client.alterar(inter_front['id'], inter_front['interface'], inter_front['protegida'], inter_front['descricao'], interface['id'], inter_front['ligacao_back'])
                    if front_or_back == "0":
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'], interface['descricao'], interface['ligacao_front'], inter_front['id'])
                        #interface_client.alterar(id_interface, nome, protegida, descricao, id_ligacao_front, id_ligacao_back)
                    else:
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'], interface['descricao'], inter_front['id'], interface['ligacao_back'])
                        
                else:
                    # Get back interface selected
                    inter_back = interface_client.get_by_id(back)
                    inter_back = inter_back.get("interface")
                    if inter_back['protegida'] == "True":
                        inter_back['protegida'] = 1
                    else:
                        inter_back['protegida'] = 0
                        
                    related_list = client.create_interface().list_connections(inter_back["interface"], inter_back["equipamento"])
                    for i in related_list.get('interfaces'):
                        
                        if i['equipamento'] == interface['equipamento']:
                            lists['connect_form'] = form
                            lists['equipment'] = equipment
                            raise Exception('Configuração inválida. Loop detectado nas ligações entre patch-panels')
                    
                    # Business Rules
                    interface_client.alterar(inter_back['id'], inter_back['interface'], inter_back['protegida'], inter_back['descricao'], inter_back['ligacao_front'], interface['id'])
                    if front_or_back == "0":
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'], interface['descricao'], interface['ligacao_front'], inter_back['id'])
                    else:
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'], interface['descricao'], inter_back['id'], interface['ligacao_back'])
                        
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_connect"))
                
                url_param = reverse("equip.interface.edit.form", args=[interface['equipamento_nome'], id_interface])
                response = HttpResponseRedirect(url_param)
                response.status_code = 278
                
                return response
            
            else:
                lists['connect_form'] = form
                lists['equipment'] = equipment
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(EQUIPMENT_INTERFACE_CONNECT_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def disconnect(request, id_interface, back_or_front, equip_name, id_interf_edit):
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Business
        client.create_interface().remove_connection(id_interface, back_or_front)
        messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_disconnect"))
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return redirect("equip.interface.edit.form", equip_name, id_interf_edit)