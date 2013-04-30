# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Acl.acl import alterAclCvs, deleteAclCvs, getAclCvs, createAclCvs, scriptAclCvs, script_template, applyAcl
from CadVlan.Acl.forms import AclForm
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.Enum import NETWORK_TYPES
from CadVlan.Util.converters.util import split_to_array, replace_id_to_name
from CadVlan.Util.cvs import CVSError
from CadVlan.Util.utility import validates_dict, clone, acl_key
from CadVlan.forms import DeleteForm
from CadVlan.messages import acl_messages, error_messages
from CadVlan.permissions import VLAN_MANAGEMENT, ENVIRONMENT_MANAGEMENT
from CadVlan.templates import ACL_FORM, ACL_APPLY_LIST, ACL_APPLY_RESULT
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError
import logging

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def create(request, id_vlan, network):
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        vlan = client.create_vlan().get(id_vlan).get("vlan")
        environment =  client.create_ambiente().buscar_por_id(vlan.get("ambiente")).get("ambiente")
        
        key_acl =  acl_key(network)
        
        createAclCvs(vlan.get(key_acl), environment, network, AuthSession(request.session).get_user())
        
        messages.add_message(request, messages.SUCCESS, acl_messages.get("success_create"))
        
    except (NetworkAPIClientError, CVSError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])           
def remove(request, id_vlan, network):
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        vlan = client.create_vlan().get(id_vlan).get("vlan")
        environment =  client.create_ambiente().buscar_por_id(vlan.get("ambiente")).get("ambiente")
        
        key_acl =  acl_key(network)
        
        if vlan.get(key_acl) is None:
            messages.add_message(request, messages.ERROR, acl_messages.get("error_acl_not_exist"))
            return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))
        
        if network == NETWORK_TYPES.v4:
            client.create_vlan().invalidate(id_vlan)
        
        else:
            client.create_vlan().invalidate_ipv6(id_vlan)
        
        deleteAclCvs(vlan.get(key_acl), environment, network, AuthSession(request.session).get_user())
        
        messages.add_message(request, messages.SUCCESS, acl_messages.get("success_remove"))
        
    except (NetworkAPIClientError, CVSError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))
    
