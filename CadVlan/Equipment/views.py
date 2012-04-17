# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.views.decorators.cache import cache_page
from CadVlan.settings import CACHE_TIMEOUT
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Equipment.business import cache_list_equipment
from CadVlan.Util.shortcuts import render_to_response_ajax
from CadVlan.templates import AJAX_EQUIPMENT_LIST
from django.template.context import RequestContext

logger = logging.getLogger(__name__)

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def ajax_list_equips(request):
    try:
        
        equip_list = dict()
        
        # Get user auth
        auth = AuthSession(request.session)
        equipment = auth.get_clientFactory().create_equipamento()
        
        # Get list of equipments from cache
        equip_list = cache_list_equipment(equipment)
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response_ajax(AJAX_EQUIPMENT_LIST, equip_list, context_instance=RequestContext(request))
