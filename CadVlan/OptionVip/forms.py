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

REGEX_TEXT = r"^[0-9a-zA-Z\\-_.\\\-\\ ]*$"


class OptionVipForm(forms.Form):

    id_option = forms.IntegerField(
        label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    name_option = forms.CharField(label=u'Nome', max_length=50, required=True,
                                  error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    type_option = forms.CharField(label=u'Tipo', max_length=50,  required=True,
                                  error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))

    def clean_name_option(self):
        if not check_regex(self.cleaned_data['name_option'], REGEX_TEXT):
            raise forms.ValidationError('Caracteres inválidos.')

        return self.cleaned_data['name_option']

    def clean_type_option(self):
        if not check_regex(self.cleaned_data['type_option'], REGEX_TEXT):
            raise forms.ValidationError('Caracteres inválidos.')

        return self.cleaned_data['type_option']


class OptionVipNetForm(forms.Form):

    def __init__(self, script_type_list, *args, **kwargs):
        super(OptionVipNetForm, self).__init__(*args, **kwargs)
        self.fields['option_vip'].choices = [(st['id'], st[
                                              'tipo_opcao'] + " - " + st['nome_opcao_txt']) for st in script_type_list["option_vip"]]

    option_vip = forms.MultipleChoiceField(
        label=u'Opções VIP', required=False, error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))
