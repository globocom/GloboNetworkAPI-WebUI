# -*- coding:utf-8 -*-
"""
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
"""
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Ldap.form import GroupForm, SudoerForm, UserSearchForm, UserForm, CHOICES_GROUP
from CadVlan.Ldap.model import Ldap, LDAPError, LDAPMethodError, LDAPNotFoundError
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.utility import validates_dict
from CadVlan.forms import DeleteForm
from CadVlan.messages import error_messages, ldap_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import LDAP_GROUP_LIST, LDAP_GROUP_FORM, LDAP_SUDOER_LIST, LDAP_SUDOER_FORM, LDAP_USER_LIST, LDAP_USER_FORM, AJAX_LDAP_RESET_PASSWORD
from CadVlan.settings import  LDAP_PWD_DEFAULT
from django.contrib import messages
from django.template import loader
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
import logging

logger = logging.getLogger(__name__)

class PATTERN_TYPES():
    INTERNAL  = "interno"
    EXTERNAL  = "externo"

def get_users(ldap):
    """
    Returns all users from LDAP in parse form list
    
    @param ldap: Ldap
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
    
def get_users_search(ldap, pattern, lock=False, policy=False):
    """
    Returns all users from LDAP in parse form list
    
    @param ldap: Ldap
    @param pattern: Type of User to be searched (PATTERN_TYPES)
    @param lock: True or False, determines whether data will be fetched lock
    @param policy: True or False, determines whether data will be fetched policies
    """ 
    try:
    
        users = ldap.get_users(lock, policy)
        users_list = []        
        for group in users:
            
            is_valid = False
            if pattern == PATTERN_TYPES.EXTERNAL:
                is_valid= ldap.valid_range_user_external(users.get(group).get('uidNumber'))
            else:
                is_valid= ldap.valid_range_user_internal(users.get(group).get('uidNumber'))
            
            if is_valid:
                user_aux = {}
                user_aux['uidNumber'] =  users.get(group).get('uidNumber')
                user_aux['cn'] = users.get(group).get('cn')
                user_aux['name'] = "%s %s" % ( users.get(group).get('givenName'), users.get(group).get('sn')) 
                if lock and users.get(group).get('pwdAccountLockedTime') is not None:
                    user_aux['pwdAccountLockedTime'] = users.get(group).get('pwdAccountLockedTime')
                
                users_list.append(user_aux)
            
        return users_list
            
    except LDAPError, e:
        raise e
    except Exception, e:
        raise LDAPMethodError(e)
    
def get_groups(ldap, cn = None):
    """
    Returns all groups from LDAP in parse form list
    
    @param ldap: Ldap
    @param cn: cn of Group.
    """ 
    try:
    
    
        if cn is None:
            groups = ldap.get_groups()
        else:
            groups = ldap.get_groups_user(cn)
            
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
    
def get_policies(ldap):
    """
    Returns all policies from LDAP in parse form list
    
    @param ldap: Ldap
    """ 
    try:
    
        policies = ldap.get_policies()
        policies_list = []        
        for policy in policies:
            policy_aux = {}
            policy_aux['cn'] = policies.get(policy).get('cn')
            policies_list.append(policy_aux)
            
        return policies_list
            
    except LDAPError, e:
        raise e
    except Exception, e:
        raise LDAPMethodError(e)
    
    
def get_sudoers(ldap):
    """
    Returns all sudoers from LDAP in parse form list
    
    @param ldap: Ldap
    """ 
    try:
    
        sudoers = ldap.get_sudoers()
        sudoers_list = []        
        for sudoer in sudoers:
            sudoer_aux = {}
            sudoer_aux['sudoCommand'] = sudoers.get(sudoer).get('sudoCommand')
            sudoer_aux['cn'] = sudoers.get(sudoer).get('cn')
            sudoer_aux['is_more'] = False
            
            if len(sudoer_aux['sudoCommand']) > 3:
                sudoer_aux['is_more'] = True
            
            sudoers_list.append(sudoer_aux)
            
        return sudoers_list
            
    except LDAPError, e:
        raise e
    except Exception, e:
        raise LDAPMethodError(e)
    
def gidNumber_suggest(ldap):
    """
    Suggested gidNumber
    
    @param ldap: Ldap
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
    
