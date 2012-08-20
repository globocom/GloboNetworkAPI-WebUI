# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.utility import DataTablePaginator, validates_dict, clone
from CadVlan.VipRequest.forms import SearchVipRequestForm, RequestVipFormInputs, RequestVipFormEnvironment, RequestVipFormOptions, RequestVipFormHealthcheck, RequestVipFormReal, HealthcheckForm, RequestVipFormIP
from CadVlan.forms import DeleteForm, ValidateForm, CreateForm
from CadVlan.messages import error_messages, request_vip_messages, healthcheck_messages, equip_group_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import VIPREQUEST_SEARCH_LIST, SEARCH_FORM_ERRORS, AJAX_VIPREQUEST_LIST, VIPREQUEST_VIEW_AJAX, VIPREQUEST_FORM, AJAX_VIPREQUEST_CLIENT, AJAX_VIPREQUEST_ENVIRONMENT, AJAX_VIPREQUEST_OPTIONS, AJAX_VIPREQUEST_HEALTHCHECK, AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER, AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER_HTML, VIPREQUEST_EDIT
from django.contrib import messages
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response, redirect
from django.template import loader
from django.template.context import RequestContext
from networkapiclient.Pagination import Pagination
from networkapiclient.exception import NetworkAPIClientError, VipError, ScriptError, VipAllreadyCreateError, EquipamentoNaoExisteError, IpError, VipNaoExisteError, IpNaoExisteError
import logging

logger = logging.getLogger(__name__)


