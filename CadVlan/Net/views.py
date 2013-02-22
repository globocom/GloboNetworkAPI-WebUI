# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, VipIpError, IpEquipCantDissociateFromVip
from django.contrib import messages
from CadVlan.permissions import VLAN_MANAGEMENT, EQUIPMENT_MANAGEMENT, NETWORK_TYPE_MANAGEMENT, ENVIRONMENT_VIP, IPS
from CadVlan.templates import  NETIPV4, NETIPV6, IP4, IP6, IP4EDIT, IP6EDIT, IP4ASSOC, IP6ASSOC, NET_FORM, NET6_EDIT, NET4_EDIT
from CadVlan.Util.converters.util import replace_id_to_name, split_to_array
from CadVlan.Net.forms import IPForm, IPEditForm, IPAssocForm, NetworkForm, NetworkEditForm
from CadVlan.Net.business import is_valid_ipv4, is_valid_ipv6
from CadVlan.messages import network_ip_messages
from CadVlan.forms import DeleteForm
from CadVlan.messages import error_messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from CadVlan.OptionVip.forms import OptionVipNetForm


logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_VIP, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def add_network_form(request):
    
    lists = dict()
    
    try:
        
        # Get User
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get all needs from NetworkAPI
        net_type_list = client.create_tipo_rede().listar()
        env_vip_list = client.create_environment_vip().list_all()
        
        # Forms
        lists['form'] = NetworkForm(net_type_list, env_vip_list)
        
        # If form was submited
        if request.method == 'POST':
            
            # Set data in form
            form = NetworkForm(net_type_list, env_vip_list, request.POST)
            
            # Validate
            if form.is_valid():
                
                vlan_id = form.cleaned_data['vlan_name_id']
                net_type = form.cleaned_data['net_type']
                env_vip = form.cleaned_data['env_vip']
                net_version = form.cleaned_data['ip_version']
                networkv4 = form.cleaned_data['networkv4']
                networkv6 = form.cleaned_data['networkv6']
                
                if net_version == "0":
                    network = networkv4
                else:
                    network = networkv6
                
                # Business
                client.create_vlan().get(vlan_id)
                client.create_network().add_network(network, vlan_id, net_type, env_vip)
                messages.add_message(request, messages.SUCCESS, network_ip_messages.get("success_insert"))
                
                return HttpResponseRedirect(reverse('vlan.list.by.id', args=[vlan_id]))
            
            else:
                # If invalid, send all error messages in fields
                lists['form'] = form
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        # If some api error occurred, try to send data to html
        try:
            lists['form'] = form
        except NameError:
            pass
    
    return render_to_response(NET_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_VIP, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def vlan_add_network_form(request, id_vlan):
    
    lists = dict()
    
    try:
        
        if request.method == 'GET':
            
            # Get User
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            # Get all needs from NetworkAPI
            net_type_list = client.create_tipo_rede().listar()
            env_vip_list = client.create_environment_vip().list_all_available(id_vlan)
            
            # Business
            vlan = client.create_vlan().get(id_vlan)
            vlan = vlan.get("vlan")
            
            environment =  client.create_ambiente().buscar_por_id(vlan.get("ambiente")).get("ambiente")
            vlan_nome = "%s | %s - %s - %s" %(  vlan.get("num_vlan"), environment.get("nome_divisao"), environment.get("nome_ambiente_logico"), environment.get("nome_grupo_l3"))
            
            # Forms
            lists['form'] = NetworkForm(net_type_list, env_vip_list, initial={'vlan_name':vlan_nome, 'vlan_name_id': vlan.get("id")})
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(NET_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def list_netip4_by_id(request, id_net):
    
    lists = dict()
    
    try:
        
        lists['aba'] = 0
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
            
            
        #recuperando lista de vlans
        net = client.create_network().get_network_ipv4(id_net)
            
        vlan = client.create_vlan().get(net.get('network').get('vlan'))
        lists['vlan_id'] = vlan['vlan']['id']
            
        net['network']['vlan'] = vlan.get('vlan').get('nome')
            
        net_type = client.create_tipo_rede().listar()
        
        id_vip =  net.get('network').get("ambient_vip")
        
        if id_vip is None:
            id_vip = 0
            
        else:
            
            lists['vip'] = client.create_environment_vip().search(id_vip).get("environment_vip")
            opts = client.create_option_vip().get_all()
            options_vip = client.create_option_vip().get_option_vip(id_vip)
            choice_opts = []
            if options_vip is not None:
                options_vip = options_vip.get('option_vip')
                
                
                if type (options_vip) == dict:
                    options_vip = [options_vip]
                    
                for opt in options_vip:
                    choice_opts.append(opt.get("id"))
                    
            lists['opt_form'] = OptionVipNetForm(opts, initial = {'option_vip':choice_opts})
            
        lists['id_vip'] = id_vip
           
                        
        lists['net'] = replace_id_to_name([net['network']], net_type['net_type'], "network_type", "id", "name")
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('vlan.search.list') 
    
    try:
            
        ips = client.create_ip().find_ip4_by_network(id_net)
        
        ips = ips.get('ips')
        
        ips_to_screen = []
        
        list_nomes = []
        
        for ip in ips:
            list_nomes = []
            if type(ip.get('equipamento')) == list:
                for equip in ip.get('equipamento'):
                    ip2 = dict()
                    ip2['id'] = ip['id']
                    ip2['oct1'] = ip['oct1']
                    ip2['oct2'] = ip['oct2']
                    ip2['oct3'] = ip['oct3']
                    ip2['oct4'] = ip['oct4']
                    ip2['descricao'] = ip['descricao']
                    ip2['equip_name'] = equip.get('nome')
                    ip2['equip_id'] = equip.get('id')
                    ips_to_screen.append(ip2)
                    
                    list_nomes.append(equip.get('nome'))
                    
                ip['equipamento'] = list_nomes
            else:
                ip2 = dict()
                ip2['id'] = ip['id']
                ip2['oct1'] = ip['oct1']
                ip2['oct2'] = ip['oct2']
                ip2['oct3'] = ip['oct3']
                ip2['oct4'] = ip['oct4']
                ip2['descricao'] = ip['descricao']
                ip2['equip_name'] = ip.get('equipamento').get('nome')
                ip2['equip_id'] = ip.get('equipamento').get('id')
                ips_to_screen.append(ip2)
                
                list_nomes = [ip.get('equipamento').get('nome')]
                ip['equipamento'] = list_nomes              
                             
        
        lists['ips'] = ips_to_screen
        lists['id'] = id_net
        lists['delete_form'] = DeleteForm()
        return render_to_response(NETIPV4, lists , context_instance=RequestContext(request))
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists['ips'] = None
    except TypeError,e:
        logger.error(e)
        messages.add_message(request,messages.ERROR,e)
        
    lists['id'] = id_net
    lists['delete_form'] = DeleteForm()
    return render_to_response(NETIPV4,lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def list_netip6_by_id(request, id_net):
        
    lists = dict()
    
    try:
        
        lists['aba'] = 0
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
            
            
        #recuperando lista de vlans
        net = client.create_network().get_network_ipv6(id_net)
            
        vlan = client.create_vlan().get(net.get('network').get('vlan'))
        lists['vlan_id'] = vlan.get('vlan')['id']
            
        net['network']['vlan'] = vlan.get('vlan').get('nome')
            
        net_type = client.create_tipo_rede().listar()
        
        id_vip =  net.get('network').get("ambient_vip")
        
        if id_vip is None:
            id_vip = 0
            
        else:
            
            lists['vip'] = client.create_environment_vip().search(id_vip).get("environment_vip")
            opts = client.create_option_vip().get_all()
            options_vip = client.create_option_vip().get_option_vip(id_vip)
            choice_opts = []
            if options_vip is not None:
                options_vip = options_vip.get('option_vip')
                
                
                if type (options_vip) == dict:
                    options_vip = [options_vip]
                    
                for opt in options_vip:
                    choice_opts.append(opt.get("id"))
                    
            lists['opt_form'] = OptionVipNetForm(opts, initial = {'option_vip':choice_opts})
            
        lists['id_vip'] = id_vip
           
                        
        lists['net'] = replace_id_to_name([net['network']], net_type['net_type'], "network_type", "id", "name")
        
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return redirect('vlan.search.list') 
        
    try:
            
        ips = client.create_ip().find_ip6_by_network(id_net)
    
        ips = ips.get('ips')
        
        ips_to_screen = []
        
        list_nomes = []
        
        for ip in ips:
            list_nomes = []
            if type(ip.get('equipamento')) == list:
                for equip in ip.get('equipamento'):
                    ip2 = dict()
                    ip2['id'] = ip['id']
                    ip2['block1'] = ip['block1']
                    ip2['block2'] = ip['block2']
                    ip2['block3'] = ip['block3']
                    ip2['block4'] = ip['block4']
                    ip2['block5'] = ip['block5']
                    ip2['block6'] = ip['block6']
                    ip2['block7'] = ip['block7']
                    ip2['block8'] = ip['block8']
                    ip2['descricao'] = ip['descricao']
                    ip2['equip_name'] = equip.get('nome')
                    ip2['equip_id'] = equip.get('id')
                    ips_to_screen.append(ip2)
                    
                    list_nomes.append(equip.get('nome'))
                    
                ip['equipamento'] = list_nomes
            else:
                ip2 = dict()
                ip2['id'] = ip['id']
                ip2['block1'] = ip['block1']
                ip2['block2'] = ip['block2']
                ip2['block3'] = ip['block3']
                ip2['block4'] = ip['block4']
                ip2['block5'] = ip['block5']
                ip2['block6'] = ip['block6']
                ip2['block7'] = ip['block7']
                ip2['block8'] = ip['block8']
                ip2['descricao'] = ip['descricao']
                ip2['equip_name'] = ip.get('equipamento').get('nome')
                ip2['equip_id'] = ip.get('equipamento').get('id')
                ips_to_screen.append(ip2)
                
                list_nomes = [ip.get('equipamento').get('nome')]
                ip['equipamento'] = list_nomes              
                             
        
        lists['ips'] = ips_to_screen
        lists['id'] = id_net
        lists['delete_form'] = DeleteForm()
            
        return render_to_response(NETIPV6, lists , context_instance=RequestContext(request))
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists['ips'] = None
    except TypeError,e:
        logger.error(e)
        messages.add_message(request,messages.ERROR,e)
    
    lists['id'] = id_net
    lists['delete_form'] = DeleteForm()   
    return render_to_response(NETIPV6,lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def insert_ip4(request, id_net):
    
    lists = dict()
    lists['id'] = id_net
    lists['form'] = IPForm()
    
    try:
        
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        try:
            client.create_network().get_network_ipv4(id_net)
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list') 
            
        if request.method == 'POST':
            
            form = IPForm(request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                equip_name = form.cleaned_data['equip_name']
                descricao = form.cleaned_data['descricao']
                oct1 = request.POST['oct1'] 
                oct2 = request.POST['oct2']
                oct3 = request.POST['oct3']
                oct4 = request.POST['oct4']
                ip = "%s.%s.%s.%s" % (oct1,oct2,oct3,oct4)
                
                if not (is_valid_ipv4(ip)):
                    messages.add_message(request, messages.ERROR, network_ip_messages.get("ip_error")) 
                    lists['id'] = id_net
                    lists['form'] = form
                    lists['oct1'] = oct1
                    lists['oct2'] = oct2
                    lists['oct3'] = oct3
                    lists['oct4'] = oct4
                    return render_to_response(IP4,lists, context_instance=RequestContext(request))  
                    
                else:
                    try:
                        equip = client.create_equipamento().listar_por_nome(equip_name)
                        equip = equip.get('equipamento').get('id')
                        client.create_ip().save_ipv4(ip, equip, descricao, id_net)
                        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_sucess")) 
                        return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
                        
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['id'] = id_net
                        lists['form'] = form
                        lists['oct1'] = oct1
                        lists['oct2'] = oct2
                        lists['oct3'] = oct3
                        lists['oct4'] = oct4
                    
                        return render_to_response(IP4,lists, context_instance=RequestContext(request))  
     
                
        ip = client.create_ip().get_available_ip4(id_net)
        ip = ip.get('ip')
        ip = ip.get('ip')
        ip = ip.split(".")
        lists['oct1'] = ip[0]
        lists['oct2'] = ip[1]
        lists['oct3'] = ip[2]
        lists['oct4'] = ip[3]
                
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(IP4,lists, context_instance=RequestContext(request))      

@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def insert_ip6(request, id_net):
    lists = dict()
    lists['id'] = id_net
    lists['form'] = IPForm()
    
    try:
        
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        try:
            client.create_network().get_network_ipv6(id_net)
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list') 
            
        if request.method == 'POST':
            
            form = IPForm(request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                equip_name = form.cleaned_data['equip_name']
                descricao = form.cleaned_data['descricao']
                block1 = request.POST['block1'] 
                block2 = request.POST['block2']
                block3 = request.POST['block3']
                block4 = request.POST['block4']
                block5 = request.POST['block5'] 
                block6 = request.POST['block6']
                block7 = request.POST['block7']
                block8 = request.POST['block8']
                ip6 = "%s:%s:%s:%s:%s:%s:%s:%s" % (block1,block2,block3,block4,block5,block6,block7,block8)
                
                if not (is_valid_ipv6(ip6)):
                    messages.add_message(request, messages.ERROR, network_ip_messages.get("ip_error")) 
                    lists['id'] = id_net
                    lists['form'] = form
                    lists['block1'] = block1
                    lists['block2'] = block2
                    lists['block3'] = block3
                    lists['block4'] = block4
                    lists['block5'] = block5
                    lists['block6'] = block6
                    lists['block7'] = block7
                    lists['block8'] = block8
                    return render_to_response(IP6,lists, context_instance=RequestContext(request))  
                    
                else:
                    try:
                        equip = client.create_equipamento().listar_por_nome(equip_name)
                        equip = equip.get('equipamento').get('id')
                        client.create_ip().save_ipv6(ip6, equip, descricao, id_net)
                        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_sucess")) 
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))
                        
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['id'] = id_net
                        lists['form'] = form
                        lists['block1'] = block1
                        lists['block2'] = block2
                        lists['block3'] = block3
                        lists['block4'] = block4
                        lists['block5'] = block5
                        lists['block6'] = block6
                        lists['block7'] = block7
                        lists['block8'] = block8
                    
                        return render_to_response(IP6,lists, context_instance=RequestContext(request))  
     
                
        ip = client.create_ip().get_available_ip6(id_net)
        ip = ip.get('ip6')
        ip = ip.get('ip6')
        ip = ip.split(":")
        lists['block1'] = ip[0]
        lists['block2'] = ip[1]
        lists['block3'] = ip[2]
        lists['block4'] = ip[3]
        lists['block5'] = ip[4]
        lists['block6'] = ip[5]
        lists['block7'] = ip[6]
        lists['block8'] = ip[7]
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(IP6,lists, context_instance=RequestContext(request))    


@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def edit_ip4(request,id_net,id_ip4):
    try :
        
        lists = dict()
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        form = IPEditForm()
        
        
        try:
            client.create_network().get_network_ipv4(id_net)
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list') 
        
        
        if request.method == 'POST':
            form = IPEditForm(request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                
                descricao = form.cleaned_data['descricao']
                oct1 = request.POST['oct1'] 
                oct2 = request.POST['oct2']
                oct3 = request.POST['oct3']
                oct4 = request.POST['oct4']
                equipamentos = form.cleaned_data['equip_names']
                ip = "%s.%s.%s.%s" % (oct1,oct2,oct3,oct4)
                
                if not (is_valid_ipv4(ip)):
                    messages.add_message(request, messages.ERROR, network_ip_messages.get("ip_error"))
                    lists['equipamentos'] = equipamentos
                    lists['id_net'] = id_net
                    lists['id_ip'] = id_ip4
                    lists['form'] = form
                    lists['oct1'] = oct1
                    lists['oct2'] = oct2
                    lists['oct3'] = oct3
                    lists['oct4'] = oct4
                    return render_to_response(IP4EDIT,lists, context_instance=RequestContext(request))  
                    
                else:
                    try:
                        client.create_ip().edit_ipv4(ip, descricao, id_ip4)
                        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_edit_sucess")) 
                        return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
                        
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['equipamentos'] = equipamentos
                        lists['id_net'] = id_net
                        lists['id_ip'] = id_ip4
                        lists['form'] = form
                        lists['oct1'] = oct1
                        lists['oct2'] = oct2
                        lists['oct3'] = oct3
                        lists['oct4'] = oct4
                    
                        return render_to_response(IP4EDIT,lists, context_instance=RequestContext(request)) 
            else:
                lists['equipamentos'] = request.POST['equip_names']    
                lists['id_net'] = id_net
                lists['id_ip'] = id_ip4
                lists['form'] = form
                lists['oct1'] = request.POST['oct1'] 
                lists['oct2'] = request.POST['oct2'] 
                lists['oct3'] = request.POST['oct3'] 
                lists['oct4'] = request.POST['oct4'] 
                return render_to_response(IP4EDIT,lists, context_instance=RequestContext(request)) 
        
        if request.method == 'GET':
            
            ip =  client.create_ip().find_ip4_by_id(id_ip4)
            ip = ip.get('ips')
            equipamentos = ip.get('equipamento')
            nomesEquipamentos = ''
            cont = 0
            if type(ip.get('equipamento')) == dict:
                nomesEquipamentos = equipamentos.get('nome')
            else:
                for equip in ip.get('equipamento'):
                    cont = cont + 1
                    if (cont == len(ip.get('equipamento'))):
                        nomesEquipamentos =  nomesEquipamentos + equip.get('nome')
                    else:
                        nomesEquipamentos = nomesEquipamentos + equip.get('nome') + ', '
            
            lists['equipamentos'] = nomesEquipamentos            
            lists['form'] = IPEditForm(initial={'descricao':ip.get('descricao'),'equip_names':nomesEquipamentos})
            lists['oct1'] = ip.get('oct1')
            lists['oct2'] = ip.get('oct2')
            lists['oct3'] = ip.get('oct3')
            lists['oct4'] = ip.get('oct4')
            lists['id_net'] = id_net
            lists['id_ip'] = ip.get('id')
                                  
            return render_to_response(IP4EDIT,lists, context_instance=RequestContext(request))                                              
              
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
        
@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def edit_ip6(request,id_net,id_ip6):
    try :
        
        lists = dict()
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        form = IPEditForm()
        
        
        try:
            client.create_network().get_network_ipv6(id_net)
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list') 
        
        
        if request.method == 'POST':
            form = IPEditForm(request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                
                equipamentos = form.cleaned_data['equip_names']
                descricao = form.cleaned_data['descricao']
                block1 = request.POST['block1'] 
                block2 = request.POST['block2']
                block3 = request.POST['block3']
                block4 = request.POST['block4']
                block5 = request.POST['block5'] 
                block6 = request.POST['block6']
                block7 = request.POST['block7']
                block8 = request.POST['block8']
                ip6 = "%s:%s:%s:%s:%s:%s:%s:%s" % (block1,block2,block3,block4,block5,block6,block7,block8)
                
                if not (is_valid_ipv6(ip6)):
                    messages.add_message(request, messages.ERROR, network_ip_messages.get("ip6_error")) 
                    lists['id_net'] = id_net
                    lists['id_ip6'] = id_ip6
                    lists['form'] = form
                    lists['equipamentos'] = equipamentos
                    lists['block1'] = block1
                    lists['block2'] = block2
                    lists['block3'] = block3
                    lists['block4'] = block4
                    lists['block5'] = block5
                    lists['block6'] = block6
                    lists['block7'] = block7
                    lists['block8'] = block8
                    return render_to_response(IP6EDIT,lists, context_instance=RequestContext(request))    
                    
                else:
                    try:
                        client.create_ip().edit_ipv6(ip6, descricao, id_ip6)
                        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_edit_sucess")) 
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))
                        
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['id_net'] = id_net
                        lists['id_ip6'] = id_ip6
                        lists['form'] = form
                        lists['equipamentos'] = equipamentos
                        lists['block1'] = block1
                        lists['block2'] = block2
                        lists['block3'] = block3
                        lists['block4'] = block4
                        lists['block5'] = block5
                        lists['block6'] = block6
                        lists['block7'] = block7
                        lists['block8'] = block8
                    
                        return render_to_response(IP6EDIT,lists, context_instance=RequestContext(request)) 
            else:
                
                lists['equipamentos'] = request.POST['equip_names']    
                lists['id_net'] = id_net
                lists['id_ip6'] = id_ip6
                lists['form'] = form
                ip = client.create_ip().get_available_ip6(id_net)
                ip = ip.get('ip6')
                ip = ip.get('ip6')
                ip = ip.split(":")
                lists['block1'] = ip[0]
                lists['block2'] = ip[1]
                lists['block3'] = ip[2]
                lists['block4'] = ip[3]
                lists['block5'] = ip[4]
                lists['block6'] = ip[5]
                lists['block7'] = ip[6]
                lists['block8'] = ip[7]
                return render_to_response(IP6EDIT,lists, context_instance=RequestContext(request)) 
        
        if request.method == 'GET':
            
            ip =  client.create_ip().find_ip6_by_id(id_ip6)
            ip = ip.get('ips')
            equipamentos = ip.get('equipamento')
            nomesEquipamentos = ''
            cont = 0
            if type(ip.get('equipamento')) == dict:
                nomesEquipamentos = equipamentos.get('nome')
            else:
                for equip in ip.get('equipamento'):
                    cont = cont + 1
                    if (cont == len(ip.get('equipamento'))):
                        nomesEquipamentos =  nomesEquipamentos + equip.get('nome')
                    else:
                        nomesEquipamentos = nomesEquipamentos + equip.get('nome') + ', '
            
            lists['equipamentos'] = nomesEquipamentos            
            lists['form'] = IPEditForm(initial={'descricao':ip.get('descricao'),'equip_names':nomesEquipamentos})
            lists['id_net'] = id_net
            lists['id_ip6'] = id_ip6
            lists['block1'] = ip.get('block1')
            lists['block2'] = ip.get('block2')
            lists['block3'] = ip.get('block3')
            lists['block4'] = ip.get('block4')
            lists['block5'] = ip.get('block5')
            lists['block6'] = ip.get('block6')
            lists['block7'] = ip.get('block7')
            lists['block8'] = ip.get('block8')
                                  
            return render_to_response(IP6EDIT,lists, context_instance=RequestContext(request))                                              
              
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))

@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def delete_ip4(request, id_net):
    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        if request.method == 'POST':
            
            #Verifica se a rede passada realmente existe
            try:
                client.create_network().get_network_ipv4(id_net)
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                redirect('vlan.search.list')
            
            form = DeleteForm(request.POST)
                
            if form.is_valid():
                # Get user
                ip_client = client.create_ip()
                equip_client = client.create_equipamento()
            
                # All ids to be deleted
                ids = form.cleaned_data['ids']
                if ids is None or len(ids) <= 0:
                    messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
                    return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
               
                ids_eqs = split_to_array(ids)
                ids = []
                eq_ids = []
                
                for elem in ids_eqs:
                    elem_sep = split_to_array(elem, '-')
                    ids.append(elem_sep[0])
                    eq_ids.append(elem_sep[1])
                                    
                ips = ip_client.find_ip4_by_network(id_net)
                ips = ips.get('ips')
                
                #Verifica se Ip pertence e Rede passada    
                listaIps = []
                
                for i in ips:
                    listaIps.append(i.get('id'))
                
                for id in ids:
                    if id not in listaIps:
                        messages.add_message(request, messages.ERROR, network_ip_messages.get("not_ip_in_net") % (id,id_net))
                        return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
                
                error_list = list()
                
                #remove ip equipment associations, and ip if its the last ip-equipment
                try:
                    for i in range(0, len(ids)):
                        equip_client.remover_ip(eq_ids[i], ids[i])
                
                except (VipIpError, IpEquipCantDissociateFromVip), e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    error_list.append(ids[i])
                
                except NetworkAPIClientError, e:
                    error_list.append(ids[i])
                
                if len(error_list) == len(ids):
                            messages.add_message(request, messages.ERROR, error_messages.get("can_not_remove_all"))
                            return list_netip4_by_id(request, id_net)
                
                elif len(error_list) > 0:
                            msg = ""
                            for id_error in error_list:
                                msg = msg + id_error + ", "
                                msg = error_messages.get("can_not_remove") % msg[:-2]
                                messages.add_message(request, messages.WARNING, msg)
                                return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
                
                else:
                    messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_delete_sucess")) 
                    return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
        
            else:
                messages.add_message(request, messages.ERROR, error_messages.get("select_one"))  
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
     
    return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def delete_ip6(request, id_net):
    try:
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        if request.method == 'POST':
            
            #Verifica se a rede passada realmente existe
            try:
                client.create_network().get_network_ipv6(id_net)
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
                redirect('vlan.search.list')
            
            form = DeleteForm(request.POST)
                
            if form.is_valid():
                # Get user
                ip_client = client.create_ip()
                equip_client = client.create_equipamento()
            
                # All ids to be deleted
                ids = form.cleaned_data['ids']
                if ids is None or len(ids) <= 0:
                    messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
                    return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
               
                ids_eqs = split_to_array(ids)
                ids = []
                eq_ids = []
                
                for elem in ids_eqs:
                    elem_sep = split_to_array(elem, '-')
                    ids.append(elem_sep[0])
                    eq_ids.append(elem_sep[1])
                                    
                ips = ip_client.find_ip6_by_network(id_net)
                ips = ips.get('ips')
                
                #Verifica se Ip pertence e Rede passada    
                listaIps = []
                
                for i in ips:
                    listaIps.append(i.get('id'))
                
                for id in ids:
                    if id not in listaIps:
                        messages.add_message(request, messages.ERROR, network_ip_messages.get("not_ip_in_net") % (id,id_net))
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))
                
                error_list = list()
                
                #remove ip equipment associations, and ip if its the last ip-equipment
                try:
                    for i in range(0, len(ids)):
                        equip_client.remove_ipv6(eq_ids[i], ids[i])
                
                except VipIpError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    error_list.append(ids[i])
                
                except NetworkAPIClientError, e:
                    error_list.append(ids[i])
                    
                if len(error_list) == len(ids):
                    messages.add_message(request, messages.ERROR, error_messages.get("can_not_remove_all"))
                    return list_netip6_by_id(request, id_net)
                    
                elif len(error_list) > 0:
                    msg = ""
                    for id_error in error_list:
                        msg = msg + id_error + ", "
                        msg = error_messages.get("can_not_remove") % msg[:-2]
                        messages.add_message(request, messages.WARNING, msg)
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))
                                
                else:
                    messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_delete_sucess")) 
                    return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))
        
            else:
                messages.add_message(request, messages.ERROR, error_messages.get("select_one"))  
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
     
    return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_VIP, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def edit_network4_form(request,id_net):
    
    lists = dict()
    
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    
    # Get all needs from NetworkAPI
    net_type_list = client.create_tipo_rede().listar()
    env_vip_list = client.create_environment_vip().list_all()
    try:
        network = client.create_network().get_network_ipv4(id_net)
        network =  network.get("network")
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        redirect('vlan.search.list')
    
    try:
        
        lists['id_net'] = network.get('id')
        lists['broadcast'] = network.get('broadcast')
        lists['oct1'] = network.get("oct1")
        lists['oct2'] = network.get("oct2")
        lists['oct3'] = network.get("oct3")
        lists['oct4'] = network.get("oct4")
        lists['block_net'] = network.get("block")
    
        if request.method == 'POST':
            
            form = NetworkEditForm(net_type_list, env_vip_list, request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                env_vip = form.cleaned_data['env_vip']
                net_type = form.cleaned_data['net_type']
                ip_type = 0
                
                client.create_network().edit_network(id_net, ip_type, net_type, env_vip)
                messages.add_message(request, messages.SUCCESS, network_ip_messages.get("sucess_edit")) 
                
                return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))

        #Get
        else:
                
            env_vip = network.get("ambient_vip")
            net_type = network.get("network_type")
            ip_version = 0
            vlan_id = network.get('vlan')
            vlan  = client.create_vlan().get(vlan_id)
            vlan = vlan.get("vlan")
            environment =  client.create_ambiente().buscar_por_id(vlan.get("ambiente")).get("ambiente")
            vlan_nome = "%s | %s - %s - %s" %(  vlan.get("num_vlan"), environment.get("nome_divisao"), environment.get("nome_ambiente_logico"), environment.get("nome_grupo_l3"))
            lists['form'] = NetworkEditForm(net_type_list, env_vip_list,initial={'vlan_name':vlan_nome,'net_type':net_type,'env_vip':env_vip,'ip_version':ip_version})
            
    except NetworkAPIClientError, e:
        
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(NET4_EDIT, lists, context_instance=RequestContext(request))
    
