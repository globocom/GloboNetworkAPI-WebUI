# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.Decorators import log, login_required, has_perm, \
    access_external
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.utility import DataTablePaginator, validates_dict, clone, \
    get_param_in_request, IP_VERSION, is_valid_int_param
from CadVlan.VipRequest.encryption import Encryption
from CadVlan.VipRequest.forms import SearchVipRequestForm, RequestVipFormInputs, \
    RequestVipFormEnvironment, RequestVipFormOptions, RequestVipFormHealthcheck, \
    RequestVipFormReal, HealthcheckForm, RequestVipFormIP, GenerateTokenForm
from CadVlan.forms import DeleteForm, ValidateForm, CreateForm, RemoveForm
from CadVlan.messages import error_messages, request_vip_messages, \
    healthcheck_messages, equip_group_messages, auth_messages
from CadVlan.permissions import VIP_ADMINISTRATION, VIP_CREATE_SCRIPT,\
    VIP_VALIDATION, VIP_REMOVE_SCRIPT, VIPS_REQUEST
from CadVlan.settings import ACCESS_EXTERNAL_TTL, NETWORK_API_URL,\
    NETWORK_API_USERNAME, NETWORK_API_PASSWORD
from CadVlan.templates import VIPREQUEST_SEARCH_LIST, SEARCH_FORM_ERRORS, \
    AJAX_VIPREQUEST_LIST, VIPREQUEST_VIEW_AJAX, VIPREQUEST_FORM, \
    AJAX_VIPREQUEST_CLIENT, AJAX_VIPREQUEST_ENVIRONMENT, AJAX_VIPREQUEST_OPTIONS, \
    AJAX_VIPREQUEST_HEALTHCHECK, AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER, \
    AJAX_VIPREQUEST_MODEL_IP_REAL_SERVER_HTML, VIPREQUEST_EDIT, \
    VIPREQUEST_TAB_REAL_SERVER, VIPREQUEST_TAB_REAL_SERVER_STATUS, \
    VIPREQUEST_TAB_HEALTHCHECK, VIPREQUEST_TAB_MAXCON, VIPREQUEST_FORM_EXTERNAL, \
    VIPREQUEST_EDIT_EXTERNAL, VIPREQUEST_TOKEN, JSON_ERROR
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, \
    HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import loader
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from networkapiclient.exception import UserNotAuthenticatedError
from hashlib import sha1
from networkapiclient.ClientFactory import ClientFactory
from networkapiclient.Pagination import Pagination
from networkapiclient.exception import NetworkAPIClientError, VipError, \
    ScriptError, VipAllreadyCreateError, EquipamentoNaoExisteError, IpError, \
    VipNaoExisteError, IpNaoExisteError, InvalidParameterError, \
    InvalidTimeoutValueError, InvalidBalMethodValueError, InvalidCacheValueError, \
    InvalidPersistenceValueError, InvalidPriorityValueError, EnvironmentVipError, \
    IpEquipmentError, RealServerPriorityError, RealServerWeightError, \
    RealServerPortError, RealParameterValueError, RealServerScriptError, EnvironmentVipNotFoundError, IpNotFoundByEquipAndVipError
from time import strftime
import logging

from CadVlan.Ldap.model import Ldap, LDAPNotFoundError
import re
import hashlib, base64

logger = logging.getLogger(__name__)


OPERATION = { 0 : 'DELETE' , 1: 'VALIDATE', 2: 'CREATE', 3: 'REMOVE'}