OPERATION = { 0 : 'DELETE' , 1: 'VALIDATE', 2: 'CREATE'}

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def search_list(request): 
    try:
        
        lists = dict()
        lists["delete_form"] = DeleteForm()
        lists["validate_form"] = ValidateForm()
        lists["create_form"] = CreateForm()
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        search_form = SearchVipRequestForm()
        
        lists["search_form"] = search_form
        lists['modal'] = 'false'
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(VIPREQUEST_SEARCH_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def ajax_list_equips(request):
    
    try:
        
        # If form was submited
        if request.method == "GET":
            
            # Get user auth
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            search_form = SearchVipRequestForm(request.GET)
            
            if search_form.is_valid():
                
                id_vip = search_form.cleaned_data['id_request']
                ipv4 = search_form.cleaned_data["ipv4"]
                ipv6 = search_form.cleaned_data["ipv6"]
                
                
                if len(ipv4) > 0:
                    ip = ipv4
                elif len(ipv6) > 0:
                    ip = ipv6
                else:
                    ip = None
                    
                # Pagination
                columnIndexNameMap = { 0: '', 1: 'id', 2 : 'ip', 3: 'descricao', 4: 'equipamento', 5: 'ambiente', 6: 'valido', 7: 'criado',8: '' }
                dtp = DataTablePaginator(request, columnIndexNameMap)
                
                # Make params
                dtp.build_server_side_list()
                
                # Set params in simple Pagination class
                pag = Pagination(dtp.start_record, dtp.end_record, dtp.asorting_cols, dtp.searchable_columns, dtp.custom_search)
                
                # Call API passing all params
                vips = client.create_vip().find_vip_requests(id_vip, ip, pag)
                
                if not vips.has_key("vips"):
                    vips["vips"] = []
                    
                    
                aux_vip = vips.get('vips') 
                
                if type(aux_vip) == dict:
                    vips['vips'] = [aux_vip]   
                          
                # Returns JSON
                return dtp.build_response(vips["vips"], vips["total"], AJAX_VIPREQUEST_LIST, request)
            
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
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def ajax_view_vip(request,id_vip):   
    
    lists= dict()
    lists['id_vip'] = id_vip
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        lists['vip'] = client.create_vip().get_by_id(id_vip).get('vip')
        
        
        if type(lists['vip']['reals']['real']) is not list:
            lists['vip']['reals']['real'] = [lists['vip']['reals']['real']]
            
        if type(lists['vip']['portas_servicos']['porta']) is not list:
            lists['vip']['portas_servicos']['porta'] = [lists['vip']['portas_servicos']['porta']]
        
        
        lists['len_porta'] =  int(len(lists['vip']['portas_servicos']['porta'])) 
        lists['len_equip'] = int (len(lists['vip']['equipamento']))
        
        # Returns HTML
        response = HttpResponse(loader.render_to_string(VIPREQUEST_VIEW_AJAX, lists, context_instance=RequestContext(request)))
        response.status_code = 200
        return response
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
         
    # Returns HTML
    response = HttpResponse(loader.render_to_string(VIPREQUEST_VIEW_AJAX, lists, context_instance=RequestContext(request)))
    # Send response status with error
    response.status_code = 412
    return response    
    
@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def delete_validate_create(request,operation):
    
    operation_text = OPERATION.get(int(operation))
    
    if request.method == 'POST':

        form = DeleteForm(request.POST) if operation_text == 'DELETE' else ValidateForm(request.POST) if operation_text == 'VALIDATE' else CreateForm(request.POST)
        id = 'ids' if operation_text == 'DELETE' else 'ids_val' if operation_text == 'VALIDATE' else 'ids_create'
        
        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_vip = auth.get_clientFactory().create_vip()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data[id])

            # All messages to display
            error_list = list()
            error_list_created = list()
            error_list_not_validate = list()

            # Control others exceptions
            have_errors = False
            
            #FLAG only for  ERROR  in create
            all_ready_msg_script_error = False

            # For each script selected to remove
            for id_vip in ids:
                try:
                    
                    if operation_text == 'DELETE':
                        # Execute in NetworkAPI
                        #criar remover
                        client_vip.remover(id_vip)
                    
                    elif operation_text == 'CREATE':
                        
                        vip = client_vip.get_by_id(id_vip).get('vip')
                        
                        if vip['is_ip4'] == 'True':
                        
                            client_vip.criar(id_vip)
                        else:
                            client_vip.create_ipv6(id_vip)
                        
                    elif operation_text == 'VALIDATE':
                        #criar validar
                        client_vip.validate(id_vip)
                
                except VipAllreadyCreateError, e:
                    logger.error(e)
                    error_list.append(id_vip)
                    error_list_created.append(id_vip) 
                except VipError, e:
                    logger.error(e)
                    error_list.append(id_vip)
                    error_list_not_validate.append(id_vip)
                except ScriptError, e:
                    logger.error(e)
                    if not all_ready_msg_script_error:
                        messages.add_message(request, messages.ERROR, e)
                    all_ready_msg_script_error = True
                    error_list.append(id_vip)
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    error_list.append(id_vip)
            
            msg_error_call,msg_sucess_call,msg_some_error_call = getErrorMesages(operation_text)
                
            if len(error_list_not_validate) > 0:
                
                msg = ""
                for id_error in error_list_not_validate:
                    msg = msg + id_error + ','
                
                msg = request_vip_messages.get('validate_before') % msg[:-1]
                messages.add_message(request, messages.WARNING, msg)
                    
            if len(error_list_created) > 0 :
                
                msg = ""
                for id_error in error_list_created:
                    msg = msg + id_error + ','
                
                msg = request_vip_messages.get('all_ready_create') % msg[:-1]
                messages.add_message(request, messages.WARNING, msg)
                
            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(request, messages.ERROR, request_vip_messages.get(msg_error_call))

            # If cant remove someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = request_vip_messages.get(msg_some_error_call) % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all has ben removed
            elif have_errors == False:
                messages.add_message(request, messages.SUCCESS, request_vip_messages.get(msg_sucess_call))

            else:
                messages.add_message(request, messages.ERROR, request_vip_messages.get(msg_error_call))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('vip-request.list')    


def getErrorMesages(operation_text):
    
    msg_erro = ""
    msg_sucesso = ""
    msg_erro_parcial = ""
    
    if operation_text == 'DELETE':
        
        msg_erro = 'can_not_remove_all'
        msg_sucesso = 'success_remove'
        msg_erro_parcial = 'can_not_remove'
    
    elif operation_text == 'VALIDATE':
        
        msg_erro = 'can_not_validate_all'
        msg_sucesso = 'success_validate'
        msg_erro_parcial = 'can_not_validate'
    
    elif operation_text == 'CREATE':
        
        msg_erro = 'can_not_create_all'
        msg_sucesso = 'success_create'
        msg_erro_parcial = 'can_not_create'
    
    else:
        return None,None,None
    
    return msg_erro,msg_sucesso,msg_erro_parcial
    
