# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import template
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.models import Set, Permission, PermissionMenu

register = template.Library()

# Constants
MAX_SUBSTRING = 30;


@register.simple_tag
def bold(value):
    return '<b>%s</b>' % value

@register.filter
def substring(value):
    if value > MAX_SUBSTRING :
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

@register.tag
def set(parser, token):
    ''' Creates and sets the variable in view
    
        @Example: {% set <var_name>  = <var_value> %} 
    '''
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %}")
    return Set(parts[1], parts[3])
 