@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "read": True},{"permission": VIPS_REQUEST, "write": True}])
def search_list(request): 
    try:
        
        lists = dict()
        lists["delete_form"] = DeleteForm()
        lists["validate_form"] = ValidateForm()
        lists["create_form"] = CreateForm()
        lists["remove_form"] = RemoveForm()
        lists["search_form"] = SearchVipRequestForm()
        lists['modal'] = 'false'
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(VIPREQUEST_SEARCH_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": VIPS_REQUEST, "read": True},{"permission": VIPS_REQUEST, "write": True}])
def ajax_list_vips(request):
    
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
                vip_create = search_form.cleaned_data["vip_create"]
                
                
                if len(ipv4) > 0:
                    ip = ipv4
                elif len(ipv6) > 0:
                    ip = ipv6
                else:
                    ip = None
                    
                # Pagination
                columnIndexNameMap = { 0: '', 1: 'id', 2 : 'ip', 3: 'descricao_ipv4', 4:'descricao_ipv6',5: 'equipamento', 6: 'ambiente', 7: 'valido', 8: 'criado',9: '' }
                dtp = DataTablePaginator(request, columnIndexNameMap)
                
                # Make params
                dtp.build_server_side_list()
                
                # Set params in simple Pagination class
                pag = Pagination(dtp.start_record, dtp.end_record, dtp.asorting_cols, dtp.searchable_columns, dtp.custom_search)
                
                # Call API passing all params
                vips = client.create_vip().find_vip_requests(id_vip, ip, pag, vip_create)
                
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

def ajax_shared_view_vip(request,id_vip, lists):
    
    lists['id_vip'] = id_vip
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        lists['vip'] = client.create_vip().get_by_id(id_vip).get('vip')
        
        if 'reals' in lists['vip']:
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
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def ajax_view_vip(request,id_vip):   
    lists= dict()
    return ajax_shared_view_vip(request, id_vip, lists)  
    
@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def delete_validate_create_remove(request, operation):
    
    operation_text = OPERATION.get(int(operation))
    
    if request.method == 'POST':

        form = DeleteForm(request.POST) if operation_text == 'DELETE' else ValidateForm(request.POST) if operation_text == 'VALIDATE' else CreateForm(request.POST) if operation_text == 'CREATE' else RemoveForm(request.POST)
        id = 'ids' if operation_text == 'DELETE' else 'ids_val' if operation_text == 'VALIDATE' else 'ids_create' if operation_text == 'CREATE' else 'ids_remove'
        
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
                        
                        client_vip.criar(id_vip)
                        
                    elif operation_text == 'VALIDATE':
                        #criar validar
                        client_vip.validate(id_vip)
                    
                    elif operation_text == 'REMOVE':
                        #remover
                        client_vip.remove_script(id_vip)
                
                except VipAllreadyCreateError, e:
                    logger.error(e)
                    error_list_created.append(id_vip) 
                except VipError, e:
                    logger.error(e)
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
                
                if operation_text == 'REMOVE':
                    msg = request_vip_messages.get('not_created') % msg[:-1]
                else:
                    msg = request_vip_messages.get('validate_before') % msg[:-1]
                messages.add_message(request, messages.WARNING, msg)
                have_errors = True
                    
            if len(error_list_created) > 0 :
                
                msg = ""
                for id_error in error_list_created:
                    msg = msg + id_error + ','
                
                msg = request_vip_messages.get('all_ready_create') % msg[:-1]
                messages.add_message(request, messages.WARNING, msg)
                have_errors = True
                
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
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('vip-request.list')    

@log
@login_required
@has_perm([{"permission": VIP_CREATE_SCRIPT, "write": True}])
def create_vip(request):
    delete_validate_create_remove(request, 2)
    # Redirect to list_all action
    return redirect('vip-request.list')  

@log
@login_required
@has_perm([{"permission": VIP_REMOVE_SCRIPT, "write": True}])
def remove_vip(request):
    delete_validate_create_remove(request, 3)
    # Redirect to list_all action
    return redirect('vip-request.list')  

@log
@login_required
@has_perm([{"permission": VIP_VALIDATION, "write": True}])   
def validate_vip(request):
    delete_validate_create_remove(request, 1)
    # Redirect to list_all action
    return redirect('vip-request.list')  

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "write": True}])
def delete_vip(request):
    delete_validate_create_remove(request, 0)
    # Redirect to list_all action
    return redirect('vip-request.list')  
    

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def ajax_validate_create_remove(request,id_vip, operation):
    
    operation_text = OPERATION.get(int(operation))

    # Get user
    auth = AuthSession(request.session)
    client_vip = auth.get_clientFactory().create_vip()

    msg = ""
    msg_type = ""
    changed = ""
    msg_error_call,msg_success_call = getErrorMessagesOne(operation_text)

    try:
        
        if operation_text == 'CREATE':
            client_vip.criar(id_vip)
            
        elif operation_text == 'VALIDATE':
            client_vip.validate(id_vip)
        
        elif operation_text == 'REMOVE':
            client_vip.remove_script(id_vip)
    
    except VipAllreadyCreateError, e:
        logger.error(e)
        msg = request_vip_messages.get('all_ready_create_one')
    except VipError, e:
        logger.error(e)
        msg = request_vip_messages.get('validate_before_one')
    except ScriptError, e:
        logger.error(e)
        msg = request_vip_messages.get(msg_error_call)
    except NetworkAPIClientError, e:
        logger.error(e)
        msg = request_vip_messages.get(msg_error_call)
    except Exception, e:
        logger.error(e)
        msg = e
        
    if (msg):
        msg_type = 'error'
    else:
        msg = request_vip_messages.get(msg_success_call)
        msg_type = 'success'
        changed = True
            
    # Return the shared view method with messages
    lists = dict()
    lists['message'] = msg
    lists['msg_type'] = msg_type
    if (changed):
        lists['changed'] = changed
    
    return ajax_shared_view_vip(request, id_vip, lists)
    

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
    
    elif operation_text == 'REMOVE':
        
        msg_erro = 'can_not_remove2_all'
        msg_sucesso = 'success_remove2'
        msg_erro_parcial = 'can_not_remove2'
    
    else:
        return None,None,None
    
    return msg_erro,msg_sucesso,msg_erro_parcial

def getErrorMessagesOne(operation_text):
    
    msg_erro = ""
    msg_sucesso = ""
    
    if operation_text == 'VALIDATE':
        msg_erro = 'can_not_validate_one'
        msg_sucesso = 'success_validate_one'
    elif operation_text == 'CREATE':
        msg_erro = 'can_not_create_one'
        msg_sucesso = 'success_create_one'
    elif operation_text == 'REMOVE':
        msg_erro = 'can_not_remove_one'
        msg_sucesso = 'success_remove_one'
    else:
        return None, None
    
    return msg_erro,msg_sucesso

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
        lists['ports_error'] = request_vip_messages.get("error_ports_required")
        is_valid = False
            
    return lists, is_valid


