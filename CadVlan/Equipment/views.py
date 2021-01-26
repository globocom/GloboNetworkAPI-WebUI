# -*- coding: utf-8 -*-
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
import json
import logging

from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from networkapiclient.exception import EquipamentoError
from networkapiclient.exception import NetworkAPIClientError
from networkapiclient.Pagination import Pagination

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Equipment.business import cache_list_equipment
from CadVlan.Equipment.forms import EquipForm
from CadVlan.Equipment.forms import MarcaForm
from CadVlan.Equipment.forms import ModeloForm
from CadVlan.Equipment.forms import SearchEquipmentForm
from CadVlan.forms import DeleteForm
from CadVlan.messages import equip_messages
from CadVlan.messages import error_messages
from CadVlan.messages import request_vip_messages
from CadVlan.permissions import BRAND_MANAGEMENT
from CadVlan.permissions import ENVIRONMENT_MANAGEMENT
from CadVlan.permissions import EQUIPMENT_GROUP_MANAGEMENT
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.permissions import VIP_ALTER_SCRIPT
from CadVlan.templates import AJAX_AUTOCOMPLETE_LIST
from CadVlan.templates import AJAX_EQUIP_LIST
from CadVlan.templates import EQUIPMENT_EDIT
from CadVlan.templates import EQUIPMENT_FORM
from CadVlan.templates import EQUIPMENT_MARCA
from CadVlan.templates import EQUIPMENT_MARCAMODELO_FORM
from CadVlan.templates import EQUIPMENT_MODELO
from CadVlan.templates import EQUIPMENT_SEARCH_LIST
from CadVlan.templates import EQUIPMENT_VIEW_AJAX
from CadVlan.templates import SEARCH_FORM_ERRORS
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.Decorators import has_perm
from CadVlan.Util.Decorators import has_perm_external
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.Util.utility import DataTablePaginator
from CadVlan.Util.utility import validates_dict

logger = logging.getLogger(__name__)


@log
@login_required
def ajax_check_real(request, id_vip):

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get reals related
        vip = client.create_vip().get_by_id(id_vip).get('vip')
        reals = [vip.get('reals')['real'], ] if type(
            vip.get('reals')['real']) is dict else vip.get('reals')['real']

        response_data = {}
        response_data['count'] = len(reals)

        return HttpResponse(json.dumps(response_data), content_type='application/json')

    except NetworkAPIClientError as e:
        logger.error(e)
        return HttpResponse(json.dumps(e), content_type='application/json')


@log
@login_required
@has_perm([{'permission': VIP_ALTER_SCRIPT, 'write': True}, ])
def ajax_view_real(request, id_equip):

    lists = dict()
    return ajax_view_real_shared(request, id_equip, lists)


def ajax_view_real_shared(request, id_equip, lists):

    try:

        lists['equip_id'] = id_equip

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get reals related
        vips_reals = client.create_equipamento().get_real_related(id_equip)
        lists['vips'] = [vips_reals.get('vips'), ] if type(
            vips_reals.get('vips')) is dict else vips_reals.get('vips')
        lists['equip_name'] = vips_reals.get('equip_name')

        # Returns HTML
        response = HttpResponse(loader.render_to_string(
            EQUIPMENT_VIEW_AJAX, lists, context_instance=RequestContext(request)))
        response.status_code = 200
        return response

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    # Returns HTML
    response = HttpResponse(loader.render_to_string(
        EQUIPMENT_VIEW_AJAX, lists, context_instance=RequestContext(request)))
    # Send response status with error
    response.status_code = 412
    return response


@log
@login_required
@has_perm([{'permission': VIP_ALTER_SCRIPT, 'write': True}, ])
def ajax_remove_real(request, id_vip):

    try:
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()

        ip = request.GET['ip']
        port_vip = request.GET['port_vip']
        port_real = request.GET['port_real']
        equip_id = request.GET['equip_id']
        real_name = request.GET['real_name']

        # Remove all reals related
        if id_vip == '0':
            vips_reals = client.create_equipamento().get_real_related(
                equip_id).get('vips')
            vips_reals = [vips_reals, ] if type(
                vips_reals) is dict else vips_reals
            vip_ids = list()
            for vip in vips_reals:
                vip_ids.append(vip['id_vip'])

            vip_ids = set(vip_ids)

            for id in vip_ids:
                lists = remove_reals_from_equip(
                    client, id, lists, ip, port_vip, port_real, real_name, True)

        else:
            lists = remove_reals_from_equip(
                client, id_vip, lists, ip, port_vip, port_real, real_name)

        return ajax_view_real_shared(request, equip_id, lists)

    except Exception as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)


