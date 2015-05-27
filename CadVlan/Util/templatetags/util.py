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


from django import template
from django.template.defaultfilters import stringfilter
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.models import Permission, PermissionMenu, SetVariable,\
    IncrementVarNode, PermissionExternal
from CadVlan.settings import MAX_RESULT_DEFAULT
from django.utils.safestring import mark_safe
from django.db.models.query import QuerySet
from django.core.serializers import serialize
from django.utils import simplejson

register = template.Library()

# Constants
MAX_SUBSTRING = 32


@register.simple_tag
def bold(value):
    return '<b>%s</b>' % value


@register.filter
@stringfilter
def substr(value):
    if len(value) > MAX_SUBSTRING:
        return value[0:MAX_SUBSTRING] + "..."
    else:
        return value


@register.simple_tag
def user_name(request):
    auth = AuthSession(request.session)
    return auth.get_user().get_name()


@register.filter
def is_authenticated(request):
    auth = AuthSession(request.session)
    return auth.is_authenticated()


@register.tag
def has_perm(parser, token):
    '''Validates that the user has access permission in view

        @Example: {% has_perm <permission> <write> <read> %}
    '''
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError(
            "'has_perm' tag must be of the form:  {% has_perm <permission> <write> <read> %}")
    return Permission(parts[1], parts[2], parts[3])


@register.tag
def has_external_perm(parser, token):
    """
    Validates that the user has access permission in view

    @Example: {% has_perm <permission> <write> <read> %}

    :param parser:
    :param token:
    :return: Template Node

    """
    parts = token.split_contents()
    if len(parts) < 5:
        raise template.TemplateSyntaxError(
            "'has_external_perm' tag must be of the form:  {% has_perm <permission> <write> <read> <external_token>%}"
        )

    key_permission = 1
    key_write = 2
    key_read = 3
    key_token = 4

    template_node = PermissionExternal(parts[key_permission], parts[key_write], parts[key_read], parts[key_token])

    return template_node


@register.tag
def has_perm_menu(parser, token):
    '''Validates that the user has access permission in top menu

        @Example: {% has_perm_menu <write> <read> %}
    '''
    parts = token.split_contents()
    if len(parts) < 3:
        raise template.TemplateSyntaxError(
            "'has_perm_menu' tag must be of the form:  {% has_perm_menu <write> <read> %}")
    return PermissionMenu(parts[1], parts[2])


@register.tag(name='set')
def set_var(parser, token):
    """
    Example:
        {% set category_list category.categories.all %}
        {% set dir_url "../" %}
        {% set type_list "table" %}
    """
    from re import split
    bits = split(r'\s+', token.contents, 2)
    return SetVariable(bits[1], bits[2])


@register.tag(name='++')
def increment_var(parser, token):

    parts = token.split_contents()
    if len(parts) < 2:
        raise template.TemplateSyntaxError(
            "'increment' tag must be of the form:  {% increment <var_name> %}")
    return IncrementVarNode(parts[1])


@register.simple_tag
def max_results():
    return MAX_RESULT_DEFAULT


@register.filter
def jsonify(json_object):
    if isinstance(json_object, QuerySet):
        return mark_safe(serialize('json', json_object))
    return mark_safe(simplejson.dumps(json_object))


@register.filter
def int_to_str(par_int):
    return str(par_int)