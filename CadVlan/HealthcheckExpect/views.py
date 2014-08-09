# -*- coding:utf-8 -*-
'''
Created on 23/07/2012
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.permissions import HEALTH_CHECK_EXPECT
from CadVlan.messages import healthcheck_messages
from CadVlan.templates import HEALTHCHECKEXPECT_FORM
import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.HealthcheckExpect.forms import HealthckeckExpectForm

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{'permission':HEALTH_CHECK_EXPECT, "write": True}])
def healthcheck_expect_form(request):
    
    lists = dict()
    
    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        ambientes = client.create_ambiente().list_all()
        
        if request.method == 'POST':
            
            form =  HealthckeckExpectForm(ambientes,request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                match_list = form.cleaned_data['match_list']
                expect_string = form.cleaned_data['expect_string']
                environment_id = form.cleaned_data['environment']
                
                client.create_ambiente().add_healthcheck_expect(environment_id, expect_string, match_list)
                messages.add_message(request,messages.SUCCESS, healthcheck_messages.get('success_create'))
                
                lists['form'] =  HealthckeckExpectForm(ambientes) 
            
        #GET METHOD
        else:
            lists['form'] = HealthckeckExpectForm(ambientes)
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request,messages.ERROR, e)
        
        
    return render_to_response(HEALTHCHECKEXPECT_FORM,lists,context_instance=RequestContext(request))