def remove_reals_from_equip(client, id_vip, lists, ip='', port_vip='', port_real='', real_name='', remove_all=False):
    try:
        vip = client.create_vip().get_by_id(id_vip).get('vip')

        reals = [vip.get('reals')['real'], ] if type(
            vip.get('reals')['real']) is dict else vip.get('reals')['real']
        priority = [vip.get('reals_prioritys')['reals_priority'], ] if type(vip.get('reals_prioritys')[
            'reals_priority']) is unicode else vip.get('reals_prioritys')['reals_priority']
        weight = [vip.get('reals_weights')['reals_weight'], ] if type(vip.get('reals_weights')[
            'reals_weight']) is unicode else vip.get('reals_weights')['reals_weight']

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

        client.create_vip().edit_reals(
            id_vip, 'method_bal', reals, priority, weight, 0)

        lists['message'] = request_vip_messages.get('real_remove')
        lists['msg_type'] = 'success'

    except Exception as e:
        lists['msg_type'] = 'error'
        lists['message'] = e

    return lists


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, 'read': True}])
def ajax_autocomplete_equips(request):
    try:

        equip_list = dict()

        # Get user auth
        auth = AuthSession(request.session)
        equipment = auth.get_clientFactory().create_equipamento()

        # Get list of equipments from cache
        equip_list = cache_list_equipment(equipment)

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(AJAX_AUTOCOMPLETE_LIST, equip_list, context_instance=RequestContext(request))


@log
@csrf_exempt
@has_perm_external([{'permission': EQUIPMENT_MANAGEMENT, 'read': True}])
def ajax_autocomplete_equips_external(request, form_acess, client):
    try:

        equip_list = dict()
        equipment = client.create_equipamento()

        # Get list of equipments from cache
        equip_list = cache_list_equipment(equipment)

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response_ajax(AJAX_AUTOCOMPLETE_LIST, equip_list, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, 'read': True}, {'permission': ENVIRONMENT_MANAGEMENT, 'read': True}, {'permission': EQUIPMENT_GROUP_MANAGEMENT, 'read': True}])
def ajax_list_equips(request):

    try:

        # If form was submited
        if request.method == 'GET':
            # Get user auth
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            # Get all environments from NetworkAPI
            env_list = get_environments(client)
            # Get all equipment types from NetworkAPI
            type_equip_list = client.create_tipo_equipamento().listar()
            # Get all groups from NetworkAPI
            group_list = client.create_grupo_equipamento().listar()

            search_form = SearchEquipmentForm(
                env_list, type_equip_list, group_list, request.GET)

            if search_form.is_valid():

                name = search_form.cleaned_data['name']
                iexact = search_form.cleaned_data['iexact']
                environment = search_form.cleaned_data['environment']
                equip_type = search_form.cleaned_data['type_equip']
                group = search_form.cleaned_data['group']
                ipv4 = search_form.cleaned_data['ipv4']
                ipv6 = search_form.cleaned_data['ipv6']

                if environment == '0':
                    environment = None
                if equip_type == '0':
                    equip_type = None
                if group == '0':
                    group = None

                if len(ipv4) > 0:
                    ip = ipv4
                elif len(ipv6) > 0:
                    ip = ipv6
                else:
                    ip = None

                # Pagination
                columnIndexNameMap = {
                    0: '', 1: 'nome', 2: 'tipo_equipamento', 3: 'grupos', 4: 'ip', 5: 'vlan', 6: 'ambiente', 7: ''}
                dtp = DataTablePaginator(request, columnIndexNameMap)

                # Make params
                dtp.build_server_side_list()

                # Set params in simple Pagination class
                pag = Pagination(dtp.start_record, dtp.end_record,
                                 dtp.asorting_cols, dtp.searchable_columns, dtp.custom_search)

                # Call API passing all params
                equips = client.create_equipamento().find_equips(
                    name, iexact, environment, equip_type, group, ip, pag)

                if 'equipamento' not in equips:
                    equips['equipamento'] = []

                # Returns JSON
                return dtp.build_response(equips['equipamento'], equips['total'], AJAX_EQUIP_LIST, request)

            else:
                # Remake search form
                lists = dict()
                lists['search_form'] = search_form

                # Returns HTML
                response = HttpResponse(loader.render_to_string(
                    SEARCH_FORM_ERRORS, lists, context_instance=RequestContext(request)))
                # Send response status with error
                response.status_code = 412
                return response

    except NetworkAPIClientError as e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')
    except BaseException as e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, 'read': True}, {'permission': ENVIRONMENT_MANAGEMENT, 'read': True}, {'permission': EQUIPMENT_GROUP_MANAGEMENT, 'read': True}])
