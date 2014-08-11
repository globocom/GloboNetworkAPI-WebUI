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


class UserForm(forms.Form):

    def __init__(self, group_list, ldap_group_list=None, ldap_user_list=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if group_list is not None:
            self.fields['groups'].choices = [
                (gl['id'], gl['nome']) for gl in group_list["user_group"]]

        if ldap_group_list is not None:
            self.fields['ldap_group'].choices = [
                (ldap_grp[0], ldap_grp[1]) for ldap_grp in ldap_group_list]

        if ldap_user_list is not None:
            self.fields['ldap_user'].choices = [
                (ldap_usr, ldap_usr) for ldap_usr in ldap_user_list]

    name = forms.CharField(label=u'Nome', required=True, max_length=200, min_length=3,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    email = forms.EmailField(label=u'Email', required=True, max_length=300, min_length=6,
                             error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    user = forms.CharField(label=u'Usuário', required=True, max_length=45, min_length=3,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))

    is_ldap = forms.BooleanField(label='Associar usuário LDAP', required=False)
    ldap_group = forms.ChoiceField(label='Grupo LDAP', required=False)
    ldap_user = forms.ChoiceField(label='Usuário LDAP', required=False, widget=forms.Select(
        attrs={'style': "width: 507px", 'size': "10"}))

    groups = forms.MultipleChoiceField(label=u'Grupos de Usuário', required=False,
                                       error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))
    password = forms.CharField(
        label='', required=False, widget=forms.HiddenInput())
    active = forms.BooleanField(
        label='', required=False, widget=forms.HiddenInput())

    def clean_ldap_user(self):

        try:
            is_ldap = self.cleaned_data['is_ldap']
            if not is_ldap:
                raise KeyError

            if self.cleaned_data['ldap_user'] == '':
                raise forms.ValidationError(
                    'Escolha um usuário LDAP para associar')

        except KeyError:
            self.cleaned_data['ldap_group'] = None
            self.cleaned_data['ldap_user'] = None

        return self.cleaned_data['ldap_user']
