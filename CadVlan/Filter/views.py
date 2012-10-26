# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.forms import DeleteForm
from CadVlan.messages import error_messages, filter_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import FILTER_LIST, FILTER_FORM, FILTER_EDIT
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError
import logging
from CadVlan.Filter.form import FilterForm

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}])
def list_all(request):

    try:
        filter_list = dict()

        # Get user
        auth = AuthSession(request.session)
        filter_client = auth.get_clientFactory().create_filter()

        # Get all filters from NetworkAPI
        filter_list = filter_client.list_all()
        
        for filter_ in filter_list['filter']:
            filter_['is_more'] = str(False)
            
            if filter_.get('equip_types') is not None:
                if type(filter_['equip_types']) is dict:
                    filter_['equip_types'] = [filter_['equip_types']]                
                
                if len(filter_['equip_types']) > 3:
                    filter_['is_more'] = str(True)
               
    
        filter_list['form'] = DeleteForm()
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(FILTER_LIST, filter_list, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True}])
def delete_all(request):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_filter = auth.get_clientFactory().create_filter()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each script selected to remove
            for id_filter in ids:
                try:
                    # Execute in NetworkAPI
                    client_filter.remove(id_filter)

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    error_list.append(id_filter)
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
                messages.add_message(request, messages.SUCCESS, filter_messages.get("success_remove"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('filter.list')

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True}])
def add_form(request):

    try:
        
        lists = dict()
        lists['action'] = reverse("filter.form")
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        equip_type = client.create_tipo_equipamento().listar()

        if request.method == "POST":

            form = FilterForm(equip_type, request.POST)
            lists['form'] = form

            if form.is_valid():
                
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                equip_type = form.cleaned_data['equip_type']

                
                filter_client = client.create_filter()
                filter_ =  filter_client.add(name, description)
                    
                for et in equip_type:
                    filter_client.associate(et, filter_['filter']['id'])
                    
                messages.add_message(request, messages.SUCCESS, filter_messages.get("success_insert"))

                return redirect('filter.list')                  

        else:

            lists['form'] = FilterForm(equip_type)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(FILTER_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True}])
def edit_form(request, id_filter):

    try:
        
        lists = dict()
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        lists['id_filter'] = id_filter
        
        equip_type = client.create_tipo_equipamento().listar()
        
        filter_ = client.create_filter().get(id_filter)
        filter_ = filter_.get("filter")
        
        if type(filter_.get('equip_types')) is dict:
                filter_['equip_types'] = [filter_['equip_types']]
            

        if request.method == "POST":

            form = FilterForm(equip_type, request.POST)
            lists['form'] = form

            if form.is_valid():
                
                name  = form.cleaned_data['name']
                description = form.cleaned_data['description']
                new_equip_type = form.cleaned_data['equip_type']

                filter_client = client.create_filter()
                filter_client.alter(id_filter, name, description)
                
                old_equip_type = list()
                if filter_.get('equip_types') is not None:
                    for eqt in filter_.get('equip_types'):
                        old_equip_type.append(eqt['id'])
                
                #Make diff from old_equip_type and new_equip_type
                to_add, to_rem = diff(old_equip_type, new_equip_type)
                
                for eqt_id in to_rem:
                    filter_client.dissociate(id_filter, eqt_id)
                
                for eqt_id in to_add:
                    filter_client.associate(eqt_id, id_filter)
                    
                messages.add_message(request, messages.SUCCESS, filter_messages.get("success_edit"))

                return redirect('filter.list')                  
        #GET
        else: 
            #Set form data for filter
            equip_types = list()
            if filter_.get('equip_types') is not None:
                for et in filter_.get('equip_types'):
                    equip_types.append(et['id'])
                    
            
            lists['form'] = FilterForm(equip_type,initial={"id":filter_['id'],
                                                           "name":filter_['name'],
                                                           "description":filter_['description'],
                                                           "equip_type": equip_types})
    
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(FILTER_EDIT, lists, context_instance=RequestContext(request))

def diff(old, new):    
    to_add = list(set(new) - set(old))
    to_rem = list(set(old) - set(new))
    
    return to_add, to_rem