def search_list(request):

    try:

        lists = dict()
        lists['delete_form'] = DeleteForm()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all environments from NetworkAPI
        env_list = get_environments(client)

        # Get all equipment types from NetworkAPI
        type_equip_list = client.create_tipo_equipamento().listar()
        # Get all groups from NetworkAPI
        group_list = client.create_grupo_equipamento().listar()

        search_form = SearchEquipmentForm(
            env_list, type_equip_list, group_list)

        lists['search_form'] = search_form

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(EQUIPMENT_SEARCH_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, 'write': True}, {'permission': ENVIRONMENT_MANAGEMENT, 'read': True}, {'permission': EQUIPMENT_GROUP_MANAGEMENT, 'read': True}])
def equip_form(request):
    try:
        equip = None
        roteadores = []
        lists = dict()
        forms_aux = dict()

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        forms_aux['tipo_equipamento'] = client.create_tipo_equipamento().listar().get(
            'equipment_type')
        forms_aux['marcas'] = client.create_marca().listar().get('brand')
        forms_aux['grupos'] = client.create_grupo_equipamento().listar().get(
            'grupo')

        data_env = {
            "start_record": 0,
            "end_record": 5000,
            "asorting_cols": [],
            "searchable_columns": [],
            "custom_search": "",
            "extends_search": []
        }
        environments = client.create_api_environment().search(search=data_env)
        forms_aux['ambientes'] = environments.get('environments')
        forms_aux['sdn_controlled_environment'] = environments.get('environments')

        if request.method == 'POST':
            roteadores = request.POST.getlist('roteadores')

            try:
                marca = int(request.POST['marca'])
            except:
                marca = 0

            if marca > 0:
                forms_aux['modelos'] = client.create_modelo().listar_por_marca(
                    marca).get('model')
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
                maintenance = form.cleaned_data['maintenance']
                sdn_controlled_environment = form.cleaned_data[
                    'sdn_controlled_environment']

                environments = [{
                    'is_router': True if amb in roteadores else False,
                    'environment': int(amb)
                } for amb in ambientes]

                groups = [{'id': int(g)} for g in grupos]
                sdn_envs = [{'environment': int(env)}
                            for env in sdn_controlled_environment]

                eqpt = {
                    'name': nome,
                    'maintenance': bool(maintenance),
                    'equipment_type': int(tipo_equipamento),
                    'model': int(modelo),
                    'environments': environments,
                    'groups': groups,
                    'sdn_controlled_environment': sdn_envs
                }
                client.create_api_v4_equipment().create([eqpt])

                messages.add_message(
                    request, messages.SUCCESS, equip_messages.get('equip_sucess'))

                # redirecionar
                return redirect('equipment.search.list')

            else:
                lists['form'] = form
                lists['roteadores'] = roteadores
        # get
        else:
            # Set Form
            forms_aux['modelos'] = None
            lists['roteadores'] = roteadores

            lists['form'] = EquipForm(forms_aux)

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        if equip is not None:
            client.create_equipamento().remover(equip)

    return render_to_response(EQUIPMENT_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, 'read': True}, {'permission': ENVIRONMENT_MANAGEMENT, 'read': True}, {'permission': EQUIPMENT_GROUP_MANAGEMENT, 'read': True}])