def valid_field_table_dynamic(field):
    field = clone(field)
    if field is not None:
        for i in range(0, len(field)):
            if "-" in field:
                field.remove("-")
    return field

def valid_ports(lists, ports_vip, ports_real):
    
    is_valid = True
    
    if ports_vip is not None and ports_real is not None:
    
        if ports_vip and ports_real:
            
            if len(ports_vip) != len(ports_real):
                lists['ports_error'] = request_vip_messages.get("error_ports")
                is_valid = False
                
        if ports_vip is None or ports_real is None or not ports_vip or not ports_real:
            lists['ports_error'] = request_vip_messages.get("error_ports")
            is_valid = False
    
    else:
        lists['ports_error'] = request_vip_messages.get("error_reals_required")
        is_valid = False
            
    return lists, is_valid


def valid_reals(lists, balancing, id_equip, id_ip, weight, priority):
    
    is_valid = True
    
    if id_equip is not None and id_ip is not None:
                    
        if str(balancing).upper() == "WEIGHTED":
        
            if weight and priority:
                
                if len(id_equip) != len(weight) or len(id_equip) != len(priority):
                    lists['reals_error'] = request_vip_messages.get("error_len_reals")
                    is_valid = False
                
        if not priority:
            lists['reals_error'] = request_vip_messages.get("error_reals")
            is_valid = False
        
        else:
            if len(id_equip) != len(priority):
                lists['reals_error'] = request_vip_messages.get("error_len_reals")
                is_valid = False
            
    return lists, is_valid


def ports_(ports_vip, ports_real):
    
    ports = []
    if ports_vip is not None and ports_real is not None:
        for i in range(0, len(ports_vip)):
            ports.append("%s:%s" % (ports_vip[i], ports_real[i]))  
    
    return ports

def mount_table_ports(lists, ports_vip, ports_real):

    if ports_vip is not None and ports_vip != '':
    
        ports = []
        for i in range(0, len(ports_vip)):
            
            if ports_real[i] != '' and ports_vip[i] != '':
                ports.append({'ports_real': ports_real[i] , 'ports_vip': ports_vip[i] })
        
        lists['ports'] = ports
    
    return lists


def mount_table_reals(lists, id_equip, id_ip, weight, priority, equip, ip):

    if id_equip is not None and id_equip != '':
    
        reals = []
        for i in range(0, len(id_equip)):
            
            if id_equip[i] != '' and id_ip[i] != '':
                
                if weight and priority:
                    reals.append({'priority': priority[i] , 'weight': weight[i], 'id_equip': id_equip[i] , 'equip': equip[i], 'id_ip': id_ip[i] , 'ip': ip[i] })
                
                else:
                
                    if not weight and not priority:
                        reals.append({'priority': '' , 'weight': '', 'id_equip': id_equip[i] , 'equip': equip[i], 'id_ip': id_ip[i] , 'ip': ip[i] })
                    
                    elif not weight:
                        reals.append({'priority': priority[i] , 'weight': '', 'id_equip': id_equip[i] , 'equip': equip[i], 'id_ip': id_ip[i] , 'ip': ip[i] })
                    else:
                        reals.append({'priority': '' , 'weight': weight[i], 'id_equip': id_equip[i] , 'equip': equip[i], 'id_ip': id_ip[i] , 'ip': ip[i] })
                    
        
        lists['reals'] = reals
        
    return lists


def reals_(id_equip, id_ip, equip, ip):

    reals = []
    
    if id_equip is not None and id_ip is not None:
        
        reals = []
        for i in range(0, len(id_equip)):
            reals.append({"real_name": equip[i] , "real_ip": ip[i] })
        
    return reals


