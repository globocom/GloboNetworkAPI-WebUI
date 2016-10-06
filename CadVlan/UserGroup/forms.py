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
from django import forms

from CadVlan.messages import error_messages


class UserGroupForm(forms.Form):

    def __init__(self, user_list, *args, **kwargs):
        super(UserGroupForm, self).__init__(*args, **kwargs)
        if user_list is not None:
            self.fields['users'].choices = [
                (st['id'], st['nome']) for st in user_list["users"]]

    users = forms.MultipleChoiceField(
        label=u'Usuários', required=True, error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))


class PermissionGroupForm(forms.Form):

    def __init__(self, function_list, *args, **kwargs):
        super(PermissionGroupForm, self).__init__(*args, **kwargs)
        self.fields['function'].choices = [
            (st['id'], st['function']) for st in function_list]

    id_group_perms = forms.IntegerField(
        label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    function = forms.ChoiceField(
        label=u'Função', required=True, error_messages=error_messages)
    read = forms.BooleanField(
        label=u'Leitura', required=False, error_messages=error_messages)
    write = forms.BooleanField(
        label=u'Escrita', required=False, error_messages=error_messages)


class IndividualPermsGroupUserForm(forms.Form):

    id_obj = forms.IntegerField(label="", widget=forms.HiddenInput(), required=False)
    id_type_obj = forms.IntegerField(label="", widget=forms.HiddenInput(), required=False)
    id_group = forms.IntegerField(label="", widget=forms.HiddenInput(), required=False)

    read = forms.BooleanField(widget=forms.CheckboxInput(), required=False)

    write = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    change_config = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    delete = forms.BooleanField(widget=forms.CheckboxInput(), required=False)


class GeneralPermsGroupUserForm(forms.Form):

    id_type_obj = forms.IntegerField(label="", widget=forms.HiddenInput(), required=False)
    id_group = forms.IntegerField(label="", widget=forms.HiddenInput(), required=False)

    read = forms.BooleanField(widget=forms.CheckboxInput(), required=False)

    write = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    change_config = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    delete = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
