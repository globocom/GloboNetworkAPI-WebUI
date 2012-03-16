# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Auth.Decorators import log, login_required, has_perm
from CadVlan.templates import EQUIPMENTACESS_SEARCH_LIST
from CadVlan.settings import CACHE_TIMEOUT
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import UserNotAuthorizedError, XMLError, DataBaseError, NetworkAPIClientError
from django.contrib import messages
from CadVlan.EquipAccess.forms import SearchEquipAccessForm
from CadVlan.Util.converters.util import replace_id_to_name

logger = logging.getLogger(__name__)


@log
@login_required
@cache_page(CACHE_TIMEOUT)
#@has_perm('criar permissao', write = True)
def search_list(request):
    
    try:
        
        if request.method == "GET":
            
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            if not request.GET.__contains__('equip_name'):
                form = SearchEquipAccessForm()
            else:
                form = SearchEquipAccessForm(request.GET)
            
            if form.is_valid():
                
                #recuperar nome do equipamento pesquisado
                name_equip = form.cleaned_data['equip_name']
                
                #recuperando lista de equipamentos de acesso
                equip_access_list = client.create_equipamento_acesso().list_by_equip(name_equip)
                
                access_type = client.create_tipo_acesso().listar()
                
                equip_access_list = replace_id_to_name(equip_access_list["equipamento_acesso"], access_type["tipo_acesso"], "tipo_acesso", "id", "protocolo")
                
                return render_to_response(EQUIPMENTACESS_SEARCH_LIST, {'form': form,'equipamento_acesso':equip_access_list}, context_instance=RequestContext(request))
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(EQUIPMENTACESS_SEARCH_LIST, {'form': form}, context_instance=RequestContext(request))