def uidNumber_suggest(ldap, pattern):
    """
    Suggested uidNumber
    
    @param ldap: Ldap
    @param pattern: Type of User to be searched (PATTERN_TYPES)
    """ 
    try:
        suggest = ''
        users = ldap.get_users()
        
        if pattern == PATTERN_TYPES.INTERNAL:
            rangeUsers = ldap.rangeUsers
        else:
            rangeUsers = ldap.rangeUsersExternal
        
        for i in rangeUsers:
            
            if not i in users:
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
                    
                except LDAPNotFoundError, e:
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

                if valid_form_group(ldap, request, cn, gidNumber):
                    
                    ldap.add_group(cn, gidNumber, member_uid)

                    messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_insert_group"))

                    return redirect('ldap.group.list')

        else:
            
            form = GroupForm(users_list, initial = {'gidNumber': gidNumber_suggest(ldap) })
                                                      

    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists["form"] = form
    lists["action"] = reverse("ldap.group.form")

    return render_to_response(LDAP_GROUP_FORM, lists, context_instance=RequestContext(request))

def valid_form_group(ldap, request, cn, gidNumber):
    
    #Valid
    is_valid = True
    
    try:
        ldap.get_group(cn)
        is_valid = False
        messages.add_message(request, messages.WARNING, ldap_messages.get("error_duplicated_name_group") % cn)
    except LDAPError:
        pass

    for grp in get_groups(ldap):
        
        if gidNumber == grp.get("gidNumber"):
            is_valid = False
            messages.add_message(request, messages.WARNING, ldap_messages.get("error_duplicated_gidNumber_group") % gidNumber)
        
    return is_valid


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def edit_group_form(request, cn):
    try:
        
        lists = dict()
        lists["edit"] = True
        lists["action"] = reverse("ldap.group.edit", args=[cn])
        
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        
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
        
    except LDAPNotFoundError, e:
        messages.add_message(request, messages.ERROR, ldap_messages.get("invalid_group") % cn)
        return redirect('ldap.group.form') 
        
    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    lists["form"] = form

    return render_to_response(LDAP_GROUP_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def list_all_sudoer(request):
    try:
        
        lists = dict()
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        
        lists['sudoers'] = get_sudoers(ldap)
        lists['form'] = DeleteForm()
        
    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(LDAP_SUDOER_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def add_sudoer_form(request):
    try:
        
        lists = dict()
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        
        groups_list = get_groups(ldap)

        if request.method == "POST":
            
            commands_list = request.POST.getlist('commands') if "commands" in request.POST else []

            form = SudoerForm(groups_list, commands_list, request.POST)

            if form.is_valid():
                cn = str(form.cleaned_data['cn'])
                sudoHost = str(form.cleaned_data['host'])
                sudoUser = form.cleaned_data['groups']
                sudoCommand = form.cleaned_data['commands']
                
                try:
                    #Valid cn
                    sudoer = None
                    sudoer = ldap.get_sudoer(cn)
                except LDAPError, e:
                    pass
                
                if sudoer is None:
                
                    ldap.add_sudoer(cn, sudoHost, sudoUser, sudoCommand)
                    
                    messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_insert_sudoer"))
                    return redirect('ldap.sudoer.list')

                else:
                    messages.add_message(request, messages.WARNING, ldap_messages.get("error_duplicated_name_sudoer") % cn)

        else:
            
            form = SudoerForm(groups_list)
                                                      

    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists["form"] = form
    lists["action"] = reverse("ldap.sudoer.form")

    return render_to_response(LDAP_SUDOER_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def edit_sudoer_form(request, cn):
    try:
        
        lists = dict()
        lists["edit"] = True
        lists["action"] = reverse("ldap.sudoer.edit", args=[cn])
        
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        groups_list = get_groups(ldap)
            
        if request.method == "POST":
            
            commands_list = request.POST.getlist('commands') if "commands" in request.POST else []
            
            form = SudoerForm(groups_list, commands_list, request.POST)

            if form.is_valid():
                cn = str(form.cleaned_data['cn'])
                sudoHost = str(form.cleaned_data['host'])
                sudoUser = form.cleaned_data['groups']
                sudoCommand = form.cleaned_data['commands']
                
                ldap.edit_sudoer(cn, sudoHost, sudoUser, sudoCommand)
                
                messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_edit_sudoer"))
                return redirect('ldap.sudoer.list')
        else:
        
            sudoer = ldap.get_sudoer(cn)
            
            groups = []
            for grp in validates_dict(sudoer,("sudoUser")):
                groups.append(str(grp).replace("%", ""))
            
            form = SudoerForm(groups_list, validates_dict(sudoer,("sudoCommand")), initial = {'cn': sudoer.get("cn"), 'host': sudoer.get("sudoHost"), 'groups': groups, 'commands': validates_dict(sudoer,("sudoCommand")) })
        
    except LDAPNotFoundError, e:
        messages.add_message(request, messages.ERROR, ldap_messages.get("invalid_sudoer") % cn)
        return redirect('ldap.sudoer.form')
        
    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    lists["form"] = form

    return render_to_response(LDAP_SUDOER_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def delete_sudoer_all(request):

    if request.method == 'POST':

        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        form = DeleteForm(request.POST)

        if form.is_valid():

            # All cns to be deleted
            cns = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each sudoer selected to remove
            for cn in cns:

                try:

                    ldap.rem_sudoer(cn)
                    
                except LDAPNotFoundError, e:
                    error_list.append(cn)
                    have_errors = True

                except LDAPError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove nothing
            if len(error_list) == len(cns):
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
                messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_remove_sudoer"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    return redirect('ldap.sudoer.list')


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def list_all_user(request, pattern):
    try:
        
        lists = dict()
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        formSearch = UserSearchForm()
        
        if request.method == 'POST':
            
            formSearch = UserSearchForm(request.POST)
            
            if formSearch.is_valid():
                
                uidNumner = formSearch.cleaned_data['uidNumner']
                cn = formSearch.cleaned_data['cn']
                name = formSearch.cleaned_data['name']
                lock = formSearch.cleaned_data['lock']
                
                users = []
                for user in get_users_search(ldap, pattern, lock):
                    
                    if uidNumner is not None:
                        if str(uidNumner) != user.get('uidNumber'):
                            continue
                        
                    if cn is not None and cn != "":        
                        if str(cn).upper() not in str(user.get('cn')).upper():
                            continue
                            
                    if name is not None and name != "":        
                        if str(name).upper() not in str(user.get('name')).upper():
                            continue
                        
                    users.append(user)
                 
                lists['users'] = users
            
        else:
            
            lists['users'] = get_users_search(ldap, pattern)       
        
    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    lists['search_form'] = formSearch
    lists['form'] = DeleteForm()
    lists['pattern'] = pattern

    return render_to_response(LDAP_USER_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def ajax_reset_password_user(request):

    lists = dict()
    ldap = Ldap(AuthSession(request.session).get_user().get_username())
    status_code = 500

    try:    
        cn = request.GET['cn']
        ldap.reset_pwd(cn)
        lists["password"] = LDAP_PWD_DEFAULT
        status_code = 200

    except LDAPNotFoundError, e:
        messages.add_message(request, messages.ERROR, ldap_messages.get("invalid_user") % cn)

    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    # Returns HTML
    return HttpResponse(loader.render_to_string(AJAX_LDAP_RESET_PASSWORD, lists, context_instance=RequestContext(request)), status=status_code)


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def delete_user_all(request, pattern):

    if request.method == 'POST':

        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        form = DeleteForm(request.POST)

        if form.is_valid():

            # All cns to be deleted
            cns = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each user selected to remove
            for cn in cns:

                try:

                    ldap.rem_user(cn)
                    
                except LDAPMethodError, e:
                    error_list.append(cn)
                    have_errors = True

                except LDAPError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove nothing
            if len(error_list) == len(cns):
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
                messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_remove_user"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    return HttpResponseRedirect(reverse('ldap.user.list', args=[pattern]))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def add_user_form(request, pattern):

    try:
        
        lists = dict()
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        
        group_list = get_groups(ldap)
        policy_list = get_policies(ldap)
        
        if pattern == PATTERN_TYPES.INTERNAL:
            groupPattern = ldap.groupStandard
            usertype_list = CHOICES_GROUP
            loginShell =  "/bin/bash"
            
        elif pattern == PATTERN_TYPES.EXTERNAL:
            groupPattern = ldap.groupStandardExternal
            usertype_list =  None
            loginShell =  "/sbin/nologin"


        if request.method == "POST":

            form = UserForm(group_list, policy_list, usertype_list, request.POST, initial = {'groupPattern' : groupPattern})
            
            if form.is_valid():
                
                data = form.cleaned_data
                
                for e in data.keys():
                    if type(data[e]) == unicode or type(data[e]) == int:
                        data[e] = str(data[e])
                
                if valid_form_user(ldap, request, data['cn'], data['uidNumber'], data['employeeNumber'], data['mail']):
                    
                    ldap.add_user(data['cn'], data['uidNumber'], data['groupPattern'], data['homeDirectory'], data['givenName'], data['initials'], data['sn'], data['mail'], data['homePhone'], data['mobile'], data['street'], data['description'], data['employeeNumber'], data['employeeType'], data['loginShell'], data['shadowLastChange'], data['shadowMin'], data['shadowMax'], data['shadowWarning'], data['policy'], data['groups'])
                    
                    messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_insert_user"))
                    
                    return HttpResponseRedirect(reverse('ldap.user.list', args=[pattern])) 

        else:
            
            form = UserForm(group_list, policy_list, usertype_list, initial = {'uidNumber': uidNumber_suggest(ldap, pattern), 'groupPattern' : groupPattern, 'shadowMin' : 1, 'shadowMax' : 365, 'shadowWarning' : 335, 'shadowLastChange' : 1, 'loginShell': loginShell})
                                                      

    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists["form"] = form
    lists["pattern"] = pattern
    lists["action"] = reverse("ldap.user.form", args=[pattern])

    return render_to_response(LDAP_USER_FORM, lists, context_instance=RequestContext(request))


def valid_form_user(ldap, request, cn, uidNumber, employeeNumber, mail, edit=False):
    
    #Valid
    is_valid = True
    
    if not edit:
        try:
            ldap.get_user(cn)
            is_valid = False
            messages.add_message(request, messages.WARNING, ldap_messages.get("error_duplicated_name_user") % cn)
        except LDAPError:
            pass

    for usr in get_users(ldap):
        
        if edit and cn == usr.get("cn"):
            continue

        if uidNumber == usr.get("uidNumber"):
            is_valid = False
            messages.add_message(request, messages.WARNING, ldap_messages.get("error_duplicated_uidNumber_user") % uidNumber)
        
        if employeeNumber == usr.get("employeeNumber"):
            is_valid = False
            messages.add_message(request, messages.WARNING, ldap_messages.get("error_duplicated_employeeNumber_user") % employeeNumber)

        if mail == usr.get("mail"):
            is_valid = False
            messages.add_message(request, messages.WARNING, ldap_messages.get("error_duplicated_mail_user") % mail)
        
    return is_valid

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def edit_user_form(request, pattern, cn):
    try:
        
        lists = dict()
        lists["pattern"] = pattern
        lists["action"] =  reverse("ldap.user.edit", kwargs={"pattern": pattern, "cn": cn})
        lists["edit"] = True
    
        ldap = Ldap(AuthSession(request.session).get_user().get_username())
        
        group_list = get_groups(ldap)
        policy_list = get_policies(ldap)
        
        if pattern == PATTERN_TYPES.INTERNAL:
            groupPattern = ldap.groupStandard
            usertype_list = CHOICES_GROUP
            
        elif pattern == PATTERN_TYPES.EXTERNAL:
            groupPattern = ldap.groupStandardExternal
            usertype_list =  None
            
        if request.method == "POST":
            
            form = UserForm(group_list, policy_list, usertype_list, request.POST, initial = {'groupPattern' : groupPattern })

            if form.is_valid():
                
                data = form.cleaned_data
                
                for e in data.keys():
                    if type(data[e]) == unicode or type(data[e]) == int:
                        data[e] = str(data[e])
                        
                if valid_form_user(ldap, request, data['cn'], data['uidNumber'], data['employeeNumber'], data['mail'], edit=True):
                
                    ldap.edit_user(data['cn'], data['uidNumber'], data['groupPattern'], data['homeDirectory'], data['givenName'], data['initials'], data['sn'], data['mail'], data['homePhone'], data['mobile'], data['street'], data['description'], data['employeeNumber'], data['employeeType'], data['loginShell'], data['shadowLastChange'], data['shadowMin'], data['shadowMax'], data['shadowWarning'], data['policy'], data['groups'])
                    
                    messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_edit_user"))
                    return HttpResponseRedirect(reverse('ldap.user.list', args=[pattern]))
        
        else:
            
            user = ldap.get_user(cn)
            user['groups'] = ldap.get_groups_user(cn)
            user['groupPattern'] = groupPattern
            
            form = UserForm(group_list, policy_list, usertype_list, initial=user)
    
    except LDAPNotFoundError, e:
        messages.add_message(request, messages.ERROR, ldap_messages.get("invalid_user") % cn)
        return HttpResponseRedirect(reverse('ldap.user.list', args=[pattern]))
        
    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    lists["form"] = form

    return render_to_response(LDAP_USER_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def ajax_lock_user(request):

    ldap = Ldap(AuthSession(request.session).get_user().get_username())
    status_code = 500

    try:    
        cn = request.GET['cn']
        ldap.lock_user(cn)
        status_code = 200
        messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_lock_user") % cn)

    except LDAPNotFoundError, e:
        messages.add_message(request, messages.ERROR, ldap_messages.get("invalid_user") % cn)

    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponse(status=status_code)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True, "read": True}])
def ajax_unlock_user(request):

    ldap = Ldap(AuthSession(request.session).get_user().get_username())
    status_code = 500
    
    try:    
        cn = request.GET['cn']
        ldap.unlock_user(cn)
        status_code = 200
        messages.add_message(request, messages.SUCCESS, ldap_messages.get("success_unlock_user") % cn)

    except LDAPNotFoundError, e:
        messages.add_message(request, messages.ERROR, ldap_messages.get("invalid_user") % cn)

    except LDAPError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        status_code = 500

    return HttpResponse(status=status_code)