# -*- coding:utf-8 -*-
'''
Created on 23/07/2012
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''
import logging
from CadVlan.permissions import NETWORK_TYPE_MANAGEMENT
from CadVlan.messages import type_network_messages
from CadVlan.templates import  NETWORKTYPE_FORM
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.NetworkType.forms import TipoRedeForm

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{'permission':NETWORK_TYPE_MANAGEMENT, "write": True}])
def network_type_form(request):
    
    lists = dict()
    
    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        if request.method == 'POST':
            
            form =  TipoRedeForm(request.POST)
            lists['form'] =  form
            
            if form.is_valid():
                
                name = form.cleaned_data['name']
                
                client.create_tipo_rede().inserir(name)
                messages.add_message(request,messages.SUCCESS, type_network_messages.get('success_create'))
                
                lists['form'] =  TipoRedeForm()
            
        #GET METHOD
        else:
            lists['form'] = TipoRedeForm()
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request,messages.ERROR, e)
        
    return render_to_response(NETWORKTYPE_FORM,lists,context_instance=RequestContext(request))