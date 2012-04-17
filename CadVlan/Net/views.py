# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.settings import CACHE_TIMEOUT
from django.shortcuts import render_to_response, redirect
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.permissions import VLAN_MANAGEMENT, EQUIPMENT_MANAGEMENT,\
    NETWORK_TYPE_MANAGEMENT
from CadVlan.templates import  NETIPV4, NETIPV6
from CadVlan.Util.converters.util import replace_id_to_name

logger = logging.getLogger(__name__)

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def list_netip4_by_id(request, id_net):
    
    lists = dict()
    
    try:
            
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
            
            
        #recuperando lista de vlans
        net = client.create_network().get_network_ipv4(id_net)
            
        vlan = client.create_vlan().get(net.get('network').get('vlan'))
            
        net['network']['vlan'] = vlan.get('vlan').get('nome')
            
        tipo_rede = client.create_tipo_rede().listar()
           
                        
        lists['net'] = replace_id_to_name([net['network']], tipo_rede['tipo_rede'], "network_type", "id", "nome")
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('vlan.search.list') 
    
    try:
            
        ips = client.create_ip().find_ip4_by_network(id_net)
        
        ips = ips.get('ips')
        
        list_nomes = []
        
        for ip in ips:
            list_nomes = []
            if type(ip.get('equipamento')) == list:
                for equip in ip.get('equipamento'):
                    list_nomes.append(equip.get('nome'))
                ip['equipamento'] = list_nomes
            else:
                list_nomes = [ip.get('equipamento').get('nome')]
                ip['equipamento'] = list_nomes 
                             
        
        lists['ips'] = ips
              
        return render_to_response(NETIPV4, lists , context_instance=RequestContext(request))
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists['ips'] = None
    except TypeError,e:
        logger.error(e)
        messages.add_message(request,messages.ERROR,e)
        
    return render_to_response(NETIPV4,lists, context_instance=RequestContext(request))

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def list_netip6_by_id(request, id_net):
        
    lists = dict()
    
    try:
            
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
            
            
        #recuperando lista de vlans
        net = client.create_network().get_network_ipv6(id_net)
            
        vlan = client.create_vlan().get(net.get('network').get('vlan'))
            
        net['network']['vlan'] = vlan.get('vlan').get('nome')
            
        tipo_rede = client.create_tipo_rede().listar()
           
                        
        lists['net'] = replace_id_to_name([net['network']], tipo_rede['tipo_rede'], "network_type", "id", "nome")
        lists['id'] = id_net
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('vlan.search.list') 
        
    try:
            
        ips = client.create_ip().find_ip6_by_network(id_net)
        
        ips = ips.get('ips')
        
        list_nomes = []
        
        for ip in ips:
            list_nomes = []
            if type(ip.get('equipamento')) == list:
                for equip in ip.get('equipamento'):
                    list_nomes.append(equip.get('nome'))
                ip['equipamento'] = list_nomes
            else:
                list_nomes = [ip.get('equipamento').get('nome')]
                ip['equipamento'] = list_nomes 
                
        print ips
                             
        
        lists['ips'] = ips
            
        return render_to_response(NETIPV6, lists , context_instance=RequestContext(request))
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists['ips'] = None
    except TypeError,e:
        logger.error(e)
        messages.add_message(request,messages.ERROR,e)
        
    return render_to_response(NETIPV6,lists, context_instance=RequestContext(request))        