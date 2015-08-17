# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import EQUIPMENT_INTERFACE_SEARCH_LIST, EQUIPMENT_INTERFACE_FORM, \
                              EQUIPMENT_INTERFACE_SEVERAL_FORM, EQUIPMENT_INTERFACE_EDIT_FORM, EQUIPMENT_INTERFACE_CONNECT_FORM
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
from CadVlan.EquipInterface.forms import AddInterfaceForm, AddEnvInterfaceForm, AddSeveralInterfaceForm, ConnectForm, EditForm
from CadVlan.EquipInterface.business import make_initials_and_params
from CadVlan.Util.extends.formsets import formset_factory


logger = logging.getLogger(__name__)

def get_environment_list(client, equip_id):

    environment_list = None
    try:
        rack = client.create_rack().get_rack_by_equip_id(equip_id)
        rack = rack.get('rack')
        environment_list = client.create_rack().list_all_rack_environments(rack[0].get('id'))
    except:
        pass

    if environment_list is None:
        environment_list = client.create_ambiente().list_all()

    return environment_list

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def search_list(request):

    try:

        lists = dict()
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
                messages.add_message(
                    request, messages.SUCCESS, equip_interface_messages.get("success_remove"))

            else:
                messages.add_message(
                    request, messages.WARNING, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    url_param = reverse("equip.interface.search.list")
    if len(equip_nam) > 2:
        url_param = url_param + "?equip_name=" + equip_nam
    return HttpResponseRedirect(url_param)


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def add_form(request, equip_name=None):

    lists = dict()

    # Get user
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        equip = client.create_equipamento().listar_por_nome(str(equip_name))
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('equip.interface.search.list')

    equip = equip.get('equipamento')
    brand = equip['id_marca'] if equip['id_tipo_equipamento'] != "2" else "0"
    int_type_list = client.create_interface().list_all_interface_types()

    environment_list = get_environment_list(client, equip['id'])

    lists['equip_type'] = equip['id_tipo_equipamento']
    lists['equip_name'] = equip['nome']
    lists['brand'] = brand
    lists['int_type'] = int_type_list
    lists['id'] = None

    if request.method == "GET":
        lists['form'] = AddInterfaceForm(int_type_list, brand, 0, initial={'equip_name': equip['nome'],'equip_id': equip['id']})
        lists['envform'] = AddEnvInterfaceForm(environment_list)


    if request.method == "POST":

        form = AddInterfaceForm(int_type_list, brand, 0, request.POST)
        envform = AddEnvInterfaceForm(environment_list, request.POST)

        try:

            if form.is_valid() and envform.is_valid():

                name = form.cleaned_data['name']
                protected = form.cleaned_data['protected']
                int_type = form.cleaned_data['int_type']
                vlan = form.cleaned_data['vlan']
                envs = envform.cleaned_data['environment']

                trunk = 0
                if int_type=="0":
                    int_type = "access"
                else:
                    int_type = "trunk"
                    trunk = 1

                id_int = client.create_interface().inserir(name, protected, None, None, None, equip['id'], int_type, vlan)
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_insert"))

                id_int = id_int.get("interface")

                if trunk:
                    for env in envs:
                        client.create_interface().associar_ambiente(env, id_int['id'])

                #success_insert: env, interface

                url_param = reverse("equip.interface.search.list")
                if len(equip_name) > 2:
                    url_param = url_param + "?equip_name=" + equip_name

                return HttpResponseRedirect(url_param)
            else:
                lists['form'] = form
                lists['envform'] = envform

        except NetworkAPIClientError, e:
            logger.error(e)
            lists['form'] = form
            lists['envform'] = envform
            messages.add_message(request, messages.ERROR, e)

    return render_to_response(EQUIPMENT_INTERFACE_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def add_several_forms(request, equip_name):

    lists = dict()

    # Get User
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
    divisor = "/" if (brand == '3' or brand ==
                      '5' or brand == '21') else ":" if brand == "0" else "." if brand == '4' else ""

    list_brands = [2, 3, 4, 5, 21, 25]

    if int(brand) not in list_brands:
        # Redirect to list_all action
        messages.add_message(
            request, messages.ERROR, equip_interface_messages.get("brand_error"))
        url_param = reverse("equip.interface.search.list")
        if len(equip_name) > 2:
            url_param = url_param + "?equip_name=" + equip_name
        return HttpResponseRedirect(url_param)

    if request.method == 'POST':

        form = AddSeveralInterfaceForm(brand, request.POST)
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
                messages.add_message(
                    request, messages.ERROR, equip_interface_messages.get("name_error"))
                return render_to_response(EQUIPMENT_INTERFACE_SEVERAL_FORM, lists, context_instance=RequestContext(request))

            cont = 0
            # Nao cadastrados
            evilCont = 0
            # Cadastrados com sucesso
            goodCont = 0
            erro = []

            # Separar o nome para mudar apenas o numero final, de acordo com
            # campos e marca
            div_aux = False
            if int(campos) < 2:
                divisor_aux = combo
                div_aux = True
            else:
                divisor_aux = divisor

            for interface_number in range(last_piece_name, last_piece_name2 + 1):
                cont = cont + 1

                name_aux = name.split(divisor_aux)
                length = len(name_aux)
                name_aux[length - 1] = interface_number
                if div_aux:
                    name = divisor_aux
                else:
                    name = ""
                for x in range(0, length):
                    if (x == 0):
                        if (int(brand) == 2 or int(brand) == 4) or int(brand) == 21:
                            name = name + " " + str(name_aux[x])
                        else:
                            name = name + str(name_aux[x])
                    else:
                        if div_aux:
                            name = name + str(name_aux[x])
                        else:
                            name = name + divisor_aux + str(name_aux[x])

                msg_erro = ""
                erro_message = None
                contador = 0
                api_error = False

                try:
                    client.create_interface().inserir(
                        name.strip(), protected, description, None, None, equip.get('id'), None)
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
                    messages.add_message(
                        request, messages.SUCCESS, equip_interface_messages.get("several_sucess"))
                    url_param = reverse("equip.interface.search.list")
                    if len(equip_name) > 2:
                        url_param = url_param + "?equip_name=" + equip_name
                    return HttpResponseRedirect(url_param)
                elif goodCont > 0 and evilCont > 0:
                    url_param = reverse("equip.interface.search.list")
                    messages.add_message(request, messages.WARNING, equip_interface_messages.get(
                        "several_warning") % (msg_erro))
                    if len(equip_name) > 2:
                        url_param = url_param + "?equip_name=" + equip_name
                    return HttpResponseRedirect(url_param)
                else:

                    messages.add_message(request, messages.ERROR, equip_interface_messages.get(
                        "several_error") % (msg_erro))

            else:
                messages.add_message(request, messages.ERROR, e)

        else:
            messages.add_message(
                request, messages.ERROR, equip_interface_messages.get("validation_error"))

    else:
        lists['form'] = AddSeveralInterfaceForm(
            brand, initial={'equip_name': equip['nome'], 'equip_id': equip['id']})

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

        # Get interface types
        int_type_list = client.create_interface().list_all_interface_types()

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

    initials, params, equip_types, up, down, front_or_back = make_initials_and_params(related_list, int_type_list)

    EditFormSet = formset_factory(EditForm, params=params, equip_types=equip_types, up=up, down=down,
                                     front_or_back=front_or_back, extra=len(related_list), max_num=len(related_list))

    lists['equip_name'] = equip_name
    lists['id_interface'] = id_interface
    lists['formset'] = EditFormSet(initial=initials)

    return render_to_response(EQUIPMENT_INTERFACE_EDIT_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def edit(request, id_interface):

    lists = dict()

    # Get user
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        interface = client.create_interface().get_by_id(id_interface)
        interface = interface.get('interface')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('equip.interface.search.list')

    lig_front = interface.get('ligacao_front')
    lig_back = interface.get('ligacao_back')
    equip_name = interface.get('equipamento_nome')
    lists['equip_name'] = equip_name
    lists['id'] = id_interface

    try:
        equip = client.create_equipamento().listar_por_nome(equip_name)
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('equip.interface.search.list')

    equip = equip.get('equipamento')
    brand = equip['id_marca'] if equip['id_tipo_equipamento'] != "2" else "0"
    int_type_list = client.create_interface().list_all_interface_types()

    environment_list = get_environment_list(client, equip['id'])

    lists['equip_type'] = equip['id_tipo_equipamento']
    lists['brand'] = brand
    lists['int_type'] = int_type_list

    if request.method == "GET":

        tipo = 0
        if "trunk" in interface.get('tipo'):
            tipo = 1

        protegida = 1
        if  interface.get('protegida')=="False":
            protegida = 0

        lists['form'] = AddInterfaceForm(int_type_list, brand, 0, initial={'equip_name': equip['nome'], 'equip_id': equip['id'],
                                         'name': interface.get('interface'), 'protected': protegida, 'int_type': tipo,
                                         'vlan': interface.get('vlan') })
        lists['envform'] = AddEnvInterfaceForm(environment_list)


    if request.method == "POST":

        form = AddInterfaceForm(int_type_list, brand, 0, request.POST)
        envform = AddEnvInterfaceForm(environment_list, request.POST)

        try:

            if form.is_valid() and envform.is_valid():
                name = form.cleaned_data['name']
                protected = form.cleaned_data['protected']
                int_type = form.cleaned_data['int_type']
                vlan = form.cleaned_data['vlan']
                envs = envform.cleaned_data['environment']

                trunk = 0
                if int_type=="0":
                    int_type = "access"
                else:
                    int_type = "trunk"
                    trunk = 1

                id_int = client.create_interface().alterar(id_interface, name, protected, None, lig_front, lig_back,
                                                           int_type, vlan)
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_edit"))

                if trunk:
                    client.create_interface().dissociar(id_interface)
                    for env in envs:
                        client.create_interface().associar_ambiente(env, id_interface)

                #success_insert: env, interface

                return HttpResponseRedirect(reverse('equip.interface.edit.form', args=[equip_name, id_interface]))
            else:
                lists['form'] = form
                lists['envform'] = envform

        except NetworkAPIClientError, e:
            logger.error(e)
            lists['form'] = form
            messages.add_message(request, messages.ERROR, e)

    return render_to_response(EQUIPMENT_INTERFACE_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def connect(request, id_interface, front_or_back):

    lists = dict()

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

                lists['search_form'] = search_form = SearchEquipForm(
                    request.GET)

                if search_form.is_valid():

                    # Get equip name in form
                    name_equip = search_form.cleaned_data['equip_name']

                    # Get equipment by name from NetworkAPI
                    equipment = client.create_equipamento().listar_por_nome(
                        name_equip)['equipamento']
                    # Get interfaces related to equipment selected
                    interf_list = client.create_interface().list_all_by_equip(
                        equipment['id'])

                    # Remove interface that is being added to the combobox
                    i = []
                    for inter in interf_list['interfaces']:

                        if id_interface != inter['id']:
                            i.append(inter)

                    interf_list = {}
                    interf_list['interfaces'] = i

                    lists['connect_form'] = ConnectForm(equipment, interf_list['interfaces'], initial={
                                                        'equip_name': equipment['nome'], 'equip_id': equipment['id']})
                    lists['equipment'] = equipment

        elif request.method == "POST":

            equip_id = request.POST['equip_id']

            # Get equipment by name from NetworkAPI
            equipment = client.create_equipamento().listar_por_id(
                equip_id)['equipamento']
            # Get interfaces related to equipment selected
            interf_list = client.create_interface().list_all_by_equip(
                equipment['id'])

            form = ConnectForm(
                equipment, interf_list['interfaces'], request.POST)

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

                    related_list = client.create_interface().list_connections(
                        inter_front["interface"], inter_front["equipamento"])
                    for i in related_list.get('interfaces'):

                        if i['equipamento'] == interface['equipamento']:
                            lists['connect_form'] = form
                            lists['equipment'] = equipment
                            raise Exception(
                                'Configuração inválida. Loop detectado nas ligações entre patch-panels')

                    # Business Rules
                    interface_client.alterar(inter_front['id'], inter_front['interface'], inter_front['protegida'],
                                             inter_front['descricao'], interface['id'], inter_front['ligacao_back'],
                                             inter_front['tipo'], inter_front['vlan'])
                    if front_or_back == "0":
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'],
                                                 interface['descricao'], interface['ligacao_front'], inter_front['id'],
                                                 interface['tipo'], interface['vlan'])
                    else:
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'],
                                                 interface['descricao'], inter_front['id'], interface['ligacao_back'],
                                                 interface['tipo'], interface['vlan'])

                else:
                    # Get back interface selected
                    inter_back = interface_client.get_by_id(back)
                    inter_back = inter_back.get("interface")
                    if inter_back['protegida'] == "True":
                        inter_back['protegida'] = 1
                    else:
                        inter_back['protegida'] = 0

                    related_list = client.create_interface().list_connections( inter_back["interface"], inter_back["equipamento"])

                    for i in related_list.get('interfaces'):
                        if i['equipamento'] == interface['equipamento']:
                            lists['connect_form'] = form
                            lists['equipment'] = equipment
                            raise Exception('Configuração inválida. Loop detectado nas ligações entre patch-panels')

                    # Business Rules
                    interface_client.alterar(inter_back['id'], inter_back['interface'], inter_back['protegida'],
                                             inter_back['descricao'], inter_back['ligacao_front'], interface['id'],
                                             inter_back['tipo'], inter_back['vlan'])
                    if front_or_back == "0":
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'],
                                                 interface['descricao'], interface['ligacao_front'], inter_back['id'],
                                                 interface['tipo'], interface['vlan'])
                    else:
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'],
                                                 interface['descricao'], inter_back['id'], interface['ligacao_back'],
                                                 interface['tipo'], interface['vlan'])

                messages.add_message(
                    request, messages.SUCCESS, equip_interface_messages.get("success_connect"))

                url_param = reverse(
                    "equip.interface.edit.form", args=[interface['equipamento_nome'], id_interface])
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
        client.create_interface().remove_connection(
            id_interface, back_or_front)
        messages.add_message(
            request, messages.SUCCESS, equip_interface_messages.get("success_disconnect"))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect("equip.interface.edit.form", equip_name, id_interf_edit)
