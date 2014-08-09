# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import template
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.permissions import PERMISSIONS


class IncrementVarNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        try:
            value = context[self.var_name]
            context[self.var_name] = value + 1
            return u""
        except:
            raise template.TemplateSyntaxError("The variable does not exist.")


class SetVariable(template.Node):

    def __init__(self, varname, value):
        self.varname = varname
        self.value = value

    def render(self, context):
        var = template.resolve_variable(self.value, context)
        if var:
            context[self.varname] = var
        else:
            context[self.varname] = context[self.value]
        return ''


class Permission(template.Node):

    '''Validates that the user has access permission in view
    '''

    def __init__(self, permission, write, read):
        self.permission = permission
        self.write = write
        self.read = read

    def render(self, context):
        auth = AuthSession(context['request'].session)
        user = auth.get_user()

        if self.write == "None":
            self.write = None

        if self.read == "None":
            self.read = None

        if user.has_perm(
                PERMISSIONS.get(
                    self.permission),
                self.write,
                self.read):
            context["has_perm"] = True
        else:
            context["has_perm"] = False

        return u""


class PermissionMenu(template.Node):

    '''Validates that the user has access permission in top menu
    '''

    def __init__(self, write, read):
        self.write = write
        self.read = read

    def render(self, context):
        auth = AuthSession(context['request'].session)
        user = auth.get_user()

        if self.write == "None":
            self.write = None

        if self.read == "None":
            self.read = None

        if user.has_perm_menu(self.write, self.read):
            context["has_perm"] = True
        else:
            context["has_perm"] = False

        return u""
