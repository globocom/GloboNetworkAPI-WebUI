# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import VIPREQUEST_SEARCH_LIST,\
    SEARCH_FORM_ERRORS, AJAX_VIPREQUEST_LIST, VIPREQUEST_VIEW_AJAX
from django.contrib import messages
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError, VipError,\
    ScriptError, VipAllreadyCreateError
import logging
from django.shortcuts import render_to_response, redirect
from CadVlan.forms import DeleteForm, ValidateForm, CreateForm
from CadVlan.VipRequest.forms import SearchVipRequestForm
from CadVlan.Util.utility import DataTablePaginator
from networkapiclient.Pagination import Pagination
from django.http import HttpResponse, HttpResponseServerError
from django.template import loader
from CadVlan.Util.converters.util import split_to_array
from CadVlan.messages import error_messages, request_vip_messages

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
    