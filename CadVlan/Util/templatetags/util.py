# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import template
from django.template.defaultfilters import stringfilter
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.models import Permission, PermissionMenu, SetVariable,\
    IncrementVarNode
from CadVlan.settings import MAX_RESULT_DEFAULT

register = template.Library()

# Constants
MAX_SUBSTRING = 32;


@register.simple_tag
def bold(value):
    return '<b>%s</b>' % value

@register.filter
@stringfilter
def substr(value):
    if len(value) > MAX_SUBSTRING :
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
        raise template.TemplateSyntaxError("'has_perm' tag must be of the form:  {% has_perm <permission> <write> <read> %}")
    return Permission(parts[1], parts[2], parts[3])

@register.tag
def has_perm_menu(parser, token):
    '''Validates that the user has access permission in top menu
    
        @Example: {% has_perm_menu <write> <read> %}
    '''
    parts = token.split_contents()
    if len(parts) < 3:
        raise template.TemplateSyntaxError("'has_perm_menu' tag must be of the form:  {% has_perm_menu <write> <read> %}")
    return PermissionMenu(parts[1], parts[2])

@register.tag(name='set')
def set_var(parser,token):
    """
    Example:
        {% set category_list category.categories.all %}
        {% set dir_url "../" %}
        {% set type_list "table" %}
    """
    from re import split
    bits = split(r'\s+', token.contents, 2)
    return SetVariable(bits[1],bits[2])

@register.tag(name='++')
def increment_var(parser, token):

    parts = token.split_contents()
    if len(parts) < 2:
        raise template.TemplateSyntaxError("'increment' tag must be of the form:  {% increment <var_name> %}")
    return IncrementVarNode(parts[1])

@register.simple_tag
def max_results():
    return MAX_RESULT_DEFAULT