def mount_ips(id_ipv4, id_ipv6, client_api):
    
    ipv4_check = False
    ipv4_type = None
    ipv4_specific = None
    if id_ipv4 is not None:
        ipv4 = client_api.create_ip().get_ipv4(id_ipv4).get("ipv4")
        ipv4_check = True
        ipv4_type = '1'
        ipv4_specific = "%s.%s.%s.%s" % (ipv4.get('oct1'), ipv4.get('oct2'), ipv4.get('oct3'), ipv4.get('oct4'))            
    
    ipv6_check = False
    ipv6_type = None
    ipv6_specific = None
    if id_ipv6 is not None and id_ipv6 != '0':
    
        ipv6 = client_api.create_ip().get_ipv6(id_ipv6).get("ipv6")
        ipv6_check = True
        ipv6_type = '1'
        ipv6_specific = "%s:%s:%s:%s:%s:%s:%s:%s" % (ipv6['block1'], ipv6['block2'], ipv6['block3'], ipv6['block4'], ipv6['block5'], ipv6['block6'], ipv6['block7'], ipv6['block8'])   
    
    form_ip = RequestVipFormIP(initial={"ipv4_check": ipv4_check, "ipv4_type": ipv4_type, "ipv4_specific": ipv4_specific, "ipv6_check": ipv6_check, "ipv6_type": ipv6_type, "ipv6_specific": ipv6_specific })
    
    return form_ip