def ajax_modelo_equip(request, id_marca):
    try:

        lists = dict()
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        marca = int(id_marca)

        if marca > 0:
            modelos = client.create_modelo().listar_por_marca(marca)
            lists['modelos'] = modelos.get('model')

            # Returns HTML
            response = HttpResponse(loader.render_to_string(
                EQUIPMENT_MODELO, lists, context_instance=RequestContext(request)))
            # Send response status with error
            response.status_code = 200
            return response

        else:

            # Returns HTML
            response = HttpResponse(loader.render_to_string(
                EQUIPMENT_MODELO, lists, context_instance=RequestContext(request)))
            # Send response status with error
            response.status_code = 200
            return response

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    except:
        logger.error(
            'Erro na requição Ajax de Busca de Modelo do Equipamento por Marca')
    # Returns HTML
    response = HttpResponse(loader.render_to_string(
        EQUIPMENT_MODELO, lists, context_instance=RequestContext(request)))
    # Send response status with error
    response.status_code = 200
    return response


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, 'read': True}, {'permission': ENVIRONMENT_MANAGEMENT, 'read': True}, {'permission': EQUIPMENT_GROUP_MANAGEMENT, 'read': True}])
def ajax_marca_equip(request):
    try:

        lists = dict()
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        marcas = client.create_marca().listar()
        lists['marcas'] = marcas.get('brand')

        # Returns HTML
        response = HttpResponse(loader.render_to_string(
            EQUIPMENT_MARCA, lists, context_instance=RequestContext(request)))
        # Send response status with error
        response.status_code = 200
        return response

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    except:
        logger.error('Erro na requição Ajax de Atualização de Marcas')
    # Returns HTML
    response = HttpResponse(loader.render_to_string(
        EQUIPMENT_MARCA, lists, context_instance=RequestContext(request)))
    # Send response status with error
    response.status_code = 200
    return response


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, 'write': True}, {'permission': ENVIRONMENT_MANAGEMENT, 'read': True}, {'permission': EQUIPMENT_GROUP_MANAGEMENT, 'read': True}])
def equip_edit(request, id_equip):

    lists = dict()
    lists['equip_id'] = id_equip

    roteadores = []

    # Get user
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    is_error = False

    forms_aux = dict()
    forms_aux['tipo_equipamento'] = client.create_tipo_equipamento().listar().get(
        'equipment_type')
    forms_aux['marcas'] = client.create_marca().listar().get('brand')
    forms_aux['grupos'] = client.create_grupo_equipamento(
    ).listar().get('grupo')
    # List All - Ambientes
    environments = client.create_ambiente().listar().get('ambiente')
    forms_aux['ambientes'] = environments
    # List All - Sdn Controller Environments
    forms_aux['sdn_controlled_environment'] = environments

    try:
        equip = client.create_api_v4_equipment().get(
            [id_equip],
            include=[
                'environments', 'sdn_controlled_environment',
                'groups', 'model__details__brand']
        ).get('equipments')[0]

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('equipment.search.list')

    list_groups = []
    list_environments = []
    list_sdn_controlled_environments = []
    try:

        if request.method == 'POST':

            roteadores_chosen = request.POST.getlist('roteadores')

            try:
                marca = int(request.POST['marca'])
            except:
                marca = 0

            if marca > 0:
                forms_aux['modelos'] = client.create_modelo().listar_por_marca(
                    marca).get('model')
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
                maintenance = form.cleaned_data['maintenance']
                sdn_controlled_environment = form.cleaned_data[
                    'sdn_controlled_environment']

                environments = [{
                    'is_router': True if amb in roteadores_chosen else False,
                    'environment': int(amb)
                } for amb in environments_chosen]

                groups = [{'id': int(g)} for g in groups_chosen]
                sdn_envs = [{'environment': int(env)}
                            for env in sdn_controlled_environment]

                eqpt = {
                    'id': int(id_equip),
                    'name': name,
                    'maintenance': bool(maintenance),
                    'equipment_type': int(type_equipment),
                    'model': int(model),
                    'environments': environments,
                    'groups': groups,
                    'sdn_controlled_environment': sdn_envs
                }
                client.create_api_v4_equipment().update([eqpt])

                messages.add_message(
                    request, messages.SUCCESS, equip_messages.get('equip_edit_sucess'))

                return redirect('equipment.search.list')

            # form invalid
            else:

                lists = list_ips_edit_equip(lists, id_equip, client)
                lists['roteadores'] = roteadores_chosen

        # GET REQUEST
        else:
            try:

                lists = list_ips_edit_equip(lists, id_equip, client)

                for group in equip.get('groups'):
                    list_groups.append(group['id'])

                for environment in equip.get('environments'):
                    list_environments.append(environment['environment'])

                    if environment['is_router'] is True:
                        roteadores.append(str(environment['environment']))

                for sdn_env in equip.get('sdn_controlled_environment'):
                    list_sdn_controlled_environments.append(
                        sdn_env['environment'])

                # Set Form
                modelos = client.create_modelo().listar_por_marca(
                    equip.get('model').get('brand').get('id'))
                forms_aux['modelos'] = modelos.get('model')

                lists['form'] = EquipForm(
                    forms_aux,
                    initial={
                        'nome': equip.get('name'),
                        'maintenance': equip.get('maintenance'),
                        'tipo_equipamento': equip.get('equipment_type'),
                        'marca': equip.get('model').get('brand').get('id'),
                        'modelo': equip.get('model').get('id'),
                        'grupo': list_groups,
                        'ambiente': list_environments,
                        'sdn_controlled_environment': list_sdn_controlled_environments
                    })
                lists['roteadores'] = roteadores

            except NetworkAPIClientError as e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists = list_ips_edit_equip(lists, id_equip, client)

    except Exception as e:
        logger.error(e)
        lists = list_ips_edit_equip(lists, id_equip, client)

    return render_to_response(EQUIPMENT_EDIT, lists, context_instance=RequestContext(request))


