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
from django.core.cache import cache
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

        if user.has_perm(PERMISSIONS.get(self.permission), self.write, self.read):
            context["has_perm"] = True
        else:
            context["has_perm"] = False

        return u""


class PermissionExternal(template.Node):
    """
        Validates that the user has access permission in view from access external
    """

    def __init__(self, permission, write, read, external_token):
        self._permission = permission
        self._write = write
        self._read = read
        self._external_token = template.Variable(external_token)

    def render(self, context):

        condition = "True"
        has_permission = False
        token = self._external_token.resolve(context)

        if token in cache:

            data_from_cache = cache.get(token)
            permissions = data_from_cache.get('permissions')
            required_permission = PERMISSIONS.get(self._permission)
            permission = permissions.get(required_permission)

            write_required = condition == self._write
            read_required = condition == self._read
            write_permission = condition == permission.get('write')
            read_permission = condition == permission.get('read')

            if (not write_required or write_permission) and (not read_required or read_permission):
                has_permission = True

        context["has_external_perm"] = has_permission

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
