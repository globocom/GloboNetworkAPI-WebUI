# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from CadVlan.Acl.acl import alterAclGit, deleteAclGit, getAclGit, createAclGit, scriptAclGit, script_template, applyAcl,\
    PATH_ACL_TEMPLATES, get_templates, get_template_edit, alter_template,\
    create_template, check_template, delete_template
from CadVlan.Acl.forms import AclForm, TemplateForm, TemplateAddForm
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.Enum import NETWORK_TYPES
from CadVlan.Util.converters.util import split_to_array, replace_id_to_name
from CadVlan.Util.git import GITError, Git
from CadVlan.Util.utility import validates_dict, clone, acl_key, IP_VERSION
from CadVlan.forms import DeleteForm
from CadVlan.messages import acl_messages, error_messages
from CadVlan.permissions import VLAN_MANAGEMENT, ENVIRONMENT_MANAGEMENT
from CadVlan.templates import ACL_FORM, ACL_APPLY_LIST, ACL_APPLY_RESULT,\
    ACL_TEMPLATE, ACL_TEMPLATE_EDIT_FORM,\
    ACL_TEMPLATE_ADD_FORM
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError
from django.views.decorators.http import require_http_methods
import logging
from CadVlan.settings import PATH_ACL
import urllib

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
        environment = client.create_ambiente().buscar_por_id(
            vlan.get("ambiente")).get("ambiente")

        key_acl = acl_key(network)

        createAclGit(vlan.get(key_acl), environment, network,
                     AuthSession(request.session).get_user())

        messages.add_message(
            request, messages.SUCCESS, acl_messages.get("success_create"))

    except (NetworkAPIClientError, GITError, ValueError), e:
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
        environment = client.create_ambiente().buscar_por_id(
            vlan.get("ambiente")).get("ambiente")

        key_acl = acl_key(network)

        if vlan.get(key_acl) is None:
            messages.add_message(
                request, messages.ERROR, acl_messages.get("error_acl_not_exist"))
            return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))

        if network == NETWORK_TYPES.v4:
            client.create_vlan().invalidate(id_vlan)

        else:
            client.create_vlan().invalidate_ipv6(id_vlan)

        deleteAclGit(vlan.get(key_acl), environment, network,
                     AuthSession(request.session).get_user())

        messages.add_message(
            request, messages.SUCCESS, acl_messages.get("success_remove"))

    except (NetworkAPIClientError, GITError, ValueError), e:
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
        environment = client.create_ambiente().buscar_por_id(
            vlan.get("ambiente")).get("ambiente")

        key_acl = acl_key(network)

        if vlan.get(key_acl) is None:
            messages.add_message(
                request, messages.ERROR, acl_messages.get("error_acl_not_exist"))
            return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))

        if network == NETWORK_TYPES.v4:
            template_name = environment['ipv4_template']
        else:
            template_name = environment['ipv6_template']

        scriptAclGit(vlan.get(key_acl), vlan, environment, network, AuthSession(
            request.session).get_user(), template_name)

    except (NetworkAPIClientError, GITError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('acl.edit', args=[id_vlan, network]))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def edit(request, id_vlan, network):

    lists = dict()
    lists['id_vlan'] = id_vlan

    # Type Network
    lists['network'] = network

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        vlan = client.create_vlan().get(id_vlan).get("vlan")
        environment = client.create_ambiente().buscar_por_id(vlan.get("ambiente")).get("ambiente")

        if network == NETWORK_TYPES.v4:
            template_name = environment['ipv4_template']
        else:
            template_name = environment['ipv6_template']

        key_acl = acl_key(network)

        if vlan.get(key_acl) is None:
            messages.add_message(
                request, messages.ERROR, acl_messages.get("error_acl_not_exist"))
            return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))

        lists['vlan'] = vlan
        vlan['ambiente'] = "%s - %s - %s" % (environment.get("nome_divisao"), environment.get(
            "nome_ambiente_logico"), environment.get("nome_grupo_l3"))

        if request.method == "POST":

            form = AclForm(request.POST)
            lists['form'] = form

            if form.is_valid():

                acl = form.cleaned_data['acl']
                comments = form.cleaned_data['comments']
                apply_acl = form.cleaned_data['apply_acl']

                alterAclGit(vlan.get(key_acl), acl, environment, comments, network, AuthSession(
                    request.session).get_user())

                #Remove Draft
                client.create_api_vlan().acl_remove_draft(id_vlan, network)

                if network == NETWORK_TYPES.v4:
                    vlan["acl_draft"] = None
                else:
                    vlan["acl_draft_v6"] = None

                lists['form'] = AclForm(
                    initial={'acl': form.cleaned_data['acl'], 'comments': ''})

                messages.add_message(
                    request, messages.SUCCESS, acl_messages.get("success_edit"))

                # If click apply ACL
                if apply_acl == True:
                    return HttpResponseRedirect(reverse('acl.apply', args=[id_vlan, network]))

        else:

            content = getAclGit(vlan.get(key_acl), environment, network, AuthSession(request.session).get_user())
            lists['form'] = AclForm(initial={'acl': content, 'comments': ''})

            if network == NETWORK_TYPES.v4:
                if vlan["acl_draft"] == content:
                    vlan["acl_draft"] = None
            else:
                if vlan["acl_draft_v6"] == content:
                    vlan["acl_draft_v6"] = None

            if content is None or content == "":
                lists['script'] = script_template(environment.get("nome_ambiente_logico"), environment.get(
                    "nome_divisao"), environment.get("nome_grupo_l3"), template_name)

        list_ips = []
        if len(vlan["redeipv4"]) > 0 and network == NETWORK_TYPES.v4:

            for net in vlan["redeipv4"]:
                n = {}
                n["ip"] = "%s.%s.%s.%s" % (
                    net["oct1"], net["oct2"], net["oct3"], net["oct4"])
                n["mask"] = "%s.%s.%s.%s" % (
                    net["mask_oct1"], net["mask_oct2"], net["mask_oct3"], net["mask_oct4"])
                n["network_type"] = net["network_type"]
                list_ips.append(n)

        elif len(vlan["redeipv6"]) > 0 and network == NETWORK_TYPES.v6:

            for net in vlan["redeipv6"]:
                n = {}
                n["ip"] = "%s:%s:%s:%s:%s:%s:%s:%s" % (net["block1"], net["block2"], net[
                                                       "block3"], net["block4"], net["block5"], net["block6"], net["block7"], net["block8"])
                n["mask"] = "%s:%s:%s:%s:%s:%s:%s:%s" % (net["mask1"], net["mask2"], net[
                                                         "mask3"], net["mask4"], net["mask5"], net["mask6"], net["mask7"], net["mask8"])
                n["network_type"] = net["network_type"]
                list_ips.append(n)

        # Replace id network_type for name network_type
        vlan['network'] = replace_id_to_name(list_ips, client.create_tipo_rede(
        ).listar().get('net_type'), "network_type", "id", "name")

    except (NetworkAPIClientError, GITError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ACL_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def apply_acl(request, id_vlan, network):

    lists = dict()
    lists['id_vlan'] = id_vlan
    lists['form'] = DeleteForm()

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        vlan = client.create_vlan().get(id_vlan).get("vlan")
        environment = client.create_ambiente().buscar_por_id(
            vlan.get("ambiente")).get("ambiente")

        key_acl = acl_key(network)

        if vlan.get(key_acl) is None:
            messages.add_message(
                request, messages.ERROR, acl_messages.get("error_acl_not_exist"))
            return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))

        lists['vlan'] = vlan
        lists['environment'] = "%s - %s - %s" % (environment.get("nome_divisao"), environment.get(
            "nome_ambiente_logico"), environment.get("nome_grupo_l3"))

        # Type Network
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
                    apply_result = client.create_vlan().apply_acl(
                        equipments, vlan, environment, network)

                    is_apply = apply_result.get('is_apply')
                    result = apply_result.get('result')
                    if is_apply == '0':

                        lists['result'] = result

                        messages.add_message(
                            request, messages.SUCCESS, acl_messages.get("success_apply"))

                        return render_to_response(ACL_APPLY_RESULT, lists, context_instance=RequestContext(request))

                    else:
                        messages.add_message(
                            request, messages.ERROR, acl_messages.get("error_apply"))
            else:
                messages.add_message(
                    request, messages.ERROR, error_messages.get("select_one"))

        list_equipments = []
        if len(vlan["redeipv4"]) > 0 and network == NETWORK_TYPES.v4:

            for net in vlan["redeipv4"]:

                try:

                    ips = client.create_ip().find_ip4_by_network(
                        net["id"]).get('ips')

                    for ip in ips:
                        equipment = {}
                        equipment["description"] = ip["descricao"]
                        equipment["ip"] = "%s.%s.%s.%s" % (
                            ip["oct1"], ip["oct2"], ip["oct3"], ip["oct4"])
                        equips = validates_dict(ip, "equipamento")

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

                    ips = client.create_ip().find_ip6_by_network(
                        net["id"]).get('ips')

                    for ip in ips:
                        equipment = {}
                        equipment["description"] = ip["descricao"]
                        equipment["ip"] = "%s:%s:%s:%s:%s:%s:%s:%s" % (ip["block1"], ip["block2"], ip[
                                                                       "block3"], ip["block4"], ip["block5"], ip["block6"], ip["block7"], ip["block8"])
                        equips = validates_dict(ip, "equipamento")

                        for equip in equips:
                            equipment_base = clone(equipment)
                            equipment_base["id"] = ip["id"]
                            equipment_base["name"] = equip["nome"]
                            list_equipments.append(equipment_base)

                except (NetworkAPIClientError), e:
                    pass

        lists["equipments"] = list_equipments

    except (NetworkAPIClientError, GITError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ACL_APPLY_LIST, lists, context_instance=RequestContext(request))


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

        messages.add_message(
            request, messages.SUCCESS, acl_messages.get("success_validate") % network)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse('vlan.edit.by.id', args=[id_vlan]))