@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_VIP, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def edit_network6_form(request,id_net):
    lists = dict()
    
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    
    # Get all needs from NetworkAPI
    net_type_list = client.create_tipo_rede().listar()
    env_vip_list = client.create_environment_vip().list_all()
    
    try:
        network = client.create_network().get_network_ipv6(id_net)
        network =  network.get("network")
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        redirect('vlan.search.list')
    
    try:
        
        lists['id_net'] = network.get("id")
        lists['block1'] = network.get("block1")
        lists['block2'] = network.get("block2")
        lists['block3'] = network.get("block3")
        lists['block4'] = network.get("block4")
        lists['block5'] = network.get("block5")
        lists['block6'] = network.get("block6")
        lists['block7'] = network.get("block7")
        lists['block8'] = network.get("block8")
        lists['block_net'] = network.get("block")
    
        if request.method == 'POST':
            
            form = NetworkEditForm(net_type_list, env_vip_list, request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                env_vip = form.cleaned_data['env_vip']
                net_type = form.cleaned_data['net_type']
                ip_type = 1;
                
                client.create_network().edit_network(id_net, ip_type, net_type, env_vip)
                messages.add_message(request, messages.SUCCESS, network_ip_messages.get("sucess_edit")) 
                
                return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))
            
        #Get
        else:
            env_vip = network.get("ambient_vip")
            net_type = network.get("network_type")
            ip_version = 1
            vlan_id = network.get('vlan')
            vlan  = client.create_vlan().get(vlan_id)
            vlan = vlan.get("vlan")
            environment =  client.create_ambiente().buscar_por_id(vlan.get("ambiente")).get("ambiente")
            vlan_nome = "%s | %s - %s - %s" %(  vlan.get("num_vlan"), environment.get("nome_divisao"), environment.get("nome_ambiente_logico"), environment.get("nome_grupo_l3"))
            lists['form'] = lists['form'] = NetworkEditForm(net_type_list, env_vip_list,initial={'vlan_name':vlan_nome,'net_type':net_type,'env_vip':env_vip,'ip_version':ip_version})
                 
    except NetworkAPIClientError, e:
        
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(NET6_EDIT, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": IPS, "write": True},{"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def delete_ip4_of_equip(request,id_ip,id_equip):
    try:
        
        if id_ip is None or id_ip == "":
            messages.add_message(request, messages.SUCCESS, network_ip_messages.get("net_invalid")) 
            return redirect("equipment.search.list")
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        client.create_equipamento().remover_ip(id_equip, id_ip)
        #client.create_ip().delete_ip4(id_ip)
        
        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_equip_delete")) 
                
        return HttpResponseRedirect(reverse('equipment.edit.by.id', args=[id_equip]))
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)   
        
    return HttpResponseRedirect(reverse('equipment.edit.by.id', args=[id_equip]))