def valid_form_and_submit(request,lists, finality_list, healthcheck_list, client_api, edit = False, idt = False):
    
    is_valid = True
    
    #Real - data
    ports_vip = valid_field_table_dynamic(request.POST.getlist('ports_vip')) if "ports_vip" in request.POST else None
    ports_real = valid_field_table_dynamic(request.POST.getlist('ports_real')) if "ports_real" in request.POST else None
    
    priority = valid_field_table_dynamic(request.POST.getlist('priority')) if "priority" in request.POST else None
    weight = valid_field_table_dynamic(request.POST.getlist('weight')) if "weight" in request.POST else None
    id_equip = valid_field_table_dynamic(request.POST.getlist('id_equip')) if "id_equip" in request.POST else None
    equip = valid_field_table_dynamic(request.POST.getlist('equip')) if "equip" in request.POST else None
    id_ip = valid_field_table_dynamic(request.POST.getlist('id_ip')) if "id_ip" in request.POST else None
    ip = valid_field_table_dynamic(request.POST.getlist('ip')) if "ip" in request.POST else None
    
    #Environment - data
    finality = request.POST["finality"] if "finality" in request.POST else None
    client = request.POST["client"] if "client" in request.POST else None
    environment = request.POST["environment"] if "environment" in request.POST else None
    
    #Options - data
    environment_vip = request.POST["environment_vip"] if "environment_vip" in request.POST else None
    
    form_inputs = RequestVipFormInputs(request.POST)
    form_environment = RequestVipFormEnvironment(finality_list, finality, client, environment, client_api, request.POST)
    form_real = RequestVipFormReal(request.POST)
    form_healthcheck = RequestVipFormHealthcheck(healthcheck_list, request.POST)
    form_options = RequestVipFormOptions(request, environment_vip, client_api, request.POST)
    form_ip = RequestVipFormIP(request.POST)
    
    if form_inputs.is_valid() & form_environment.is_valid() & form_real.is_valid() & form_healthcheck.is_valid() & form_options.is_valid() & form_ip.is_valid():
        
        #Inputs
        business =  form_inputs.cleaned_data["business"]
        service =  form_inputs.cleaned_data["service"]
        name =  form_inputs.cleaned_data["name"]
        filter_l7 =  form_inputs.cleaned_data["filter_l7"]
        validated =  form_inputs.cleaned_data["validated"]
        created =  form_inputs.cleaned_data["created"]
        
        
        #Environment
        finality =  form_environment.cleaned_data["finality"]
        client =  form_environment.cleaned_data["client"]
        environment =  form_environment.cleaned_data["environment"]
        environment_vip =  form_environment.cleaned_data["environment_vip"]
        
        #Healthcheck
        healthcheck_type =  form_healthcheck.cleaned_data["healthcheck_type"]
        healthcheck =  form_healthcheck.cleaned_data["healthcheck"]
        excpect =  form_healthcheck.cleaned_data["excpect"]
        
        #Options
        timeout =  form_options.cleaned_data["timeout"]
        caches =  form_options.cleaned_data["caches"]
        persistence =  form_options.cleaned_data["persistence"]
        balancing =  form_options.cleaned_data["balancing"]
        
        #Reals
        maxcom = form_real.cleaned_data["maxcom"]
        
        #IP
        ipv4_check = form_ip.cleaned_data["ipv4_check"]
        ipv6_check = form_ip.cleaned_data["ipv6_check"]
        
        lists, is_valid_ports = valid_ports(lists, ports_vip, ports_real)
        lists, is_valid_reals = valid_reals(lists, balancing, id_equip, id_ip, weight, priority)
        
        if is_valid_ports and is_valid_reals:
            
            ports = ports_(ports_vip, ports_real)
            
            reals = reals_(id_equip, id_ip, equip, ip)
            
            ipv4 = None
            ipv6 = None
            try:
            
                if ipv4_check:
                    
                    ipv4_type = form_ip.cleaned_data["ipv4_type"]
                    ipv4_specific = form_ip.cleaned_data["ipv4_specific"]
                    
                    if ipv4_type == '0': 
                        ipv4 = client_api.create_ip().get_available_ip4_for_vip(environment_vip).get("ip").get("id")
                        
                    else:
                        ipv4 = client_api.create_ip().check_vip_ip(ipv4_specific, environment_vip).get("ip").get("id")
                        
                if ipv6_check:
                    
                    ipv6_type = form_ip.cleaned_data["ipv6_type"]
                    ipv6_specific = form_ip.cleaned_data["ipv6_specific"]
                    
                    if ipv6_type == '0': 
                        ipv6 = client_api.create_ip().get_available_ip6_for_vip(environment_vip).get("ip").get("id")
                        
                    else:
                        ipv6 = client_api.create_ip().check_vip_ip(ipv6_specific, environment_vip).get("ip").get("id")
                
                if edit:
                    client_api.create_vip().alter(idt, ipv4, ipv6, excpect, '0', created, finality, client, environment, caches, balancing, persistence, healthcheck_type, healthcheck, timeout, name, maxcom, business, service, filter_l7, reals, priority, weight, ports)

                else:
                    client_api.create_vip().add(ipv4, ipv6, excpect, finality, client, environment, caches, balancing, persistence, healthcheck_type, healthcheck, timeout, name, maxcom, business, service, filter_l7, reals, priority, weight, ports)
                
            except NetworkAPIClientError, e:
                is_valid = False
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                
                form_ip = mount_ips(ipv4, ipv6, client_api)
        else:
            is_valid = False    
                
    else:
        is_valid = False
        
    #Real - data
    ports_vip = request.POST.getlist('ports_vip') if "ports_vip" in request.POST else None
    ports_real = request.POST.getlist('ports_real') if "ports_real" in request.POST else None
    
    lists = mount_table_ports(lists, ports_vip, ports_real)
    
    #Real - data
    priority = request.POST.getlist('priority') if "priority" in request.POST else None
    weight = request.POST.getlist('weight') if "weight" in request.POST else None
    id_equip = request.POST.getlist('id_equip') if "id_equip" in request.POST else None
    equip = request.POST.getlist('equip') if "equip" in request.POST else None
    id_ip = request.POST.getlist('id_ip') if "id_ip" in request.POST else None
    ip = request.POST.getlist('ip') if "ip" in request.POST else None
    
    lists = mount_table_reals(lists, id_equip, id_ip, weight, priority, equip, ip)
    
    lists['form_inputs'] = form_inputs
    lists['form_environment'] = form_environment
    lists['form_real'] = form_real
    lists['form_healthcheck'] = form_healthcheck
    lists['form_options'] = form_options
    lists['form_ip'] = form_ip
        
    return is_valid
    
