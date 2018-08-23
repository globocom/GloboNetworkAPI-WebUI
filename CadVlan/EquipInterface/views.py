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

from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http import Http404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext

from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Util.Decorators import has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.extends.formsets import formset_factory

from CadVlan.templates import EQUIPMENT_INTERFACE_SEARCH_LIST
from CadVlan.templates import EQUIPMENT_INTERFACE_FORM
from CadVlan.templates import EQUIPMENT_INTERFACE_CONNECT_FORM
from CadVlan.templates import EQUIPMENT_INTERFACE_EDIT_FORM
from CadVlan.templates import EQUIPMENT_INTERFACE_SEVERAL_FORM
from CadVlan.templates import EQUIPMENT_INTERFACE_ADD_CHANNEL
from CadVlan.templates import EQUIPMENT_INTERFACES
from CadVlan.templates import EQUIPMENT_INTERFACE_EDIT_CHANNEL

from CadVlan.forms import DeleteForm
from CadVlan.forms import SearchEquipForm
from CadVlan.forms import ChannelForm
from CadVlan.forms import DeleteChannelForm

from CadVlan.EquipInterface.forms import EnvInterfaceForm
from CadVlan.EquipInterface.forms import ChannelAddForm
from CadVlan.EquipInterface.forms import EditForm
from CadVlan.EquipInterface.forms import ConnectForm
from CadVlan.EquipInterface.forms import AddSeveralInterfaceForm
from CadVlan.EquipInterface.forms import AddEnvInterfaceForm
from CadVlan.EquipInterface.forms import AddInterfaceForm

from CadVlan.EquipInterface.business import make_initials_and_params

from CadVlan.settings import PATCH_PANEL_ID
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.messages import equip_interface_messages
from CadVlan.messages import error_messages

from networkapiclient.exception import NetworkAPIClientError
from networkapiclient.exception import InterfaceNaoExisteError
from networkapiclient.exception import InvalidParameterError
from networkapiclient.exception import NomeInterfaceDuplicadoParaEquipamentoError



logger = logging.getLogger(__name__)

def env_vlans(env_list, env_id, range):

    env_vlans_list = []

    for i, env in enumerate(env_id):
        #verifica se o numero das vlans está dentro do intervalo do ambiente
        for e in env_list:
            if e.get('id') == env:
                if not "None" in e.get('range') :
                    for intervalo in range[i].split(';'):
                        for a in intervalo.split('-'):
                            if a is u'':
                                range[i] = e.get('range')
                            else:
                                if not (int(a) >= int(e.get('min_num_vlan_1')) and int(a) <= int(e.get('max_num_vlan_1'))):
                                    if not (int(a) >= int(e.get('min_num_vlan_2')) and int(a) <= int(e.get('max_num_vlan_2'))):
                                        raise InvalidParameterError(u'Numero de vlan fora do range definido para o '
                                                                    u'ambiente: %s'%(e.get('range')))
                elif not range[i]:
                    raise InvalidParameterError(u'Ambiente sem Vlan cadastrada. Especifique o numero da Vlan.')

        env_vlans_dict = dict()
        env_vlans_dict["vlans"] = range[i]
        env_vlans_dict["env"] = env
        env_vlans_list.append(env_vlans_dict)
    return env_vlans_list