@log
@login_required
@has_perm([{"permission": IPS, "write": True},{"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def delete_ip6_of_equip(request,id_ip,id_equip):
    try:
        
        if id_ip is None or id_ip == "":
            messages.add_message(request, messages.SUCCESS, network_ip_messages.get("net_invalid")) 
            return redirect("equipment.search.list")
        
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        client.create_equipamento().remove_ipv6(id_equip, id_ip)
        #client.create_ip().delete_ip6(id_ip)
        
        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_equip_delete")) 
                
        return HttpResponseRedirect(reverse('equipment.edit.by.id', args=[id_equip]))
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)   
        
    return HttpResponseRedirect(reverse('equipment.edit.by.id', args=[id_equip]))

@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def insert_ip6_by_equip(request, id_net,id_equip):
    lists = dict()
    lists['id'] = id_net
    
    if id_net is None or id_net == "":
        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("net_invalid")) 
        return redirect("equipment.search.list")
    
    #REDIRECIONA PARA A PAGINA PARA ENTRAR NA ACTION CORRETA,USADA APENAS PARA JA INSERIR O EQUIPAMENTO
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        try:
            client.create_network().get_network_ipv6(id_net)
            equip = client.create_equipamento().listar_por_id(id_equip).get('equipamento')
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list') 
        
        lists['form'] = IPForm(initial={"equip_name":equip.get('nome')})        
        ip = client.create_ip().get_available_ip6(id_net)
        ip = ip.get('ip6')
        ip = ip.get('ip6')
        ip = ip.split(":")
        lists['block1'] = ip[0]
        lists['block2'] = ip[1]
        lists['block3'] = ip[2]
        lists['block4'] = ip[3]
        lists['block5'] = ip[4]
        lists['block6'] = ip[5]
        lists['block7'] = ip[6]
        lists['block8'] = ip[7]
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(IP6,lists, context_instance=RequestContext(request)) 


@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def insert_ip4_by_equip(request, id_net,id_equip):
    lists = dict()
    lists['id'] = id_net
    
    if id_net is None or id_net == "":
        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("net_invalid")) 
        return redirect("equipment.search.list")
    
    #REDIRECIONA PARA A PAGINA PARA ENTRAR NA ACTION CORRETA, USADA APENAS PARA JA INSERIR O EQUIPAMENTO
    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        try:
            client.create_network().get_network_ipv4(id_net)
            equip = client.create_equipamento().listar_por_id(id_equip).get('equipamento')
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list') 
        
        lists['form'] = IPForm(initial={"equip_name":equip.get('nome')})        
        ip = client.create_ip().get_available_ip4(id_net)
        ip = ip.get('ip').get('ip')
        ip = ip.split(".")
        lists['oct1'] = ip[0]
        lists['oct2'] = ip[1]
        lists['oct3'] = ip[2]
        lists['oct4'] = ip[3]
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(IP4,lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def assoc_ip4(request, id_net, id_ip4):
    try :
        
        lists = dict()
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        form = IPAssocForm()
        
        try:
            client.create_network().get_network_ipv4(id_net)
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list') 
        
        if request.method == 'POST':
            form = IPAssocForm(request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                flag_error = False
                
                oct1 = request.POST['oct1'] 
                oct2 = request.POST['oct2']
                oct3 = request.POST['oct3']
                oct4 = request.POST['oct4']
                equipamentos = form.cleaned_data['equip_names']
                new_equip = form.cleaned_data['equip_name']
                
                if new_equip in equipamentos.split(','):
                    messages.add_message(request, messages.ERROR, network_ip_messages.get("already_assoc_equip"))
                    flag_error = True
                else:
                    equip_dict = client.create_equipamento().listar_por_nome(new_equip)
                
                ip = "%s.%s.%s.%s" % (oct1,oct2,oct3,oct4)
                
                if not (is_valid_ipv4(ip)):
                    messages.add_message(request, messages.ERROR, network_ip_messages.get("ip_error"))
                    flag_error = True
                    
                if flag_error:
                    lists['equipamentos'] = equipamentos
                    lists['id_net'] = id_net
                    lists['id_ip'] = id_ip4
                    lists['form'] = form
                    lists['oct1'] = oct1
                    lists['oct2'] = oct2
                    lists['oct3'] = oct3
                    lists['oct4'] = oct4
                    return render_to_response(IP4ASSOC,lists, context_instance=RequestContext(request))  
                    
                else:
                    try:
                        client.create_ip().assoc_ipv4(id_ip4, equip_dict['equipamento']['id'], id_net)
                        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_assoc_success")) 
                        return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))
                        
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['equipamentos'] = equipamentos
                        lists['id_net'] = id_net
                        lists['id_ip'] = id_ip4
                        lists['form'] = form
                        lists['oct1'] = oct1
                        lists['oct2'] = oct2
                        lists['oct3'] = oct3
                        lists['oct4'] = oct4
                    
                        return render_to_response(IP4ASSOC,lists, context_instance=RequestContext(request)) 
            else:
                lists['equipamentos'] = request.POST['equip_names']    
                lists['id_net'] = id_net
                lists['id_ip'] = id_ip4
                lists['form'] = form
                lists['oct1'] = request.POST['oct1'] 
                lists['oct2'] = request.POST['oct2'] 
                lists['oct3'] = request.POST['oct3'] 
                lists['oct4'] = request.POST['oct4'] 
                return render_to_response(IP4ASSOC, lists, context_instance=RequestContext(request)) 
        
        if request.method == 'GET':
            
            ip =  client.create_ip().find_ip4_by_id(id_ip4)
            ip = ip.get('ips')
            equipamentos = ip.get('equipamento')
            nomesEquipamentos = ''
            cont = 0
            if type(ip.get('equipamento')) == dict:
                nomesEquipamentos = equipamentos.get('nome')
            else:
                for equip in ip.get('equipamento'):
                    cont = cont + 1
                    if (cont == len(ip.get('equipamento'))):
                        nomesEquipamentos =  nomesEquipamentos + equip.get('nome')
                    else:
                        nomesEquipamentos = nomesEquipamentos + equip.get('nome') + ','
            
            lists['equipamentos'] = nomesEquipamentos            
            lists['form'] = IPAssocForm(initial={'descricao':ip.get('descricao'),'equip_names':nomesEquipamentos})
            lists['oct1'] = ip.get('oct1')
            lists['oct2'] = ip.get('oct2')
            lists['oct3'] = ip.get('oct3')
            lists['oct4'] = ip.get('oct4')
            
            lists['form'].fields['descricao'].widget.attrs['readonly'] = True
            
            lists['id_net'] = id_net
            lists['id_ip'] = ip.get('id')
            
            return render_to_response(IP4ASSOC,lists, context_instance=RequestContext(request))                                              
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return HttpResponseRedirect(reverse('network.ip4.list.by.id', args=[id_net]))