def valid_reals(lists, balancing, id_equip, id_ip, weight, priority):
    
    is_valid = True
    
    if id_equip is not None and id_ip is not None:
                    
        if str(balancing).upper() == "WEIGHTED":
        
            if len(id_equip) != len(weight) or len(id_equip) != len(priority):
                lists['reals_error'] = request_vip_messages.get("error_reals")
                is_valid = False
                
        if not priority:
            lists['reals_error'] = request_vip_messages.get("error_reals")
            is_valid = False
        
        else:
            if len(id_equip) != len(priority):
                lists['reals_error'] = request_vip_messages.get("error_reals")
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


def mount_table_reals(lists, id_equip, id_ip, weight, priority, equip, ip, version=None, status=None):

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

        if status is not None:
            for i in range(0, len(reals)):
                reals[i]['status'] = status[i]

        if version is not None:
            for i in range(0, len(reals)):
                reals[i]['version'] = version[i]
        
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
    is_error = False
    id_vip = None
    
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
                    
                    try:
                        if ipv4_type == '0': 
                            ipv4 = client_api.create_ip().get_available_ip4_for_vip(environment_vip, name).get("ip").get("id")
                            
                        else:
                            ipv4 = client_api.create_ip().check_vip_ip(ipv4_specific, environment_vip).get("ip").get("id")
                    except NetworkAPIClientError, e:
                        is_valid = False
                        is_error = True
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        
                if ipv6_check:
                    
                    ipv6_type = form_ip.cleaned_data["ipv6_type"]
                    ipv6_specific = form_ip.cleaned_data["ipv6_specific"]
                    
                    try:
                        if ipv6_type == '0': 
                            ipv6 = client_api.create_ip().get_available_ip6_for_vip(environment_vip, name).get("ip").get("id")
                            
                        else:
                            ipv6 = client_api.create_ip().check_vip_ip(ipv6_specific, environment_vip).get("ip").get("id")
                    except NetworkAPIClientError, e:
                        is_valid = False
                        is_error = True
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        
                if not is_error:
                
                    if edit:
                        client_api.create_vip().alter(idt, ipv4, ipv6, excpect, '0', created, finality, client, environment, caches, balancing, persistence, healthcheck_type, healthcheck, timeout, name, maxcom, business, service, filter_l7, reals, priority, weight, ports)
                        id_vip = idt
    
                    else:
                        vip = client_api.create_vip().add(ipv4, ipv6, excpect, finality , client, environment, caches, balancing, persistence, healthcheck_type, healthcheck, timeout, name, maxcom, business, service, filter_l7, reals, priority, weight, ports)
                        id_vip = vip.get("requisicao_vip").get("id")

                
            except NetworkAPIClientError, e:
                is_valid = False
                is_error = True
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)

            finally:
                try:

                    if is_error and ipv4_check and ipv4_type == '0' and ipv4 is not None:
                        client_api.create_ip().delete_ip4(ipv4)

                    if is_error and ipv6_check and ipv6_type == '0' and ipv6 is not None:
                        client_api.create_ip().delete_ip6(ipv6)

                except NetworkAPIClientError, e:
                    logger.error(e)
                
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
        
    return is_valid, id_vip

@csrf_exempt
@log
@access_external()
def add_form_external(request, form_acess, client):
    return add_form_shared(request, client, form_acess, True)


