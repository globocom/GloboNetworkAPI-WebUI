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


class EquipForm(forms.Form):
    equip_id = forms.IntegerField(
        label='', required=False, widget=forms.HiddenInput())
    equip_name = forms.CharField(
        label='', required=False, widget=forms.HiddenInput())


class DeleteForm(EquipForm):
    ids = forms.CharField(widget=forms.HiddenInput(), label='', required=True)


class DeleteFormAux(EquipForm):
    ids_aux = forms.CharField(
        widget=forms.HiddenInput(), label='', required=True)


class ValidateForm(EquipForm):
    ids_val = forms.CharField(
        widget=forms.HiddenInput(), label='', required=True)


class CreateForm(EquipForm):
    ids_create = forms.CharField(
        widget=forms.HiddenInput(), label='', required=True)


class RemoveForm(EquipForm):
    ids_remove = forms.CharField(
        widget=forms.HiddenInput(), label='', required=True)


class SearchEquipForm(forms.Form):
    equip_name = forms.CharField(label=u'Nome de Equipamento', min_length=3, required=True, widget=forms.TextInput(
        attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default", 'autocomplete': "off"}), error_messages=error_messages)


class ControlAcessForm(forms.Form):
    token = forms.CharField(
        widget=forms.HiddenInput(), label='', required=False)


class ConfigForm(EquipForm):
    ids_config = forms.CharField(
        widget=forms.HiddenInput(), label='', required=True)

class AplicarForm(EquipForm):
    ids_aplicar = forms.CharField(
        widget=forms.HiddenInput(), label='', required=True)

class CriarVlanAmbForm(EquipForm):
    ids_config = forms.CharField(
        widget=forms.HiddenInput(), label='', required=True)
