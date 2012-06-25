# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import OPTIONVIP_LIST, OPTIONVIP_FORM, NETIPV4, NETIPV6
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.forms import DeleteForm
from CadVlan.Util.converters.util import split_to_array, replace_id_to_name
from CadVlan.messages import error_messages, option_vip_messages
from CadVlan.OptionVip.forms import OptionVipForm, OptionVipNetForm
from CadVlan.permissions import OPTION_VIP, EQUIPMENT_MANAGEMENT,\
    VLAN_MANAGEMENT, NETWORK_TYPE_MANAGEMENT
from django.core.urlresolvers import reverse

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": OPTION_VIP, "read": True}])
def list_all(request):

    try:

        option_vip_list = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all option vips from NetworkAPI
        option_vip_list = client.create_option_vip().get_all()
        option_vip_list['form'] = DeleteForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(OPTIONVIP_LIST, option_vip_list, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": OPTION_VIP, "write": True}])
def delete_all(request):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_ovip = auth.get_clientFactory().create_option_vip()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each script selected to remove
            for id_option_vip in ids:
                try:

                    # Execute in NetworkAPI
                    client_ovip.remove(id_option_vip);

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(request, messages.ERROR, error_messages.get("can_not_remove_all"))

            # If cant remove someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = error_messages.get("can_not_remove") % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all has ben removed
            elif have_errors == False:
                messages.add_message(request, messages.SUCCESS, option_vip_messages.get("success_remove"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('option-vip.list')

@log
@login_required
@has_perm([{"permission": OPTION_VIP, "write": True}])
def add_form(request):

    try:

        if request.method == "POST":

            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            form = OptionVipForm(request.POST)

            if form.is_valid():
                name_option = form.cleaned_data['name_option']
                type_option = form.cleaned_data['type_option']

                try:
                    client.create_option_vip().add(type_option, name_option);
                    messages.add_message(request, messages.SUCCESS, option_vip_messages.get("success_insert"))

                    return redirect('option-vip.list')

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)                    

        else:

            form = OptionVipForm()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    action = reverse("option-vip.form")

    return render_to_response(OPTIONVIP_FORM, {'form': form, 'action': action }, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": OPTION_VIP, "write": True}])
def edit_form(request, id_optionvip):

    try:
        lists = dict()
        lists['form'] = OptionVipForm()

        if request.method == 'POST':

            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            id_ovip = int (id_optionvip)

            form = OptionVipForm(request.POST) 

            lists['form'] = form
            lists['action'] = reverse("option-vip.edit", args=[id_ovip])

            if form.is_valid():
                id_option = form.cleaned_data['id_option']
                name_option = form.cleaned_data['name_option']
                type_option = form.cleaned_data['type_option']

                try:
                    client.create_option_vip().alter(id_option, type_option, name_option)
                    messages.add_message(request, messages.SUCCESS, option_vip_messages.get("success_edit"))
                    return redirect('option-vip.list')

                except NetworkAPIClientError, e:
                    messages.add_message(request, messages.ERROR, e)

            return render_to_response(OPTIONVIP_FORM, lists, context_instance=RequestContext(request))

        id_ovip = int(id_optionvip) 

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        option_vip = client.create_option_vip().search(id_ovip)

        if option_vip is None:
            messages.add_message(request, messages.ERROR, option_vip_messages.get("invalid_option_vip"))
            return redirect('option-vip.list') 

        option_vip = option_vip.get('opcoesvip')

        # Set Option VIP data
        initial = {'id_option':  option_vip.get('id'), 'name_option':  option_vip.get('nome_opcao_txt'), 'type_option':  option_vip.get('tipo_opcao')}
        form = OptionVipForm(initial=initial)

        lists['form'] = form
        lists['action'] = reverse("option-vip.edit", args=[id_ovip])

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except KeyError, e:
        logger.error(e)

    return render_to_response(OPTIONVIP_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": OPTION_VIP, "write": True}])
def option_vip_associate_net4(request,id_net):
    '''
    
    Método para associar opções Vips ao Ambiente Vip de determinada Rede
    Método pŕaticamente igual ao método listar net por Id, devido a necessidade de se carregar corretamente as Redes, tanto pelo metodo de listagem 
    de redes por ID, como por esse, pois ficam na mesma pagina e nao é utilizado AJAX, logo tudo deve ser recarregado.
    Diferenças: POST, onde é feita a associação
    
    '''
    lists = dict()
    
    try:
        
        lists['aba'] = 1
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
            
            
        #recuperando lista de vlans
        net = client.create_network().get_network_ipv4(id_net)
            
        vlan = client.create_vlan().get(net.get('network').get('vlan'))
            
        net['network']['vlan'] = vlan.get('vlan').get('nome')
            
        tipo_rede = client.create_tipo_rede().listar()
        
        id_vip =  net.get('network').get("ambient_vip")
                           
        lists['net'] = replace_id_to_name([net['network']], tipo_rede['tipo_rede'], "network_type", "id", "nome")
        
        if id_vip is None:
            id_vip = 0
            
        else:  
        
            enviroment_vip = client.create_environment_vip().search(id_vip)
        
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
        lists['id'] = id_net
        lists['delete_form'] = DeleteForm()
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists['ips'] = None
    except TypeError,e:
        logger.error(e)
        messages.add_message(request,messages.ERROR,e)
        
    lists['id'] = id_net
    lists['delete_form'] = DeleteForm()
    
    try:
        
        if id_vip == 0:
            lists['id_vip'] = id_vip
            return render_to_response(NETIPV4,lists, context_instance=RequestContext(request))
        
        opts = client.create_option_vip().get_all()
        
        opts_choisen = client.create_option_vip().get_option_vip(id_vip)
        
        if opts_choisen is not None:
                opts_choisen = opts_choisen.get('optionvip')
                
        if type(opts_choisen) == dict:
            opts_choisen = [opts_choisen]
            
        if opts_choisen is None:
            opts_choisen = []
        
        post = False
        
        if request.method == 'POST':
            
            form = OptionVipNetForm(opts, request.POST)
            
            if form.is_valid():
                
                lista_opcoes = form.cleaned_data['option_vip']
                
                for id_opc_vip in opts_choisen:
                    client.create_option_vip().disassociate(id_opc_vip.get('id'), id_vip)
                
                for id_opc_vip in lista_opcoes:
                    client.create_option_vip().associate(id_opc_vip,id_vip)
                    
                
               
                messages.add_message(request, messages.SUCCESS, option_vip_messages.get("sucess_options"))
            else:
                post = True
                lists['opt_form'] = form
            
            
        
        key = u"environmentvip_%s" % (str(id_vip,))
        enviroment_vip = enviroment_vip.get(key)
        lists['vip'] = enviroment_vip
        opts = client.create_option_vip().get_all()
        options_vip = client.create_option_vip().get_option_vip(id_vip)
        choice_opts = []
        if options_vip is not None:
            options_vip = options_vip.get('optionvip')
                
                
            if type (options_vip) == dict:
                options_vip = [options_vip]
                    
            for opt in options_vip:
                choice_opts.append(opt.get("id"))
        
        if not post:          
            lists['opt_form'] = OptionVipNetForm(opts, initial = {'option_vip':choice_opts})
            
        lists['id_vip'] = id_vip
            
        return render_to_response(NETIPV4,lists, context_instance=RequestContext(request))
            
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    
    return render_to_response(NETIPV4,lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": VLAN_MANAGEMENT, "read": True}, {"permission": NETWORK_TYPE_MANAGEMENT, "read": True},{"permission": OPTION_VIP, "write": True}])
def option_vip_associate_net6(request,id_net):
    '''
    
    Método para associar opções Vips ao Ambiente Vip de determinada Rede
    Método pŕaticamente igual ao método listar net por Id, devido a necessidade de se carregar corretamente as Redes, tanto pelo metodo de listagem 
    de redes por ID, como por esse, pois ficam na mesma pagina e nao é utilizado AJAX, logo tudo deve ser recarregado.
    Diferenças: POST, onde é feita a associação
    
    '''
    lists = dict()
    
    try:
        
        lists['aba'] = 1
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
            
            
        #recuperando lista de vlans
        net = client.create_network().get_network_ipv6(id_net)
            
        vlan = client.create_vlan().get(net.get('network').get('vlan'))
            
        net['network']['vlan'] = vlan.get('vlan').get('nome')
            
        tipo_rede = client.create_tipo_rede().listar()
        
        id_vip =  net.get('network').get("ambient_vip")
                           
        lists['net'] = replace_id_to_name([net['network']], tipo_rede['tipo_rede'], "network_type", "id", "nome")
        
        if id_vip is None:
            id_vip = 0
            
        else:  
        
            enviroment_vip = client.create_environment_vip().search(id_vip)
        
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
                             
        
        lists['ips'] = ips
        lists['id'] = id_net
        lists['delete_form'] = DeleteForm()
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        lists['ips'] = None
    except TypeError,e:
        logger.error(e)
        messages.add_message(request,messages.ERROR,e)
        
    lists['id'] = id_net
    lists['delete_form'] = DeleteForm()
    
    try:
        
        if id_vip == 0:
            lists['id_vip'] = id_vip
            return render_to_response(NETIPV6,lists, context_instance=RequestContext(request))
        
        opts = client.create_option_vip().get_all()
        
        opts_choisen = client.create_option_vip().get_option_vip(id_vip)
        
        if opts_choisen is not None:
                opts_choisen = opts_choisen.get('optionvip')
                
        if type(opts_choisen) == dict:
            opts_choisen = [opts_choisen]
            
        if opts_choisen is None:
            opts_choisen = []
            
        if int(id_vip) != int(id_vip):
            
            messages.add_message(request, messages.ERROR, option_vip_messages.get("vip_not_in_net") % (id_vip,id_net))
            lists['opt_form'] = False
            return render_to_response(NETIPV6,lists, context_instance=RequestContext(request))
        
        post = False
        
        if request.method == 'POST':
            
            form = OptionVipNetForm(opts, request.POST)
            
            if form.is_valid():
                
                lista_opcoes = form.cleaned_data['option_vip']
                
                for id_opc_vip in opts_choisen:
                    client.create_option_vip().disassociate(id_opc_vip.get('id'), id_vip)
                
                for id_opc_vip in lista_opcoes:
                    client.create_option_vip().associate(id_opc_vip,id_vip)
                    
                
               
                messages.add_message(request, messages.SUCCESS, option_vip_messages.get("sucess_options"))
            else:
                post = True
                lists['opt_form'] = form
            
            
        
        key = u"environmentvip_%s" % (str(id_vip,))
        enviroment_vip = enviroment_vip.get(key)
        lists['vip'] = enviroment_vip
        opts = client.create_option_vip().get_all()
        options_vip = client.create_option_vip().get_option_vip(id_vip)
        choice_opts = []
        if options_vip is not None:
            options_vip = options_vip.get('optionvip')
                
                
            if type (options_vip) == dict:
                options_vip = [options_vip]
                    
            for opt in options_vip:
                choice_opts.append(opt.get("id"))
        
        if not post:          
            lists['opt_form'] = OptionVipNetForm(opts, initial = {'option_vip':choice_opts})
            
        lists['id_vip'] = id_vip
            
        return render_to_response(NETIPV6,lists, context_instance=RequestContext(request))
            
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    
    return render_to_response(NETIPV6,lists, context_instance=RequestContext(request))
    