def list_ips_edit_equip(lists, id_equip, client):
    try:

        ips = client.create_ip().find_ips_by_equip(id_equip)
        if ips.get('ips') is not None:

            ips4 = validates_dict(ips.get('ips'), 'ipv4')
            ips6 = validates_dict(ips.get('ips'), 'ipv6')

            if ips4 is not None:
                lists['ips4'] = ips4
            if ips6 is not None:
                lists['ips6'] = ips6

    except Exception as e:
        logger.error(e)

    return lists


@log
@login_required
@has_perm([{'permission': BRAND_MANAGEMENT, 'write': True}])
def marca_form(request):

    lists = dict()

    # Primeira aba de cadastro de marcas
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

                messages.add_message(
                    request, messages.SUCCESS, equip_messages.get('marca_sucess'))

                return render_to_response(EQUIPMENT_MARCAMODELO_FORM, lists, context_instance=RequestContext(request))

            # Form Invalid
            else:
                lists['form_marca'] = form

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(EQUIPMENT_MARCAMODELO_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{'permission': BRAND_MANAGEMENT, 'write': True}])
def modelo_form(request):

    lists = dict()
    # Segunda aba de cadastro de modelos
    lists['aba'] = 1

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        marcas = client.create_marca().listar()

        lists['form_modelo'] = ModeloForm(marcas)
        lists['form_marca'] = MarcaForm()

        if request.method == 'POST':

            form = ModeloForm(marcas, request.POST)

            if form.is_valid():

                marca = form.cleaned_data['marca']
                nome = form.cleaned_data['nome']

                client.create_modelo().inserir(marca, nome)

                messages.add_message(
                    request, messages.SUCCESS, equip_messages.get('modelo_sucess'))

                return render_to_response(EQUIPMENT_MARCAMODELO_FORM, lists, context_instance=RequestContext(request))

            # Form Invalid
            else:
                lists['form_modelo'] = form

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(EQUIPMENT_MARCAMODELO_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, 'write': True}, {'permission': ENVIRONMENT_MANAGEMENT, 'read': True}, {'permission': EQUIPMENT_GROUP_MANAGEMENT, 'read': True}])
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
            messages.add_message(
                request, messages.ERROR, error_messages.get('select_one'))

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
            client_equip.remover(id_equip)

        except EquipamentoError as e:
            error_list.append(id_equip)

        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            have_errors = True
            break

    # If cant remove nothing
    if len(error_list) == len(ids):
        messages.add_message(
            request, messages.ERROR, error_messages.get('can_not_remove_all'))

    # If cant remove someones
    elif len(error_list) > 0:
        msg = ''
        for id_error in error_list:
            msg = msg + id_error + ', '

        msg = error_messages.get('can_not_remove') % msg[:-2]

        messages.add_message(request, messages.WARNING, msg)

    # If all has ben removed
    elif have_errors is False:
        messages.add_message(
            request, messages.SUCCESS, equip_messages.get('success_remove'))

    else:
        messages.add_message(
            request, messages.SUCCESS, error_messages.get('can_not_remove_error'))


@log
@login_required
@has_perm([{'permission': EQUIPMENT_MANAGEMENT, 'write': True}, {'permission': ENVIRONMENT_MANAGEMENT, 'read': True}, {'permission': EQUIPMENT_GROUP_MANAGEMENT, 'read': True}])
def delete_equipment(request, id_equip):
    """
    Method called from modal of equipment's reals
    """

    # Get user
    auth = AuthSession(request.session)
    client_equip = auth.get_clientFactory().create_equipamento()

    delete_equipments_shared(request, client_equip, [id_equip, ])

    # Redirect to list_all action
    return redirect('equipment.search.list')


def get_environments(client):
    try:
        # Get all environments from NetworkAPI
        search_env = {
            'extends_search': [],
            'start_record': 0,
            'custom_search': '',
            'end_record': 99999999,
            'asorting_cols': [],
            'searchable_columns': []}
        env_cli = client.create_api_environment()
        # env_list = env_cli.search()
        return client.create_api_environment().search(search=search_env, kind='basic')

    except Exception as e:
        raise e