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


class EquipGroupForm(forms.Form):

    id_egroup = forms.IntegerField(
        label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    egroup = forms.CharField(label=u'Nome Grupo', min_length=3, max_length=50,  required=False,
                             error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px", 'readonly': 'readonly'}))
    equip_name = forms.CharField(label=u'Nome de Equipamento', min_length=3, required=True, widget=forms.TextInput(
        attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default", 'autocomplete': "off"}), error_messages=error_messages)


class UserEquipGroupForm(forms.Form):

    def __init__(self, ugroup_list, *args, **kwargs):
        super(UserEquipGroupForm, self).__init__(*args, **kwargs)

        ugroup_choices = [(group["id"], group["nome"])
                          for group in ugroup_list["user_group"]]
        ugroup_choices.insert(0, ('', "-"))

        self.fields['ugroup'].choices = ugroup_choices

    id_egroup = forms.IntegerField(
        label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    egroup = forms.CharField(label=u'Nome Grupo', min_length=3, max_length=50,  required=False,
                             error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px", 'readonly': 'readonly'}))
    ugroup = forms.ChoiceField(label="Grupo de Usuários", required=True, choices=[(
        0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 340px"}))
    update = forms.BooleanField(
        label="Alterar Config", required=False, initial=False)
    write = forms.BooleanField(label="Escrita", required=False, initial=False)
    read = forms.BooleanField(label="Leitura", required=False, initial=False)
    delete = forms.BooleanField(
        label="Exclusão      ", required=False, initial=False)
