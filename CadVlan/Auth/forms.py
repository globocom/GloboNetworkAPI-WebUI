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


class LoginForm(forms.Form):
    redirect = forms.CharField(
        widget=forms.HiddenInput(), label='', required=False)
    is_ldap_user = forms.BooleanField(
        widget=forms.HiddenInput(), label='', required=False)
    username = forms.CharField(label=u'Usuário', min_length=3, max_length=45, required=True,
                               error_messages=error_messages, widget=forms.TextInput(
            attrs={'style': "width: 150px;border-radius:3px;height:30.59px;"}))
    password = forms.CharField(label=u'Senha', min_length=3, max_length=45, required=True,
                               error_messages=error_messages, widget=forms.PasswordInput(
            attrs={'style': "width: 150px;border-radius:3px;height:30.59px;"}))


class PassForm(forms.Form):
    username = forms.CharField(label=u'Usuário', min_length=3, max_length=45, required=True,
                               error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    email = forms.EmailField(label=u'Email', min_length=6, max_length=300, required=True,
                             error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))


class ChangePassForm(forms.Form):
    new_pass = forms.CharField(label=u'Nova senha (somente autenticacao local)', min_length=6, max_length=20, required=True,
                               error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 200px"}))
    confirm_new_password = forms.CharField(label=u'Confirme a nova senha (somente autenticacao local)', min_length=6, max_length=20,
                                           required=True, error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 200px"}))

    def clean_confirm_new_password(self):
        if self.cleaned_data['confirm_new_password'] != self.data['new_pass']:
            raise forms.ValidationError('Confirmacao da senha nao confere')

        return self.cleaned_data['confirm_new_password']