@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def script(request, id_vlan, network):
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        vlan = client.create_vlan().get(id_vlan).get("vlan")
        environment =  client.create_ambiente().buscar_por_id(vlan.get("ambiente")).get("ambiente")
        
        key_acl =  acl_key(network)
        
        if vlan.get(key_acl) is None:
            messages.add_message(request, messages.ERROR, acl_messages.get("error_acl_not_exist"))
            return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))
        
        scriptAclCvs(vlan.get(key_acl), vlan, environment, network, AuthSession(request.session).get_user())
        
    except (NetworkAPIClientError, CVSError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return HttpResponseRedirect(reverse('acl.edit', args=[id_vlan, network]))

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def edit(request, id_vlan, network):
    
    lists = dict()
    lists['id_vlan'] = id_vlan
    
    #Type Network
    lists['network'] = network
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        vlan = client.create_vlan().get(id_vlan).get("vlan")
        environment =  client.create_ambiente().buscar_por_id(vlan.get("ambiente")).get("ambiente")
        
        key_acl =  acl_key(network)
        
        if vlan.get(key_acl) is None:
            messages.add_message(request, messages.ERROR, acl_messages.get("error_acl_not_exist"))
            return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))
        
        lists['vlan'] = vlan
        vlan['ambiente'] = "%s - %s - %s" %( environment.get("nome_divisao"), environment.get("nome_ambiente_logico"), environment.get("nome_grupo_l3"))
        
        if request.method == "POST":
            
            form = AclForm(request.POST)
            lists['form'] = form
            
            if form.is_valid():
                
                acl = form.cleaned_data['acl']
                comments = form.cleaned_data['comments']
                apply_acl = form.cleaned_data['apply_acl']
                
                alterAclCvs(vlan.get(key_acl), acl, environment, comments, network, AuthSession(request.session).get_user())
                
                lists['form'] = AclForm(initial={'acl': form.cleaned_data['acl'], 'comments': ''})
                
                messages.add_message(request, messages.SUCCESS, acl_messages.get("success_edit"))
                
                #If click apply ACL
                if apply_acl == True :
                    return HttpResponseRedirect(reverse('acl.apply', args=[id_vlan, network]))
                
        else:
            
        
            content = getAclCvs(vlan.get(key_acl), environment, network, AuthSession(request.session).get_user())
            lists['form'] = AclForm(initial={'acl':content, 'comments': ''})
            
            if content is None or content == "":
                lists['script'] = script_template(environment.get("nome_ambiente_logico"), environment.get("nome_divisao"), environment.get("nome_grupo_l3"))
                
        list_ips = []
        if len(vlan["redeipv4"]) > 0 and network == NETWORK_TYPES.v4:

            for net in vlan["redeipv4"]:
                n = {}
                n["ip"] = "%s.%s.%s.%s" % (net["oct1"], net["oct2"], net["oct3"], net["oct4"])
                n["mask"] = "%s.%s.%s.%s" % (net["mask_oct1"], net["mask_oct2"], net["mask_oct3"], net["mask_oct4"])
                n["network_type"] = net["network_type"]
                list_ips.append(n)
                
        elif len(vlan["redeipv6"]) > 0 and network == NETWORK_TYPES.v6:

            for net in vlan["redeipv6"]:
                n = {}
                n["ip"] = "%s:%s:%s:%s:%s:%s:%s:%s" % (net["block1"], net["block2"], net["block3"], net["block4"], net["block5"], net["block6"], net["block7"], net["block8"])
                n["mask"] = "%s:%s:%s:%s:%s:%s:%s:%s" % (net["mask1"], net["mask2"], net["mask3"], net["mask4"], net["mask5"], net["mask6"], net["mask7"], net["mask8"])
                n["network_type"] = net["network_type"]
                list_ips.append(n)
        
        # Replace id network_type for name network_type
        vlan['network'] = replace_id_to_name(list_ips, client.create_tipo_rede().listar().get('net_type'), "network_type", "id", "name")
        
    except (NetworkAPIClientError, CVSError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(ACL_FORM,lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def apply_acl(request,id_vlan, network):
    
    lists = dict()
    lists['id_vlan'] = id_vlan
    lists['form'] = DeleteForm()
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        vlan = client.create_vlan().get(id_vlan).get("vlan")
        environment =  client.create_ambiente().buscar_por_id(vlan.get("ambiente")).get("ambiente")
        
        key_acl =  acl_key(network)
        
        if vlan.get(key_acl) is None:
            messages.add_message(request, messages.ERROR, acl_messages.get("error_acl_not_exist"))
            return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))
        
        lists['vlan'] = vlan
        lists['environment'] = "%s - %s - %s" %( environment.get("nome_divisao"), environment.get("nome_ambiente_logico"), environment.get("nome_grupo_l3"))
        
        #Type Network
        lists['network'] = network
        
        if request.method == "POST":
            
            form = DeleteForm(request.POST)
                
            if form.is_valid():
                
                client_equip = client.create_equipamento()
            
                # All ids to be apply
                ids = split_to_array(form.cleaned_data['ids'])
                
                equipments = []
                
                for _id in ids:
                    
                    try:
                    
                        equip = client_equip.listar_por_id(_id)
                        
                        equipments.append(equip)
                        
                    except NetworkAPIClientError, e:
                        logger.error(e)
                        messages.add_message(request, messages.ERROR, e)
                   
                if equipments is not None and equipments != "":
                
                    #is_apply, result = applyAcl(equipments, vlan, environment, network, AuthSession(request.session).get_user())
                    apply_result = client.create_vlan().apply_acl(equipments, vlan, environment, network) 
                    
                    is_apply = apply_result.get('is_apply')
                    result   = apply_result.get('result')
                    if is_apply == '0':
                        
                        lists['result'] = result
                        
                        messages.add_message(request, messages.SUCCESS, acl_messages.get("success_apply"))
                        
                        return render_to_response(ACL_APPLY_RESULT,lists, context_instance=RequestContext(request))

                    else:
                        messages.add_message(request, messages.ERROR, acl_messages.get("error_apply"))
            else:
                messages.add_message(request, messages.ERROR, error_messages.get("select_one")) 
        
        
        list_equipments = []
        if len(vlan["redeipv4"]) > 0 and network == NETWORK_TYPES.v4:

            for net in vlan["redeipv4"]:
                
                try:
             
                    ips = client.create_ip().find_ip4_by_network(net["id"]).get('ips')
                
                    for ip in ips:
                        equipment = {}
                        equipment["description"] = ip["descricao"]
                        equipment["ip"] = "%s.%s.%s.%s" % (ip["oct1"], ip["oct2"], ip["oct3"], ip["oct4"])
                        equips = validates_dict(ip,"equipamento")
                        
                        for equip in equips:
                            equipment_base = clone(equipment)
                            equipment_base["id"] = equip["id"]
                            equipment_base["name"] = equip["nome"]
                            list_equipments.append(equipment_base)

                except (NetworkAPIClientError, Exception), e:
                    pass
                
        elif len(vlan["redeipv6"]) > 0 and network == NETWORK_TYPES.v6:

            for net in vlan["redeipv6"]:
                
                try:
             
                    ips = client.create_ip().find_ip6_by_network(net["id"]).get('ips')
                
                    for ip in ips:
                        equipment = {}
                        equipment["description"] = ip["descricao"]
                        equipment["ip"] = "%s:%s:%s:%s:%s:%s:%s:%s" % (ip["block1"], ip["block2"], ip["block3"], ip["block4"], ip["block5"], ip["block6"], ip["block7"], ip["block8"])
                        equips = validates_dict(ip,"equipamento")
                        
                        for equip in equips:
                            equipment_base = clone(equipment)
                            equipment_base["id"] = ip["id"]
                            equipment_base["name"] = equip["nome"]
                            list_equipments.append(equipment_base)
                        
                except (NetworkAPIClientError), e:
                    pass
                    
        lists["equipments"] = list_equipments
        
    except (NetworkAPIClientError, CVSError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(ACL_APPLY_LIST,lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])           
def validate(request, id_vlan, network):
    try:
        
        auth = AuthSession(request.session)
        client_vlan = auth.get_clientFactory().create_vlan()
        
        client_vlan.get(id_vlan)
        
        if network == NETWORK_TYPES.v4:
            client_vlan.validar(id_vlan)
        
        else:
            client_vlan.validate_ipv6(id_vlan)
        
        messages.add_message(request, messages.SUCCESS, acl_messages.get("success_validate") % network)
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))