def get_equip_environment(client, equip_id):


    environment_list = client.create_ambiente().listar_por_equip(equip_id)

    if environment_list is not None:
        if environment_list.get('ambiente') is None:
            environment_list = None
    try:
        environment = environment_list.get('ambiente')
        environment.get('id')
        ambiente = []
        ambiente.append(environment)
        environment_list = dict()
        environment_list['ambiente'] = ambiente
    except:
        pass
    return environment_list

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def search_list(request):

    try:

        lists = dict()
        lists['search_form'] = SearchEquipForm()
        lists['del_form'] = DeleteForm()
        lists['del_chan_form'] = DeleteChannelForm()
        lists['channel_form'] = ChannelForm()

        if request.method == "GET":

            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            if request.GET.__contains__('equip_name'):
                lists['search_form'] = search_form = SearchEquipForm(request.GET)

                if search_form.is_valid():

                    # Get equip name in form
                    name_equip = search_form.cleaned_data['equip_name']

                    lists['equip_name'] = name_equip
                    # Get equipment by name from NetworkAPI
                    equipment = client.create_equipamento().listar_por_nome(name_equip)['equipamento']

                    # Get all interfaces by equipment id
                    equip_interface_list = client.create_interface().list_all_by_equip(equipment['id'])

                    init_map = {'equip_name': equipment['nome'], 'equip_id': equipment['id']}

                    # New form
                    del_form = DeleteForm(initial=init_map)
                    del_chan_form = DeleteChannelForm(initial=init_map)
                    lists['channel_form'] = ChannelForm(initial=init_map)

                    # Send to template
                    lists['del_form'] = del_form
                    lists['del_chan_form'] = del_chan_form
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
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    url_param = reverse("interface.list")
    if len(equip_nam) > 2:
        url_param = url_param + "?search_equipment=" + equip_nam
    return HttpResponseRedirect(url_param)

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def channel_delete(request):

    equip_nam = request.POST['equip_name']

    if request.method == 'POST':

        form = DeleteChannelForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids_chan'])
            equip_nam = form.cleaned_data['equip_name']

            # Control others exceptions
            have_errors = False

            for idt in ids:
                try:
                    client.create_interface().delete_channel(idt)
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True

            if have_errors == False:
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_remove_channel"))

            else:
                messages.add_message(request, messages.WARNING, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    url_param = reverse("interface.list")
    if len(equip_nam) > 2:
        url_param = url_param + "?search_equipment=" + equip_nam
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
        return redirect('interface.list')

    equip = equip.get('equipamento')
    brand = equip['id_marca'] if equip['id_tipo_equipamento'] != "2" else "0"
    int_type_list = client.create_interface().list_all_interface_types()

    environment_list = get_equip_environment(client, equip['id'])

    lists['equip_type'] = equip['id_tipo_equipamento']
    lists['equip_name'] = equip['nome']
    lists['brand'] = brand
    lists['int_type'] = int_type_list
    lists['id'] = None

    if request.method == "GET":
        lists['form'] = AddInterfaceForm(int_type_list, brand, 0, initial={'equip_name': equip['nome'],'equip_id': equip['id']})
        if environment_list is not None:
            lists['envform'] = AddEnvInterfaceForm(environment_list)


    if request.method == "POST":

        form = AddInterfaceForm(int_type_list, brand, 0, request.POST)
        if environment_list is not None:
            envform = AddEnvInterfaceForm(environment_list, request.POST)

        try:

            if form.is_valid():

                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                protected = form.cleaned_data['protected']
                int_type = form.cleaned_data['int_type']
                vlan = form.cleaned_data['vlan']

                envs = None
                if environment_list is not None and envform.is_valid():
                    envs = envform.cleaned_data['environment']

                trunk = 0
                if int_type=="0":
                    int_type = "access"
                else:
                    int_type = "trunk"
                    trunk = 1

                id_int = client.create_interface().inserir(name, protected, description, None, None, equip['id'], int_type, vlan)
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_insert"))

                id_int = id_int.get("interface")

                if trunk and envs is not None:
                    for env in envs:
                        client.create_interface().associar_ambiente(env, id_int['id'])
                    messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_associando_amb"))

                url_param = reverse("interface.list")
                if len(equip_name) > 2:
                    url_param = url_param + "?search_equipment=" + equip_name

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
        return redirect('interface.list')

    equip = equip.get('equipamento')

    brand = equip['id_marca'] if equip['id_tipo_equipamento'] != "2" else "0"
    divisor = "/" if (brand == '3' or brand ==
                      '5' or brand == '6' or brand == '21') else ":" if brand == "0" else "." if brand == '4' else ""

    list_brands = [2, 3, 4, 5, 6, 21, 25]
    # 2 Patch-Panel-Generico
    # 3 Cisco
    # 4 F5
    # 5 Foundry
    # 6 Dell
    # 21 HUAWEI
    # 25 Sistmax

    if int(brand) not in list_brands:
        # Redirect to list_all action
        messages.add_message(
            request, messages.ERROR, equip_interface_messages.get("brand_error"))
        url_param = reverse("interface.list")
        if len(equip_name) > 2:
            url_param = url_param + "?search_equipment=" + equip_name
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
                    url_param = reverse("interface.list")
                    if len(equip_name) > 2:
                        url_param = url_param + "?search_equipment=" + equip_name
                    return HttpResponseRedirect(url_param)
                elif goodCont > 0 and evilCont > 0:
                    url_param = reverse("interface.list")
                    messages.add_message(request, messages.WARNING, equip_interface_messages.get(
                        "several_warning") % (msg_erro))
                    if len(equip_name) > 2:
                        url_param = url_param + "?search_equipment=" + equip_name
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

        lists['channel'] = interface.get('channel')
        lists['sw_router'] = interface.get('sw_router')
        lists['equip_name'] = equip_name
        lists['channel_id'] = interface.get('id_channel')

        # Get interface types
        int_type_list = client.create_interface().list_all_interface_types()

        # Get related interfaces
        related_list = client.create_interface().list_connections(interface.get("interface"), equip.get("id"))

        # Join
        related_list = related_list['interfaces']
        related_list.append(interface)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        # Redirect to list_all action with the equipment selected
        url_param = reverse("interface.list")
        if len(equip_name) > 2:
            url_param = url_param + "?search_equipment=" + equip_name
        return HttpResponseRedirect(url_param)

    initials, params, equip_types, up, down, front_or_back = make_initials_and_params(related_list, int_type_list)

    EditFormSet = formset_factory(EditForm, params=params, equip_types=equip_types, up=up, down=down,
                                     front_or_back=front_or_back, extra=len(related_list), max_num=len(related_list))

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
        return redirect('interface.list')

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
        return redirect('interface.list')

    equip = equip.get('equipamento')
    brand = equip['id_marca'] if equip['id_tipo_equipamento'] != "2" else "0"
    int_type_list = client.create_interface().list_all_interface_types()

    environment_list = get_equip_environment(client, equip['id'])

    lists['equip_type'] = equip['id_tipo_equipamento']
    lists['brand'] = brand
    lists['int_type'] = int_type_list
    lists['id_interface'] = interface.get('id')


    if request.method == "GET":

        tipo = 0
        if "trunk" in interface.get('tipo'):
            tipo = 1

        protegida = 1
        if  interface.get('protegida')=="False":
            protegida = 0

        lists['form'] = AddInterfaceForm(int_type_list, brand, 0, initial={'equip_name': equip['nome'], 'equip_id': equip['id'],
                                         'name': interface.get('interface'), 'description': interface.get('descricao'),
                                         'protected': protegida, 'int_type': tipo, 'vlan': interface.get('vlan'), 'type': tipo})
        if environment_list is not None:
            if tipo:
                try:
                    int_envs = client.create_interface().get_env_by_id(id_interface)
                    int_envs = int_envs.get('ambiente')
                    envs_list = []
                    if type(int_envs) is not list:
                        i = int_envs
                        int_envs = []
                        int_envs.append(i)
                    envform_list = []
                    for i in int_envs:
                        envs_list.append(int(i.get('id')))
                    envform = EnvInterfaceForm(environment_list, initial={'environment': envs_list})
                except:
                    envform = EnvInterfaceForm(environment_list)
                    pass
                lists['envform'] = envform
            else:
                envform = EnvInterfaceForm(environment_list)
                lists['envform'] = envform

    if request.method == "POST":

        form = AddInterfaceForm(int_type_list, brand, 0, request.POST)
        lists['form'] = form

        if environment_list is not None:
            envform = AddEnvInterfaceForm(environment_list, request.POST)
            lists['envform'] = envform

        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            protected = form.cleaned_data['protected']
            int_type = form.cleaned_data['int_type']
            vlan = form.cleaned_data['vlan']

            envs = None
            if environment_list is not None and envform.is_valid():
                envs = request.POST.getlist('environment')

            trunk = 0
            if int_type=="0":
                int_type = "access"
            else:
                int_type = "trunk"
                trunk = 1

            try:
                client.create_interface().alterar(id_interface, name, protected, description, lig_front, lig_back,
                                                       int_type, vlan)
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_edit"))
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)

            if trunk and envs is not None:
                client.create_interface().dissociar(id_interface)
                for env in envs:
                    client.create_interface().associar_ambiente(env, id_interface)

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
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        client.create_api_interface_request().remove_connection(id_interface, back_or_front)
        messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_disconnect"))
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return redirect("equip.interface.edit.form", equip_name, id_interf_edit)

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def channel(request):

    if request.method == 'POST':

        form = ChannelForm(request.POST)
        equip_nam = request.POST['equip_name']

        if form.is_valid():
            ids = split_to_array(form.cleaned_data['ids_channel'])

            interfaces_ids = ""
            for id_interface in ids:
                interfaces_ids = interfaces_ids + "-" + str(id_interface)

            url_param = reverse("equip.interface.add.channel", args=[equip_nam])
            url_param = url_param + "/?ids=" + interfaces_ids + "?" + equip_nam
            return HttpResponseRedirect(url_param)
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
            url_param = reverse("interface.list")
            if len(equip_nam) > 2:
                url_param = url_param + "?search_equipment=" + equip_nam
            return HttpResponseRedirect(url_param)

    return redirect("home")

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def add_channel(request, equip_name=None):

    lists = dict()
    lists['equip_name'] = equip_name

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        equip = client.create_equipamento().listar_por_nome(str(equip_name))
        equip = equip.get('equipamento')

        equip_interface_list = client.create_interface().list_all_by_equip(equip['id'])

        environment_list = get_equip_environment(client, equip['id'])

        if request.method == "GET":

            requestGet = request.GET['ids']
            requestGet = requestGet.split("?")
            ids = requestGet[0]

            for var in ids.split('-'):
                if len(var) > 1:
                    interface = var
                    try:
                        interface = client.create_interface().get_by_id(int(interface))
                        interface = interface.get('interface')
                    except:
                        messages.add_message(request, messages.ERROR, u'Interface %s não encontrada.' % var)
                        return redirect('interface.list')

                    if interface['channel'] is not None:
                        messages.add_message(request, messages.ERROR, u'Interface %s já está associada ao channel %s.' % (interface['interface'],interface['channel']))
                        return redirect('interface.list')

            try:
                interface = interface['id_ligacao_front']
                interface = client.create_interface().get_by_id(int(interface))
                interface = interface.get('interface')
            except:
                messages.add_message(request, messages.ERROR, u'Interface não conectada')
                return redirect('interface.list')

            tipo = interface['tipo']
            if "access" in tipo:
                tipo = 0
            else:
                tipo = 1

            form = ChannelAddForm(equip_interface_list, initial={'ids': ids, 'equip_name': equip_name, 'int_type': tipo,
                                                                 'vlan': interface['vlan']})
            lists['form'] = form

            if environment_list is not None:
                if tipo:
                    envform = AddEnvInterfaceForm(environment_list)
                else:
                    envform = AddEnvInterfaceForm(environment_list)
                lists['envform'] = envform
            else:
                messages.add_message(request, messages.WARNING, "O equipamento não possui ambientes cadastrados.")


        if request.method == "POST":

            form = ChannelAddForm(equip_interface_list, request.POST)
            lists['form'] = form

            if environment_list is not None:
                envform = AddEnvInterfaceForm(environment_list, request.POST)

            if form.is_valid():

                name = form.cleaned_data['name']
                lacp = form.cleaned_data['lacp']
                int_type = form.cleaned_data['int_type']
                vlan_nativa = form.cleaned_data['vlan']
                interfaces_ids = form.cleaned_data['ids']
                equip_nam = form.cleaned_data['equip_name']

                if int_type == "0":
                    int_type = "access"
                    env_vlans_list = []
                else:
                    int_type = "trunk"
                    if environment_list is None:
                        messages.add_message(request, messages.ERROR, "O equipamento não possui ambientes cadastrados.")
                        return render_to_response(EQUIPMENT_INTERFACE_ADD_CHANNEL, lists, context_instance=RequestContext(request))
                    if envform.is_valid():
                        environment = request.POST.getlist('environment')
                        vlan_range = request.POST.getlist('vlans')
                        env_vlans_list = env_vlans(environment_list.get("ambiente"), environment, vlan_range)

                try:
                    client.create_interface().inserir_channel(interfaces_ids, name, lacp, int_type, vlan_nativa, env_vlans_list)
                    messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_insert_channel"))
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    return render_to_response(EQUIPMENT_INTERFACE_ADD_CHANNEL, lists, context_instance=RequestContext(request))
                except Exception, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    return render_to_response(EQUIPMENT_INTERFACE_ADD_CHANNEL, lists, context_instance=RequestContext(request))

                url_param = reverse("interface.list")
                if len(equip_nam) > 2:
                    url_param = url_param + "?search_equipment=" + equip_nam
                return HttpResponseRedirect(url_param)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        url_param = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url_param)

    return render_to_response(EQUIPMENT_INTERFACE_ADD_CHANNEL, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def edit_channel(request, channel_name, equip_name, channel=None):

    lists = dict()

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    lists['channel_name'] = channel_name
    lists['channel'] = channel

    try:

        equip = client.create_equipamento().listar_por_nome(str(equip_name))
        equip = equip.get('equipamento')

        equip_interface_list = client.create_interface().list_available_interfaces(channel, equip['id'])

        try:
            equip_interface_list.get('interface')['id']
            equip_interface_list = equip_interface_list.get('interface')
            interface = list()
            interface.append(equip_interface_list)
            equip_interface_list = dict()
            equip_interface_list['interfaces'] = interface
        except:
            pass

        environment_list = get_equip_environment(client, equip['id'])

        channel = client.create_interface().get_interface_by_channel(channel_name, equip_name)
        channel = channel.get('interfaces')

        if type(channel) is list:
            lists['equip_interface'] = channel
            channel = channel[0]
        else:
            equip_int = []
            equip_int.append(channel)
            lists['equip_interface'] = equip_int

        if request.method == "GET":

            tipo = channel['tipo']
            if "access" in tipo:
                tipo = 0
            else:
                tipo = 1

            if channel['lacp']=="True":
                lacp = 1
            else:
                lacp = 0

            form = ChannelAddForm(equip_interface_list, initial={'id': channel['id_channel'], 'name': channel['channel'],
                                                                 'lacp': lacp, 'equip_name': equip_name, 'type':tipo,
                                                                 'int_type': tipo, 'vlan': channel['vlan_nativa']})
            lists['form'] = form

            if environment_list is not None:
                envs = environment_list.get('ambiente')
                lists['environment_list'] = envs
                if tipo:
                    try:
                        int_envs = client.create_interface().get_env_by_id(channel['id'])
                        int_envs = int_envs.get('ambiente')
                        if type(int_envs) is not list:
                            i = int_envs
                            int_envs = []
                            int_envs.append(i)
                        envform_list = []
                        for i in int_envs:
                            envform = AddEnvInterfaceForm(environment_list, initial={'environment': int(i.get('id')), 'vlans': i.get('vlans')})
                            envform_list.append(envform)
                    except:
                        envform = AddEnvInterfaceForm(environment_list)
                        envform_list.append(envform)
                        pass
                    lists['envform'] = envform_list
                else:
                    envform = AddEnvInterfaceForm(environment_list)
                    lists['envform'] = envform
                lists['envsform'] = AddEnvInterfaceForm(environment_list)
            else:
                messages.add_message(request, messages.WARNING, "O equipamento não possui ambientes cadastrados.")

        if request.method == "POST":

            form = ChannelAddForm(equip_interface_list, request.POST)
            lists['form'] = form

            if environment_list is not None:
                envform = AddEnvInterfaceForm(environment_list, request.POST)

            if form.is_valid():

                id_channel = form.cleaned_data['id']
                name = form.cleaned_data['name']
                lacp = form.cleaned_data['lacp']
                int_type = form.cleaned_data['int_type']
                vlan_nativa = form.cleaned_data['vlan']
                interfaces_ids = request.POST.getlist('idsInterface')

                if int_type=="0":
                    int_type = "access"
                    env_vlans_list = []
                else:
                    int_type = "trunk"
                    if environment_list is None:
                        messages.add_message(request, messages.ERROR, "O equipamento não possui ambientes cadastrados.")
                        return render_to_response(EQUIPMENT_INTERFACE_EDIT_CHANNEL, lists, context_instance=RequestContext(request))
                    if envform.is_valid():
                        environment = request.POST.getlist('environment')
                        vlan_range = request.POST.getlist('vlans')
                        env_vlans_list = env_vlans(environment_list.get("ambiente"), environment, vlan_range)
                try:
                    client.create_interface().editar_channel(id_channel, name, lacp, int_type, vlan_nativa, env_vlans_list,
                                                             interfaces_ids)
                    messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_edit_channel"))
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    return render_to_response(EQUIPMENT_INTERFACE_EDIT_CHANNEL, lists, context_instance=RequestContext(request))
                except Exception, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    return render_to_response(EQUIPMENT_INTERFACE_EDIT_CHANNEL, lists, context_instance=RequestContext(request))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(EQUIPMENT_INTERFACE_EDIT_CHANNEL, lists, context_instance=RequestContext(request))


def channel_insert_interface(request):

    try:

        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()

        interface_Id = request.GET.get('interface_Id')
        equip_interface = client_api.create_interface().get_by_id(interface_Id)
        equip_interface = equip_interface.get('interface')
        equip_interface_list = []
        equip_interface_list.append(equip_interface)
        lists = dict()
        lists['equip_interface'] = equip_interface_list
        lists['qtd'] = 0

        return render( request, EQUIPMENT_INTERFACES, lists)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


def config_sync_all(request, equip_name, is_channel, ids):

    equip_nam = equip_name

    # Get user
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    # Control others exceptions
    have_errors = False

    try:
        if int(is_channel):
            client.create_api_interface_request().deploy_channel_config_sync(ids)
        else:
            client.create_api_interface_request().deploy_interface_config_sync(ids)
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        have_errors = True

    # If all has ben removed
    if have_errors == False:
        messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_sync"))
    else:
        messages.add_message(request, messages.WARNING, error_messages.get("can_not_sync_error"))

    url_list = '/interface/?search_equipment=%s' % equip_name
    url_edit = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse(url_list)

    return HttpResponseRedirect(url_edit)