""" --- TEMPLATES --- """


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def template_list(request):
    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()

        # Get user
        user = AuthSession(request.session).get_user()

        templates = get_templates(user)
        lists['templates'] = list()
        lists["delete_form"] = DeleteForm()

        for template in templates:
            envs = client.create_ambiente().get_environment_template(
                template['name'], template['network'])
            if envs:
                envs = envs['ambiente'] if not isinstance(
                    envs['ambiente'], unicode) else [envs['ambiente'], ]
            lists['templates'].append(
                {'name': template['name'], 'network': template['network'], 'envs': envs})

    except (NetworkAPIClientError, GITError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ACL_TEMPLATE, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}, {"permission": ENVIRONMENT_MANAGEMENT, "read": True}])
def template_add(request):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get user
        user = AuthSession(request.session).get_user()

        environment = client.create_ambiente().list_all()

        lists = dict()

        lists['form'] = TemplateAddForm(environment)

        if request.method == 'POST':

            form = TemplateAddForm(environment, request.POST)

            lists['form'] = form

            name_ipv4 = request.POST['name']
            content_ipv4 = request.POST['content']
            name_ipv6 = request.POST['name_ipv6']
            content_ipv6 = request.POST['content_ipv6']
            environment = request.POST['environment']

            if form.is_valid() and __valid_add_form(request, name_ipv4, content_ipv4, name_ipv6, content_ipv6):

                duplicate = False

                if name_ipv4 and content_ipv4:
                    if check_template(name_ipv4, IP_VERSION.IPv4[1], user):
                        duplicate = True
                        messages.add_message(
                            request, messages.ERROR, acl_messages.get("field_duplicated") % name_ipv4)
                    else:
                        create_template(
                            name_ipv4, IP_VERSION.IPv4[1], content_ipv4, user)

                        if int(environment) != 0:
                            client.create_ambiente().set_template(
                                environment, name_ipv4, IP_VERSION.IPv4[1])

                if name_ipv6 and content_ipv6:
                    if check_template(name_ipv6, IP_VERSION.IPv6[1], user):
                        duplicate = True
                        messages.add_message(
                            request, messages.ERROR, acl_messages.get("field_duplicated") % name_ipv6)
                    else:
                        create_template(
                            name_ipv6, IP_VERSION.IPv6[1], content_ipv6, user)

                        if int(environment) != 0:
                            client.create_ambiente().set_template(
                                environment, name_ipv6, IP_VERSION.IPv6[1])

                if not duplicate:
                    messages.add_message(
                        request, messages.SUCCESS, acl_messages.get("success_template_edit"))
                    return redirect('acl.template.list')

    except (NetworkAPIClientError, GITError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ACL_TEMPLATE_ADD_FORM, lists, context_instance=RequestContext(request))


