# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import ENVIRONMENT_LIST
from CadVlan.settings import CACHE_TIMEOUT
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.permissions import ENVIRONMENT_MANAGEMENT
from CadVlan.forms import DeleteForm

logger = logging.getLogger(__name__)

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm([{"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def list_all(request):
    
    try:
        
        lists = dict();
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get all scripts from NetworkAPI
        environment = client.create_ambiente().listar()
        
        # Business
        lists['environment'] = environment.get("ambiente")
        lists['form'] = DeleteForm()
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(ENVIRONMENT_LIST, lists, context_instance=RequestContext(request))