@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def add_form(request):

    try:
        
        lists = dict()
        lists['ports'] = ''
        lists['ports_error'] = ''
        lists['reals_error'] = ''
        
        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()
        
        finality_list =  client_api.create_environment_vip().buscar_finalidade().get("finalidade")
        healthcheck_list =  client_api.create_ambiente().listar_healtchcheck_expect_distinct().get("healthcheck_expect")

        if request.method == "POST":
            
            is_valid = valid_form_and_submit(request, lists, finality_list, healthcheck_list, client_api)
            
            if is_valid:
                messages.add_message(request, messages.SUCCESS, request_vip_messages.get("success_insert"))
                return redirect('vip-request.list')
            
        else:

            lists['form_inputs'] = RequestVipFormInputs()
            lists['form_environment'] = RequestVipFormEnvironment(finality_list)
            lists['form_real'] = RequestVipFormReal()
            lists['form_healthcheck'] = RequestVipFormHealthcheck(healthcheck_list)
            lists['form_options'] = RequestVipFormOptions()
            lists['form_ip'] = RequestVipFormIP()
            
            

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VIPREQUEST_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def edit_form(request, id_vip):

    try:
        
        lists = dict()
        lists['ports'] = ''
        lists['ports_error'] = ''
        lists['idt'] = id_vip
        
        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()
        
        vip = client_api.create_vip().buscar(id_vip).get("vip")
        
        finality_list =  client_api.create_environment_vip().buscar_finalidade().get("finalidade")
        healthcheck_list =  client_api.create_ambiente().listar_healtchcheck_expect_distinct().get("healthcheck_expect")
        
        if request.method == "POST":
            
            is_valid = valid_form_and_submit(request, lists, finality_list, healthcheck_list, client_api, edit = True, idt = id_vip)
            
            if is_valid:
                messages.add_message(request, messages.SUCCESS, request_vip_messages.get("success_edit"))
                return redirect('vip-request.list')
        
        else:
            
            business = vip.get("areanegocio")
            service = vip.get("nome_servico")
            name = vip.get("host")
            filter_l7 = vip.get("l7_filter")
            created = vip.get("vip_criado")
            validated = vip.get("validado")
            
            if created == "1" :
                messages.add_message(request, messages.ERROR, request_vip_messages.get("can_not_edit"))
            
            form_inputs = RequestVipFormInputs(initial={"business": business, "service": service, "name": name, "filter_l7": filter_l7, "created": created, "validated": validated   })            
            
            finality = vip.get("finalidade")
            client = vip.get("cliente")
            environment = vip.get("ambiente")
            
            try:
            
                environment_vip = client_api.create_environment_vip().search(None, finality, client, environment).get("environmentvip").get("id")
                
            except Exception, e:
                environment_vip = None
                messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_environment_vip") %( finality, client, environment ))
            
            form_environment = RequestVipFormEnvironment(finality_list, finality, client, environment, client_api, initial={"finality": finality, "client": client, "environment": environment, "environment_vip": environment_vip })
            
            excpect = None
            healthcheck_type = vip.get("healthcheck_type")
            healthcheck = vip.get("healthcheck")
            
            id_healthcheck_expect = vip.get("id_healthcheck_expect")
            
            if id_healthcheck_expect is not None:
                excpect =  client_api.create_ambiente().buscar_healthcheck_por_id(id_healthcheck_expect).get("healthcheck_expect").get("id")    
            
            form_healthcheck = RequestVipFormHealthcheck(healthcheck_list, initial={"healthcheck_type": healthcheck_type, "healthcheck": healthcheck, "excpect": excpect})
            
            maxcon = vip.get("maxcon")            
            form_real = RequestVipFormReal(initial={"maxcom": maxcon})
            
            timeout = vip.get("timeout")
            caches = vip.get("cache")
            persistence = vip.get("persistencia")
            balancing = vip.get("metodo_bal")
            
            form_options = RequestVipFormOptions(request, environment_vip, client_api, initial={"timeout": timeout, "caches": caches, "persistence": persistence, "balancing": balancing})
            
            id_ipv4 = vip.get("id_ip")
            id_ipv6 = vip.get("id_ipv6")

            form_ip = mount_ips(id_ipv4, id_ipv6, client_api)
            
            ports = []
            if "portas_servicos" in vip:
                if type(vip['portas_servicos']['porta']) == unicode or  len(vip['portas_servicos']['porta']) == 1:
                    vip['portas_servicos']['porta'] = [vip['portas_servicos']['porta']]
                
                ports = vip.get("portas_servicos").get('porta')
            
            ports_vip = []
            ports_real = []
            for port in ports:
                p = str(port).split(":")
                ports_vip.append(p[0])
                
                if len(p) > 1:
                    ports_real.append(p[1])
                else:
                    ports_real.append('')

            lists = mount_table_ports(lists, ports_vip, ports_real)
            
            reals = []
            if "reals" in vip:
                if type(vip['reals']['real']) == dict or len(vip['reals']['real']) == 1:
                    vip['reals']['real'] = [vip['reals']['real']]
                    
                reals = vip.get("reals").get("real")
            
            prioritys = []
            if "reals_prioritys" in vip:
                if len(vip['reals_prioritys']['reals_priority']) == 1:
                    vip['reals_prioritys']['reals_priority'] = [vip['reals_prioritys']['reals_priority']]
                    
                prioritys = vip.get("reals_prioritys").get("reals_priority")

            
            weights = []
            if "reals_weights" in vip:
                if len(vip['reals_weights']['reals_weight']) == 1:
                    vip['reals_weights']['reals_weight'] = [vip['reals_weights']['reals_weight']]

                weights = vip.get("reals_weights").get("reals_weight")
            
            balancing = []
            id_equip = []
            id_ip = []
            weight = []
            priority = []
            equip = []
            ip = []
            for i in range(0, len(reals)):
                
                try:
                    
                    real_name = reals[i].get("real_name")
                    real_ip = reals[i].get("real_ip")
                
                    equip_aux = client_api.create_equipamento().listar_por_nome(real_name).get("equipamento")
                    
                    ip_aux = client_api.create_ip().get_ipv4_or_ipv6(real_ip).get("ip")
                    
                    equip.append(equip_aux.get("nome"))
                    id_equip.append(equip_aux.get("id"))
                    
                    id_ip.append(ip_aux.get("id"))
                    ip.append(real_ip)
                    
                    if prioritys:
                        priority.append(prioritys[i])

                    if weights:
                        weight.append(weights[i])
                        
                except (EquipamentoNaoExisteError, IpNaoExisteError), e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_reals") % (real_name, real_ip))
                
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
            
                
            lists = mount_table_reals(lists, id_equip, id_ip, weight, priority, equip, ip)
            
            lists['form_inputs'] = form_inputs
            lists['form_environment'] = form_environment
            lists['form_real'] = form_real
            lists['form_healthcheck'] = form_healthcheck
            lists['form_options'] = form_options
            lists['form_ip'] = form_ip



    except VipNaoExisteError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, request_vip_messages.get("invalid_vip"))
        return redirect('vip-request.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VIPREQUEST_EDIT, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def ajax_popular_client(request):

    lists = dict()
    status_code = None
    lists['clients'] = ''

    try:    
        finality = request.GET['finality']
        
        auth = AuthSession(request.session)
        client_evip = auth.get_clientFactory().create_environment_vip()
        
        lists['clients'] = validates_dict(client_evip.buscar_cliente_por_finalidade(finality), 'cliente_txt')
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500
        
    # Returns HTML
    return HttpResponse(loader.render_to_string(AJAX_VIPREQUEST_CLIENT, lists, context_instance=RequestContext(request)), status=status_code)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def ajax_popular_environment(request):

    lists = dict()
    status_code = None
    lists['environments'] = ''

    try:    
        finality = request.GET['finality']
        client = request.GET['client']
        
        auth = AuthSession(request.session)
        client_evip = auth.get_clientFactory().create_environment_vip()
        
        lists['environments'] = validates_dict(client_evip.buscar_ambientep44_por_finalidade_cliente(finality, client), 'ambiente_p44')
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500
        
    # Returns HTML
    return HttpResponse(loader.render_to_string(AJAX_VIPREQUEST_ENVIRONMENT, lists, context_instance=RequestContext(request)), status=status_code)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def ajax_popular_options(request):

    lists = dict()
    status_code = None

    try:    
        environment_vip = request.GET['environment_vip']
        
        auth = AuthSession(request.session)
        client_ovip = auth.get_clientFactory().create_option_vip()
        
        lists['timeout'] = validates_dict(client_ovip.buscar_timeout_opcvip(environment_vip), 'timeout_opt')
        lists['balancing'] = validates_dict(client_ovip.buscar_balanceamento_opcvip(environment_vip), 'balanceamento_opt')
        lists['caches'] = validates_dict(client_ovip.buscar_grupo_cache_opcvip(environment_vip), 'grupocache_opt')
        lists['persistence'] = validates_dict(client_ovip.buscar_persistencia_opcvip(environment_vip), 'persistencia_opt')
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500
        
    # Returns Json
    return HttpResponse(loader.render_to_string(AJAX_VIPREQUEST_OPTIONS, lists, context_instance=RequestContext(request)), status=status_code)


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def ajax_add_healthcheck(request):
    
    lists = dict()
    status_code = None
    form = HealthcheckForm()

    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory().create_ambiente()
        
        if request.method == "GET":

            form = HealthcheckForm(request.GET)

            if form.is_valid():
        
                excpect  = form.cleaned_data['excpect_new']
        
                client.add_expect_string_healthcheck(excpect)
                
                lists['success'] =  healthcheck_messages.get("success_create")
                
                
        lists['healthchecks'] =  client.listar_healtchcheck_expect_distinct().get("healthcheck_expect")
        lists['form'] = form
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500
    
    # Returns Json
    return HttpResponse(loader.render_to_string(AJAX_VIPREQUEST_HEALTHCHECK, lists, context_instance=RequestContext(request)), status=status_code)


@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def ajax_model_ip_real_server(request):
    
    lists = dict()
    lists['msg'] = ''
    lists['ips'] = ''
    ips = None
    equip = None
    balancing = None
    status_code = None

    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        if request.method == "GET":

            id_evip = request.GET['environment_vip']
            equip_name = request.GET['equip_name']
            balancing = request.GET['balancing']
            
            equip_real = split_to_array(request.GET['equip_real']) if "equip_real" in request.GET else None
            ips_real = split_to_array(request.GET['ips_real']) if "ips_real" in request.GET else None
            
            #Valid Equipament
            equip = client.create_equipamento().listar_por_nome(equip_name).get("equipamento")
            
            ips = client.create_ip().get_ip_by_equip_and_vip(equip_name, id_evip)
            
            ipv4 = validates_dict(ips, 'ipv4')
            ipv6 = validates_dict(ips, 'ipv6')
            
            #Valid is IP existing in table
            for equi in equip_real:
                
                if equip_name == equi:
                    
                    if ipv4 is not None:
            
                        for i in range(0, len(ipv4)):
                            
                            for ip_r in ips_real:
                                
                                if  ( i <= (len(ipv4)-1) )  :
                                
                                    if ipv4[i]['ip'] == str(ip_r).replace("%3A", ":"):
                                        del ipv4[i]
                                        
                    if ipv6 is not None:
                        
                        for i in range(0, len(ipv6)):
                            
                            for ip_r in ips_real:
                                
                                if  ( i <= (len(ipv6)-1) )  :
                                
                                    if ipv6[i]['ip'] == str(ip_r).replace("%3A", ":"):
                                        del ipv6[i]
            
            
            ips['ipv4'] = ipv4
            ips['ipv6'] = ipv6
            

    except IpError, e:
        pass

    except EquipamentoNaoExisteError, e:        
        logger.error(e)
        lists['msg'] = equip_group_messages.get("invalid_equipament_group")

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500
        
    lists['ips'] = loader.render_to_string(AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER_HTML, { 'ips': ips , 'equip': equip, 'balancing': balancing}, context_instance=RequestContext(request))
    
    # Returns Json
    return HttpResponse(loader.render_to_string(AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER, lists, context_instance=RequestContext(request)), status=status_code)