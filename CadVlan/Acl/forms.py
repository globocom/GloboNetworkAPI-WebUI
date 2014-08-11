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
from CadVlan.Util.utility import check_regex


class AclForm(forms.Form):

    acl = forms.CharField(label=u'ACL', required=False, error_messages=error_messages, widget=forms.Textarea(
        attrs={'style': "width: 800px;height:400px;resize:none;"}))
    comments = forms.CharField(label=u'Comentários', required=False,
                               error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    apply_acl = forms.BooleanField(
        widget=forms.HiddenInput(), label='', required=False)


class TemplateForm(forms.Form):

    def __init__(self, edit=False, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)

        if edit == True:
            self.fields['name'].widget.attrs['readonly'] = True

    name = forms.CharField(label=u'Nome do Template', required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': 'width: 350px'}))
    content = forms.CharField(label=u'Template', required=True, error_messages=error_messages, widget=forms.Textarea(
        attrs={'style': "width: 600px;height:310px;resize:none;"}))


class TemplateAddForm(forms.Form):

    def __init__(self, environment_list, *args, **kwargs):
        super(TemplateAddForm, self).__init__(*args, **kwargs)

        env_choices = ([(env['id'], env["divisao_dc_name"] + " - " + env["ambiente_logico_name"] +
                         " - " + env["grupo_l3_name"]) for env in environment_list["ambiente"]])
        env_choices.insert(0, (0, "-"))

        self.fields['environment'].choices = env_choices

    name = forms.CharField(label=u'Nome do Template', required=False, max_length=250,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': 'width: 350px'}))
    content = forms.CharField(label=u'Template', required=False, error_messages=error_messages, widget=forms.Textarea(
        attrs={'style': "width: 600px;height:310px;resize:none;"}))
    environment = forms.ChoiceField(label="Ambiente", required=False, choices=[(
        0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 400px"}))
    name_ipv6 = forms.CharField(label=u'Nome do Template', required=False,
                                error_messages=error_messages, widget=forms.TextInput(attrs={'style': 'width: 350px'}))
    content_ipv6 = forms.CharField(label=u'Template', required=False, error_messages=error_messages, widget=forms.Textarea(
        attrs={'style': "width: 600px;height:310px;resize:none;"}))

    def clean_name(self):

        if self.cleaned_data['name'] and ' ' in self.cleaned_data['name']:
            raise forms.ValidationError(
                'O nome do template não deve conter espaços')
        elif self.cleaned_data['name'] and not check_regex(self.cleaned_data['name'], "^[a-zA-Z0-9_.-]+$"):
            raise forms.ValidationError(
                'Nome do template contém caracteres inválidos.')

        return self.cleaned_data['name']

    def clean_name_ipv6(self):

        if self.cleaned_data['name_ipv6'] and ' ' in self.cleaned_data['name_ipv6']:
            raise forms.ValidationError(
                'O nome do template não deve conter espaços')
        elif self.cleaned_data['name_ipv6'] and not check_regex(self.cleaned_data['name_ipv6'], "^[a-zA-Z0-9_.-]+$"):
            raise forms.ValidationError(
                'Nome do template contém caracteres inválidos.')

        return self.cleaned_data['name_ipv6']