def __valid_add_form(request, name_ipv4, content_ipv4, name_ipv6, content_ipv6):

    if not name_ipv4 and not content_ipv4 and not name_ipv6 and not content_ipv6:
        messages.add_message(
            request, messages.ERROR, acl_messages.get('field_required'))
        return False
    elif (not name_ipv4 and content_ipv4) or (name_ipv4 and not content_ipv4):
        messages.add_message(
            request, messages.ERROR, acl_messages.get('field_required'))
        return False
    elif (not name_ipv6 and content_ipv6) or (name_ipv6 and not content_ipv6):
        messages.add_message(
            request, messages.ERROR, acl_messages.get('field_required'))
        return False

    return True


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def template_edit(request, template_name, network):

    try:

        # Get user
        user = AuthSession(request.session).get_user()

        lists = dict()

        lists['template_name'] = template_name
        lists['network'] = network

        if check_template(template_name, network, user):
            content = get_template_edit(template_name, network, user)
        else:
            messages.add_message(
                request, messages.ERROR, acl_messages.get("invalid_template"))
            return redirect('acl.template.list')

        lists['form'] = TemplateForm(
            True, initial={'name': template_name, 'content': content})

        if request.method == 'POST':
            form = TemplateForm(True, request.POST)
            lists['form'] = form

            if form.is_valid():
                alter_template(
                    template_name, network, form.cleaned_data['content'], user)

                messages.add_message(
                    request, messages.SUCCESS, acl_messages.get("success_template_edit"))

                return redirect('acl.template.list')
    except (NetworkAPIClientError, GITError, ValueError), e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(ACL_TEMPLATE_EDIT_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def template_delete(request):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            user = AuthSession(request.session).get_user()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            for id in ids:
                id_split = id.split('+')
                template_name = id_split[0]
                template_name = urllib.unquote_plus(str(template_name))
                network = id_split[1]

                if check_template(template_name, network, user):
                    client.create_ambiente().set_template(
                        0, template_name, network)
                    delete_template(template_name, network, user)

            messages.add_message(
                request, messages.SUCCESS, acl_messages.get("success_remove"))
        else:
            messages.add_message(
                request, messages.ERROR, error_messages.get("select_one"))

    return HttpResponseRedirect(reverse('acl.template.list'))


@log
@login_required
@require_http_methods(["POST"])
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def save_draft(request):

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        id_vlan = request.POST.get('id_vlan')
        type_acl = request.POST.get('type_acl')
        content_draft = request.POST.get('content_draft')

        client.create_api_vlan().acl_save_draft(id_vlan, type_acl, content_draft)

        return HttpResponse()

    except NetworkAPIClientError, exception:
        logger.error(exception)
        return HttpResponse(exception, status=203)

    except Exception, exception:
        logger.error(exception)
        return HttpResponse(exception, status=203)


@log
@login_required
@require_http_methods(["GET"])
@has_perm([{"permission": VLAN_MANAGEMENT, "write": True}])
def remove_draft(request):

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        id_vlan = request.GET.get('id_vlan')
        type_acl = request.GET.get('type_acl')

        client.create_api_vlan().acl_remove_draft(id_vlan, type_acl)

        return HttpResponse()

    except NetworkAPIClientError, exception:
        logger.error(exception)
        return HttpResponse(exception, status=203)

    except Exception, exception:
        logger.error(exception)
        return HttpResponse(exception, status=203)