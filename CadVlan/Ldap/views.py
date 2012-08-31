# -*- coding:utf-8 -*-
"""
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
"""
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Ldap.form import GroupForm
from CadVlan.Ldap.model import Ldap, LDAPError, LDAPMethodError, LDAPNotFoundError
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.utility import validates_dict
from CadVlan.forms import DeleteForm
from CadVlan.messages import error_messages, ldap_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import LDAP_GROUP_LIST, LDAP_GROUP_FORM
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
import logging

logger = logging.getLogger(__name__)


def get_users(ldap):
    """
    Returns all users from LDAP in parse form list
    """ 
    try:
    
        users = ldap.get_users()
        users_list = []        
        for group in users:
            user_aux = {}
            user_aux['uidNumber'] = users.get(group).get('uidNumber')
            user_aux['cn'] = users.get(group).get('cn')
            users_list.append(user_aux)
            
        return users_list
            
    except LDAPError, e:
        raise e
    except Exception, e:
        raise LDAPMethodError(e)
    
def get_groups(ldap):
    """
    Returns all groups from LDAP in parse form list
    """ 
    try:
    
        groups = ldap.get_groups()
        groups_list = []        
        for group in groups:
            group_aux = {}
            group_aux['gidNumber'] = groups.get(group).get('gidNumber')
            group_aux['cn'] = groups.get(group).get('cn')
            groups_list.append(group_aux)
            
        return groups_list
            
    except LDAPError, e:
        raise e
    except Exception, e:
        raise LDAPMethodError(e)
    
def gidNumber_suggest(ldap):
    """
    Suggested gidNumber
    """ 
    try:
        suggest = ''
        groups = ldap.get_groups()
        for i in ldap.rangeGroups:
            
            if not i in groups:
                suggest = i
                break
        
        return suggest
    
    except LDAPError, e:
        raise e
    except Exception, e:
        raise LDAPMethodError(e)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def list_all_group(request):
    try:
        
        lists = dict()
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        
        lists['groups'] = get_groups(ldap)
        lists['form'] = DeleteForm()
        
    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(LDAP_GROUP_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def delete_group_all(request):

    if request.method == 'POST':

        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        form = DeleteForm(request.POST)

        if form.is_valid():

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each group selected to remove
            for gid in ids:

                try:

                    ldap.rem_group(gid)
                    
                except LDAPMethodError, e:
                    error_list.append(gid)
                    have_errors = True

                except LDAPError, e:
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
                messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_remove_group"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    return redirect('ldap.group.list')


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def add_group_form(request):

    try:
        
        lists = dict()
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        
        users_list = get_users(ldap)

        if request.method == "POST":

            form = GroupForm(users_list, request.POST)

            if form.is_valid():
                cn = str(form.cleaned_data['cn'])
                gidNumber = str(form.cleaned_data['gidNumber'])
                member_uid = form.cleaned_data['member_uid']
                
                try:
                    #Valid cn
                    group = None
                    group = ldap.get_group(cn)
                except LDAPError, e:
                    pass
                
                if group is None:

                    #Valid gidNumber
                    is_gidNumber_valid = True
                    for grp in get_groups(ldap):

                        if str(gidNumber) == grp.get("gidNumber"):
                            is_gidNumber_valid = False
                            break

                    if not is_gidNumber_valid:
                        messages.add_message(request, messages.WARNING, ldap_messages.get("error_duplicated_gidNumber_group") % gidNumber)

                    else:
                        ldap.add_group(cn, gidNumber, member_uid)

                        messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_insert_group"))
                        return redirect('ldap.group.list')
                else:
                    messages.add_message(request, messages.WARNING, ldap_messages.get("error_duplicated_name_group") % cn)

        else:
            
            form = GroupForm(users_list, initial = {'gidNumber': gidNumber_suggest(ldap) })
                                                      

    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists["form"] = form
    lists["action"] = reverse("ldap.group.form")

    return render_to_response(LDAP_GROUP_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def edit_group_form(request, cn):
    try:
        
        lists = dict()
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        action = reverse("ldap.group.form")
        
        users_list = get_users(ldap)
            
        form = GroupForm(users_list) 
            
        if request.method == "POST":
            
            form = GroupForm(users_list, request.POST)

            if form.is_valid():
                cn = str(form.cleaned_data['cn'])
                gidNumber = str(form.cleaned_data['gidNumber'])
                member_uid = form.cleaned_data['member_uid']
                
                ldap.edit_group(cn, gidNumber, member_uid)
                
                messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_edit_group"))
                return redirect('ldap.group.list')
        
        else:
            group = ldap.get_group(cn)
            form = GroupForm(users_list, initial = {'cn': group.get("cn"), 'gidNumber': group.get("gidNumber"), 'member_uid': validates_dict(group,("memberUid")) })
        
        action = reverse("ldap.group.edit", args=[cn])
        lists["edit"] = True
    
    except LDAPNotFoundError, e:
        messages.add_message(request, messages.ERROR, ldap_messages.get("invalid_group") % cn)
        
    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    lists["form"] = form
    lists["action"] = action

    return render_to_response(LDAP_GROUP_FORM, lists, context_instance=RequestContext(request))