@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def add_form(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return add_form_shared(request, client_api)

@csrf_exempt
@log
@access_external()
def edit_form_external(request, id_vip, form_acess, client):
    return edit_form_shared(request, id_vip, client, form_acess, True)

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def edit_form(request, id_vip):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return edit_form_shared(request, id_vip, client_api)

@csrf_exempt
@access_external()
@log
def ajax_popular_client_external(request, form_acess, client):
    return popular_client_shared(request, client)

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def ajax_popular_client(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return popular_client_shared(request, client_api)

@csrf_exempt
@access_external()
@log
def ajax_popular_environment_external(request, form_acess, client):
    return popular_environment_shared(request, client)

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def ajax_popular_environment(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return popular_environment_shared(request, client_api)

@csrf_exempt
@access_external()
@log
def ajax_popular_options_external(request, form_acess, client):
    return popular_options_shared(request, client)

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def ajax_popular_options(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return popular_options_shared(request, client_api)

@csrf_exempt
@access_external()
@log
def ajax_add_healthcheck_external(request, form_acess, client):
    return popular_add_healthcheck_shared(request, client)

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def ajax_add_healthcheck(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return popular_add_healthcheck_shared(request, client_api)

@csrf_exempt
@access_external()
@log
def ajax_model_ip_real_server_external(request, form_acess, client):
    return model_ip_real_server_shared(request, client)

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def ajax_model_ip_real_server(request):
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()
    return model_ip_real_server_shared(request, client_api)

def parse_real_server(request, vip, client_api, id_vip, id_evip, is_status=False, valid = True):
    reals = []
    if "reals" in vip:
        reals = validates_dict(vip['reals'], 'real')
    
    prioritys = []
    if "reals_prioritys" in vip:
        prioritys = validates_dict(vip['reals_prioritys'], 'reals_priority')
    
    
    weights = []
    if "reals_weights" in vip:
        weights = validates_dict(vip['reals_weights'], 'reals_weight')
    
    id_equip = []
    id_ip = []
    weight = []
    priority = []
    equip = []
    ip = []
    status = []
    version = []
    for i in range(0, len(reals)):
        
        real = None
        
        try:
            
            real_name = reals[i].get("real_name")
            real_ip = reals[i].get("real_ip")
            
            real = client_api.create_vip().valid_real_server(real_ip, real_name , id_evip, valid).get("real")
            
            equip_aux = real.get("equipment")
            ip_aux = real.get("ip")
                      
            equip.append(equip_aux.get("nome"))
            id_equip.append(equip_aux.get("id"))
            
            id_ip.append(ip_aux.get("id"))
            ip.append(real_ip)
            
            if is_status:
            
                version.append(ip_aux.get("version"))
                
                try:
                
                    if ip_aux.get("version")  == IP_VERSION.IPv4[1]:
                        code = client_api.create_vip().checar_real(id_vip, ip_aux.get("id"), equip_aux.get("id"))
                    else:
                        code = client_api.create_vip().check_real_ipv6 (id_vip, ip_aux.get("id"), equip_aux.get("id"))
                    
                    if code is not None and 'sucesso' in code:
                        
                        code = int(code.get('sucesso').get('descricao').get('stdout'))
                        
                        if 2 == code: #Disable
                            status.append(0)
                            
                        elif 3 == code: #Enable
                            status.append(1)
                        
                        else:
                            status.append(0)
                        
                    else:
                        status.append(0)
                    
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    status.append(0)

            if prioritys:
                priority.append(prioritys[i])
    
            if weights:
                weight.append(weights[i])
                
        except (EquipamentoNaoExisteError, IpNaoExisteError, IpNotFoundByEquipAndVipError), e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_reals") % (real_name, real_ip))
        
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)    
    
    return  id_equip, id_ip, weight, priority, equip, ip, status, version


@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def tab_real_server_status(request, id_vip):

    try:
        
        lists = dict()
        lists['idt'] = id_vip
        lists['status_form'] = DeleteForm()
        
        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()
        
        vip = client_api.create_vip().get_by_id(id_vip).get("vip")
        vip['equipamento'] = validates_dict(vip, 'equipamento')
        vip['environments'] = validates_dict(vip, 'environments')
        vip['balancing'] = str(vip.get("metodo_bal")).upper()
        lists['vip'] = vip
        
        finality = vip.get("finalidade")
        client = vip.get("cliente")
        environment = vip.get("ambiente")

        id_evip = client_api.create_environment_vip().search(None, finality, client, environment).get("environment_vip").get("id")

        id_equip, id_ip, weight, priority, equip, ip, status, version = parse_real_server(request, vip, client_api, id_vip, id_evip, True)
            
        lists = mount_table_reals(lists, id_equip, id_ip, weight, priority, equip, ip, version, status)
    
    except EnvironmentVipNotFoundError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_environment_vip") %( finality, client, environment ))
    
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(VIPREQUEST_TAB_REAL_SERVER_STATUS, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def tab_real_server(request, id_vip):
    
    try:
        lists = dict()
        lists['idt'] = id_vip
        html = ''
        
        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()
        
        vip = client_api.create_vip().get_by_id(id_vip).get("vip")
        vip['equipamento'] = validates_dict(vip, 'equipamento')
        vip['environments'] = validates_dict(vip, 'environments')
        vip['balancing'] = str(vip.get("metodo_bal")).upper()
        lists['vip'] = vip
        
        finality = vip.get("finalidade")
        client = vip.get("cliente")
        environment = vip.get("ambiente")
        
        try:
            environment_vip = client_api.create_environment_vip().search(None, finality, client, environment).get("environment_vip").get("id")
            lists['environment_vip'] = environment_vip
        except Exception, e:
            environment_vip = None
            messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_environment_vip") %( finality, client, environment ))
            
        maxcon = vip.get("maxcon")   
        
        balancing = vip.get("metodo_bal")
        lists['balancing'] = balancing
                 
        form_real = RequestVipFormReal(initial={"maxcom": maxcon})
        lists['form_real'] = form_real
        
        parse = True
        
        #Already edited
        if request.method == "POST":
            try:
                
                priority = valid_field_table_dynamic(request.POST.getlist('priority')) if "priority" in request.POST else None
                weight = valid_field_table_dynamic(request.POST.getlist('weight')) if "weight" in request.POST else None
                id_equip = valid_field_table_dynamic(request.POST.getlist('id_equip')) if "id_equip" in request.POST else None
                equip = valid_field_table_dynamic(request.POST.getlist('equip')) if "equip" in request.POST else None
                id_ip = valid_field_table_dynamic(request.POST.getlist('id_ip')) if "id_ip" in request.POST else None
                ip = valid_field_table_dynamic(request.POST.getlist('ip')) if "ip" in request.POST else None
                
                lists, is_valid_reals = valid_reals(lists, balancing, id_equip, id_ip, weight, priority)
                if is_valid_reals:
                    reals = reals_(id_equip, id_ip, equip, ip)
                    client_api.create_vip().edit_reals(id_vip, balancing, reals, priority, weight)
                    
                    messages.add_message(request, messages.SUCCESS, request_vip_messages.get("tab_edit_success") % 'real server')
                else:
                    html = lists['reals_error']
                    parse = False
                
            except (EnvironmentVipError, InvalidTimeoutValueError, InvalidBalMethodValueError, InvalidCacheValueError, InvalidPersistenceValueError, InvalidPriorityValueError, EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, request_vip_messages.get("tab_edit_error") % 'real server')
                
                try:
                    raise e
                except InvalidTimeoutValueError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_timeout") % vip['timeout'])
                except InvalidBalMethodValueError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_balancing") % vip['balancing'])
                except InvalidCacheValueError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_cache") % vip['cache'])
                except InvalidPersistenceValueError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_persistence") % vip['persistencia'])
                except InvalidPriorityValueError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get("error_priority"))
                except EnvironmentVipError, e:
                    messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_environment_vip") %( finality, client, environment ))
                except (EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                    messages.add_message(request, messages.ERROR, e)
                
            except RealServerScriptError, e:
                logger.error(e)
                messages.add_message(request, messages.WARNING, e)
            except InvalidParameterError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
            except Exception, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                
        if parse is True:
            id_equip, id_ip, weight, priority, equip, ip, status, version = parse_real_server(request, vip, client_api, id_vip, environment_vip, True, False)
            lists = mount_table_reals(lists, id_equip, id_ip, weight, priority, equip, ip, version, status)
    
    except VipNaoExisteError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, request_vip_messages.get("invalid_vip"))
        return redirect('vip-request.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    if request.method == "POST":
        return HttpResponse(content=html, status=200)
    else:
        return render_to_response(VIPREQUEST_TAB_REAL_SERVER, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def tab_healthcheck(request, id_vip):
    
    try:
        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()
        
        lists = dict()
        lists['idt'] = id_vip
        
        vip = client_api.create_vip().get_by_id(id_vip).get("vip")
        vip['equipamento'] = validates_dict(vip, 'equipamento')
        vip['environments'] = validates_dict(vip, 'environments')
        vip['balancing'] = str(vip.get("metodo_bal")).upper()
        lists['vip'] = vip
        
        healthcheck_list =  client_api.create_ambiente().listar_healtchcheck_expect_distinct().get("healthcheck_expect")
        
        #Already edited
        if request.method == "POST":
            
            form_healthcheck = RequestVipFormHealthcheck(healthcheck_list, request.POST)
            lists['form_healthcheck'] = form_healthcheck
            
            if form_healthcheck.is_valid():
                
                healthcheck_type =  form_healthcheck.cleaned_data["healthcheck_type"]
                healthcheck =  form_healthcheck.cleaned_data["healthcheck"]
                excpect =  form_healthcheck.cleaned_data["excpect"]
                
                if excpect is not None:
                    excpect = int(excpect)
                
                try:
                    
                    finality = vip.get("finalidade")
                    client = vip.get("cliente")
                    environment = vip.get("ambiente")
                    
                    environment_vip = client_api.create_environment_vip().search(None, finality, client, environment)
                    if environment_vip is None:
                        raise EnvironmentVipError(environment_vip)
                    
                    
                    client_api.create_vip().alter_healthcheck(id_vip, healthcheck_type, healthcheck, excpect)
                    messages.add_message(request, messages.SUCCESS, request_vip_messages.get("tab_edit_success") % 'healthcheck')
                    
                except (EnvironmentVipError, InvalidTimeoutValueError, InvalidBalMethodValueError, InvalidCacheValueError, InvalidPersistenceValueError, InvalidPriorityValueError, EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, request_vip_messages.get("tab_edit_error") % 'healthcheck')
                    
                    try:
                        raise e
                    except InvalidTimeoutValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_timeout") % vip['timeout'])
                    except InvalidBalMethodValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_balancing") % vip['balancing'])
                    except InvalidCacheValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_cache") % vip['cache'])
                    except InvalidPersistenceValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_persistence") % vip['persistencia'])
                    except InvalidPriorityValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_priority"))
                    except EnvironmentVipError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_environment_vip") %( finality, client, environment ))
                    except (EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                        messages.add_message(request, messages.ERROR, e)
                    
                    
                except InvalidParameterError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                except Exception, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    
                    
        #Request to edit
        else:
            excpect = vip.get("id_healthcheck_expect")
            healthcheck_type = vip.get("healthcheck_type")
            healthcheck = vip.get("healthcheck")
            
            form_healthcheck = RequestVipFormHealthcheck(healthcheck_list, initial={"healthcheck_type": healthcheck_type, "healthcheck": healthcheck, "excpect": excpect})
            
            lists['form_healthcheck'] = form_healthcheck
            
        
    except VipNaoExisteError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, request_vip_messages.get("invalid_vip"))
        return redirect('vip-request.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VIPREQUEST_TAB_HEALTHCHECK, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def tab_maxcon(request, id_vip):
    
    try:
        # Get user
        auth = AuthSession(request.session)
        client_api = auth.get_clientFactory()
        
        lists = dict()
        lists['idt'] = id_vip
        
        vip = client_api.create_vip().get_by_id(id_vip).get("vip")
        vip['equipamento'] = validates_dict(vip, 'equipamento')
        vip['environments'] = validates_dict(vip, 'environments')
        vip['balancing'] = str(vip.get("metodo_bal")).upper()
        lists['vip'] = vip
        
        #Already edited
        if request.method == "POST":
            
            form_real = RequestVipFormReal(request.POST)
            lists['form_real'] = form_real
            
            if form_real.is_valid():
                
                maxcon = form_real.cleaned_data["maxcom"]
                #equip_name = form_real.cleaned_data["equip_name"]
                
                try:
                    
                    finality = vip.get("finalidade")
                    client = vip.get("cliente")
                    environment = vip.get("ambiente")
                    
                    environment_vip = client_api.create_environment_vip().search(None, finality, client, environment)
                    if environment_vip is None:
                        raise EnvironmentVipError(environment_vip)
                    
                    client_api.create_vip().alter_maxcon(id_vip, maxcon)
                    messages.add_message(request, messages.SUCCESS, request_vip_messages.get("tab_edit_success") % 'maxconn')
                    
                except (EnvironmentVipError, InvalidTimeoutValueError, InvalidBalMethodValueError, InvalidCacheValueError, InvalidPersistenceValueError, InvalidPriorityValueError, EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, request_vip_messages.get("tab_edit_error") % 'maxconn')
                    
                    try:
                        raise e
                    except InvalidTimeoutValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_timeout") % vip['timeout'])
                    except InvalidBalMethodValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_balancing") % vip['balancing'])
                    except InvalidCacheValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_cache") % vip['cache'])
                    except InvalidPersistenceValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_persistence") % vip['persistencia'])
                    except InvalidPriorityValueError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_priority"))
                    except EnvironmentVipError, e:
                        messages.add_message(request, messages.ERROR, request_vip_messages.get("error_existing_environment_vip") %( finality, client, environment ))
                    except (EquipamentoNaoExisteError, IpEquipmentError, IpError, RealServerPriorityError, RealServerWeightError, RealServerPortError, RealParameterValueError), e:
                        messages.add_message(request, messages.ERROR, e)
                    
                    
                except InvalidParameterError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                except Exception, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    
        #Request to edit
        else:
            maxcon = vip.get("maxcon")
            equip_name = vip.get("equip_name")
            
            form_real = RequestVipFormReal(initial={"equip_name": equip_name, "maxcom": maxcon})
            lists['form_real'] = form_real
        
        
        
    except VipNaoExisteError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, request_vip_messages.get("invalid_vip"))
        return redirect('vip-request.form')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VIPREQUEST_TAB_MAXCON, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": VIP_ADMINISTRATION, "read": True},{"permission": VIP_ADMINISTRATION, "write": True}])
def status_real_server(request, id_vip, status):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_api = auth.get_clientFactory()
            client_vip = auth.get_clientFactory().create_vip()

            # All ids to be change status
            ids = split_to_array(form.cleaned_data['ids'])
            
            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False
            
            enable = False
            if status == "enable":
                enable = True

            for idts in ids:
                
                try:
                    
                    idt_vector = split_to_array(idts, sep="-")
                    
                    equip_id = idt_vector[0]
                    ip_id = idt_vector[1]
                    version = idt_vector[2]
                    
                    if version == IP_VERSION.IPv4[1]:
                        
                        if enable:
                            client_vip.habilitar_real(id_vip, ip_id, equip_id)
                        else:
                            client_vip.desabilitar_real(id_vip, ip_id, equip_id)
                    
                    elif version == IP_VERSION.IPv6[1]:
                        
                        if enable:
                            client_vip.enable_real_ipv6(id_vip, ip_id, equip_id)
                        else:
                            client_vip.disable_real_ipv6(id_vip, ip_id, equip_id)

                except ScriptError, e:
                    logger.error(e)
                    have_errors = True
                    equip_aux = client_api.create_equipamento().listar_por_id(equip_id).get("equipamento")
                    error_list.append(equip_aux.get("nome"))

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant change nothing
            if len(error_list) == len(ids):
                messages.add_message(request, messages.ERROR, request_vip_messages.get("can_not_real_all") % ('Habilitar' if enable else 'Desabilitar') )

            # If cant change someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                messages.add_message(request, messages.WARNING, request_vip_messages.get("can_not_real") % ( ('Habilitar' if enable else 'Desabilitar'),  msg[:-2]))
                
            # If all has ben changed
            elif have_errors == False:
                messages.add_message(request, messages.SUCCESS, request_vip_messages.get("success_real") % ('Habilitado' if enable else 'Desabilitado') )

            else:
                messages.add_message(request, messages.SUCCESS, request_vip_messages.get("can_not_real") % ('Habilitar' if enable else 'Desabilitar') )

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    return HttpResponseRedirect(reverse('vip-request.tab.real.server.status.edit', args=[id_vip]))

@csrf_exempt
@log
def generate_token(request):
    try:
        
        lists = {}
        
        form = GenerateTokenForm(request.POST) if request.method == 'POST' else GenerateTokenForm()            
        
        if form.is_valid():
            
            user_ldap_ass = ""
            user = str(form.cleaned_data['user'])
            idt  = None if not form.cleaned_data['requestVip'] else form.cleaned_data['requestVip'] 
            ttl  = ACCESS_EXTERNAL_TTL if not form.cleaned_data['p'] else form.cleaned_data['p']
            
            #Login with LDAP
            if form.cleaned_data['is_ldap_user']:
                username_ldap, password_ldap = str(user).split("@")
                try:
                    user_ldap = Ldap("").get_user(username_ldap)
                except LDAPNotFoundError, e:
                    raise Exception(auth_messages.get("user_ldap_not_found"))

                pwd_ldap = user_ldap['userPassword']
                activate = user_ldap.get('nsaccountlock')
                pwd = password_ldap
                
                if re.match("\{(MD|md)5\}.*", pwd_ldap, 0):
                    pwd = base64.b64encode(hashlib.md5(pwd).digest())
                    pwd_ldap = pwd_ldap[pwd_ldap.index("}")+1:]
                    
                if pwd == pwd_ldap and (activate is None or activate.upper() == 'FALSE'):
                    #Valid User
                    client, client_user = validate_user_networkapi(user, form.cleaned_data['is_ldap_user'])
                    user_ldap_client = client_user.get('user')
                    user_ldap_ass = user_ldap_client['user_ldap']
                else:
                    client_user = None
            else:
                #Valid User
                client, client_user = validate_user_networkapi(user, form.cleaned_data['is_ldap_user'])
            
            
            #Valid User
            if client_user is None:
                raise UserNotAuthenticatedError("user_invalid")
            else:
                #Valid idt
                if idt is not None and not is_valid_int_param(idt):
                    raise Exception(error_messages.get("invalid_param") % "requestVip")
                
                #Valid ttl
                if not is_valid_int_param(ttl):
                    raise Exception(error_messages.get("invalid_param") % "p")
    
                if idt is not None:
                    client.create_vip().get_by_id(idt)
    
                #Encrypt hash
                user_hash = Encryption().Encrypt(user+"@"+str(user_ldap_ass))
                
                #Generates token
                key = "%s:%s:%s" % ( __name__, str(user) , str(strftime("%Y%m%d%H%M%S")))
                token = sha1(key).hexdigest()
                
                # Set token in cache
                cache.set(token, user_hash, int(ttl))
                
                lists["token"] = token
                lists["url"] = reverse("vip-request.edit.external", args=[idt]) if idt is not None else reverse("vip-request.form.external")
            
            
            return render_to_response(VIPREQUEST_TOKEN, lists, context_instance=RequestContext(request))
        
    except InvalidParameterError, e:
        logger.error(e)
        lists["error"] = error_messages.get("invalid_param") % "id"
             
    except VipNaoExisteError, e:         
        logger.error(e)
        lists["error"] = request_vip_messages.get("invalid_vip")
    except Exception, e:
        logger.error(e)
        lists["error"] = e  

        
    return render_to_response(JSON_ERROR, lists, context_instance=RequestContext(request))

def validate_user_networkapi(user_request, is_ldap_user):
    
    try:
        
        username, password = str(user_request).split("@")
        
        client = ClientFactory(NETWORK_API_URL, NETWORK_API_USERNAME, NETWORK_API_PASSWORD)
            
        client_user = client.create_usuario().authenticate(username, password, is_ldap_user)
        
    except Exception,  e:
        logger.error(e)
        raise UserNotAuthenticatedError(e)
        
    return client, client_user

def add_form_shared(request, client_api, form_acess = "", external = False):

    try:
        
        lists = dict()
        lists['ports'] = ''
        lists['ports_error'] = ''
        lists['reals_error'] = ''
        lists['form_acess'] = form_acess
        lists['external'] = True if external else False
        
        finality_list =  client_api.create_environment_vip().buscar_finalidade().get("finalidade")
        healthcheck_list =  client_api.create_ambiente().listar_healtchcheck_expect_distinct().get("healthcheck_expect")

        if request.method == "POST":
            
            is_valid, id_vip = valid_form_and_submit(request, lists, finality_list, healthcheck_list, client_api)
            
            if is_valid:
                messages.add_message(request, messages.SUCCESS, request_vip_messages.get("success_insert"))
                
                if external:
                    return HttpResponseRedirect("%s?token=%s" % (reverse('vip-request.edit.external', args=[id_vip]), form_acess.initial.get("token")))
                else:
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
        
        
    template =  VIPREQUEST_FORM_EXTERNAL if external else VIPREQUEST_FORM

    return render_to_response(template, lists, context_instance=RequestContext(request))

def edit_form_shared(request, id_vip, client_api, form_acess = "", external = False):

    try:
        
        lists = dict()
        lists['ports'] = ''
        lists['ports_error'] = ''
        lists['idt'] = id_vip
        lists['form_acess'] = form_acess
        lists['external'] = True if external else False
        
        vip = client_api.create_vip().buscar(id_vip).get("vip")
        
        finality_list =  client_api.create_environment_vip().buscar_finalidade().get("finalidade")
        healthcheck_list =  client_api.create_ambiente().listar_healtchcheck_expect_distinct().get("healthcheck_expect")
        
        if request.method == "POST":
            
            is_valid, id_vip = valid_form_and_submit(request, lists, finality_list, healthcheck_list, client_api, edit = True, idt = id_vip)
            
            if is_valid:
                messages.add_message(request, messages.SUCCESS, request_vip_messages.get("success_edit"))
                
                if external:
                    return HttpResponseRedirect("%s?token=%s" % (reverse('vip-request.edit.external', args=[id_vip]), form_acess.initial.get("token")))
                else:
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
            
                environment_vip = client_api.create_environment_vip().search(None, finality, client, environment).get("environment_vip").get("id")
                
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
            
            id_equip, id_ip, weight, priority, equip, ip, status, version = parse_real_server(request, vip, client_api, id_vip, environment_vip, False, False)
                
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
        
    template =  VIPREQUEST_EDIT_EXTERNAL if external else VIPREQUEST_EDIT

    return render_to_response(template, lists, context_instance=RequestContext(request))


def popular_client_shared(request, client_api):

    lists = dict()
    status_code = None
    lists['clients'] = ''

    try:    
        finality = get_param_in_request(request, 'finality')

        if finality is None:
            raise InvalidParameterError("Parâmetro inválido: O campo finalidade inválido ou não foi informado.")
        
        client_evip = client_api.create_environment_vip()
        
        lists['clients'] = validates_dict(client_evip.buscar_cliente_por_finalidade(finality), 'cliente_txt')
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500
        
    # Returns HTML
    return HttpResponse(loader.render_to_string(AJAX_VIPREQUEST_CLIENT, lists, context_instance=RequestContext(request)), status=status_code)

def popular_environment_shared(request, client_api):

    lists = dict()
    status_code = None
    lists['environments'] = ''

    try:
        
        finality = get_param_in_request(request, 'finality')
        if finality is None:
            raise InvalidParameterError("Parâmetro inválido: O campo finalidade inválido ou não foi informado.")
        
        client = get_param_in_request(request, 'client')
        if client is None:
            raise InvalidParameterError("Parâmetro inválido: O campo cliente inválido ou não foi informado.")
        
        client_evip = client_api.create_environment_vip()
        
        lists['environments'] = validates_dict(client_evip.buscar_ambientep44_por_finalidade_cliente(finality, client), 'ambiente_p44')
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500
        
    # Returns HTML
    return HttpResponse(loader.render_to_string(AJAX_VIPREQUEST_ENVIRONMENT, lists, context_instance=RequestContext(request)), status=status_code)


def popular_options_shared(request, client_api):

    lists = dict()
    status_code = None

    try:    
        environment_vip = get_param_in_request(request, 'environment_vip')
        if environment_vip is None:
            raise InvalidParameterError("Parâmetro inválido: O campo Ambiente Vip inválido ou não foi informado.")
        
        client_ovip = client_api.create_option_vip()
        
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


def popular_add_healthcheck_shared(request, client_api):
    
    lists = dict()
    status_code = None
    form = HealthcheckForm()

    try:
        
        client = client_api.create_ambiente()
        
        if request.method == "GET":
            form = HealthcheckForm(request.GET)
            
        else:
            form = HealthcheckForm(request.POST)
        

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


def model_ip_real_server_shared(request, client_api):
    
    lists = dict()
    lists['msg'] = ''
    lists['ips'] = ''
    ips = None
    equip = None
    balancing = None
    status_code = None

    try:
        
        
        id_evip = get_param_in_request(request, 'environment_vip')
        equip_name = get_param_in_request(request, 'equip_name')
        balancing = get_param_in_request(request, 'balancing')
        
        equip_real = split_to_array(get_param_in_request(request, 'equip_real') ) if get_param_in_request(request, 'equip_real') is not None else None
        ips_real = split_to_array(get_param_in_request(request, 'ips_real') ) if get_param_in_request(request, 'ips_real') is not None else None
                
        #Valid Equipament
        equip = client_api.create_equipamento().listar_por_nome(equip_name).get("equipamento")
        
        ips = client_api.create_ip().get_ip_by_equip_and_vip(equip_name, id_evip)
        
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