@log
@login_required
@has_perm([{"permission": IPS, "write": True}, {"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True}])
def assoc_ip6(request, id_net, id_ip6):
    try :
        
        lists = dict()
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        form = IPAssocForm()
        
        try:
            client.create_network().get_network_ipv6(id_net)
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect('vlan.search.list') 
        
        if request.method == 'POST':
            form = IPAssocForm(request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                flag_error = False
                
                block1 = request.POST['block1']
                block2 = request.POST['block2']
                block3 = request.POST['block3']
                block4 = request.POST['block4']
                block5 = request.POST['block5']
                block6 = request.POST['block6']
                block7 = request.POST['block7']
                block8 = request.POST['block8']
                
                equipamentos = form.cleaned_data['equip_names']
                new_equip = form.cleaned_data['equip_name']
                
                if new_equip in equipamentos.split(','):
                    messages.add_message(request, messages.ERROR, network_ip_messages.get("already_assoc_equip"))
                    flag_error = True
                else:
                    equip_dict = client.create_equipamento().listar_por_nome(new_equip)
                
                ip6 = "%s:%s:%s:%s:%s:%s:%s:%s" % (block1,block2,block3,block4,block5,block6,block7,block8)
                
                if not (is_valid_ipv6(ip6)):
                    messages.add_message(request, messages.ERROR, network_ip_messages.get("ip_error"))
                    flag_error = True
                    
                if flag_error:
                    lists['equipamentos'] = equipamentos
                    lists['id_net'] = id_net
                    lists['id_ip'] = id_ip6
                    lists['form'] = form
                    lists['block1'] = block1
                    lists['block2'] = block2
                    lists['block3'] = block3
                    lists['block4'] = block4
                    lists['block5'] = block5
                    lists['block6'] = block6
                    lists['block7'] = block7
                    lists['block8'] = block8
                    return render_to_response(IP6ASSOC,lists, context_instance=RequestContext(request))  
                    
                else:
                    try:
                        client.create_ip().assoc_ipv6(id_ip6, equip_dict['equipamento']['id'], id_net)
                        messages.add_message(request, messages.SUCCESS, network_ip_messages.get("ip_assoc_success")) 
                        return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))
                        
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                        lists['equipamentos'] = equipamentos
                        lists['id_net'] = id_net
                        lists['id_ip'] = id_ip6
                        lists['form'] = form
                        lists['block1'] = block1
                        lists['block2'] = block2
                        lists['block3'] = block3
                        lists['block4'] = block4
                        lists['block5'] = block5
                        lists['block6'] = block6
                        lists['block7'] = block7
                        lists['block8'] = block8
                    
                        return render_to_response(IP6ASSOC,lists, context_instance=RequestContext(request)) 
            else:
                lists['equipamentos'] = request.POST['equip_names']    
                lists['id_net'] = id_net
                lists['id_ip'] = id_ip6
                lists['form'] = form
                lists['block1'] = request.POST['block1']
                lists['block2'] = request.POST['block2']
                lists['block3'] = request.POST['block3']
                lists['block4'] = request.POST['block4']
                lists['block5'] = request.POST['block5']
                lists['block6'] = request.POST['block6']
                lists['block7'] = request.POST['block7']
                lists['block8'] = request.POST['block8']

                return render_to_response(IP6ASSOC, lists, context_instance=RequestContext(request)) 
        
        if request.method == 'GET':
            
            ip =  client.create_ip().find_ip6_by_id(id_ip6)
            ip = ip.get('ips')
            equipamentos = ip.get('equipamento')
            nomesEquipamentos = ''
            cont = 0
            if type(ip.get('equipamento')) == dict:
                nomesEquipamentos = equipamentos.get('nome')
            else:
                for equip in ip.get('equipamento'):
                    cont = cont + 1
                    if (cont == len(ip.get('equipamento'))):
                        nomesEquipamentos =  nomesEquipamentos + equip.get('nome')
                    else:
                        nomesEquipamentos = nomesEquipamentos + equip.get('nome') + ','
            
            lists['equipamentos'] = nomesEquipamentos            
            lists['form'] = IPAssocForm(initial={'descricao':ip.get('descricao'),'equip_names':nomesEquipamentos})
            lists['block1'] = ip.get('block1')
            lists['block2'] = ip.get('block2')
            lists['block3'] = ip.get('block3')
            lists['block4'] = ip.get('block4')
            lists['block5'] = ip.get('block5')
            lists['block6'] = ip.get('block6')
            lists['block7'] = ip.get('block7')
            lists['block8'] = ip.get('block8')
            
            lists['form'].fields['descricao'].widget.attrs['readonly'] = True
            
            lists['id_net'] = id_net
            lists['id_ip'] = ip.get('id')
            
            return render_to_response(IP6ASSOC,lists, context_instance=RequestContext(request))                                              
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return HttpResponseRedirect(reverse('network.ip6.list.by.id', args=[id_net]))