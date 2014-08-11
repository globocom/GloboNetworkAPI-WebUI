from django import forms

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

from CadVlan.messages import error_messages


class EquipAccessForm(forms.Form):

    def __init__(self, protocol_list, *args, **kwargs):
        super(EquipAccessForm, self).__init__(*args, **kwargs)
        self.fields['protocol'].choices = [
            (p['id'], p['protocolo']) for p in protocol_list["tipo_acesso"]]

    host = forms.CharField(label=u'Host', min_length=5, max_length=100, required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    user = forms.CharField(label=u'Usuario', min_length=3, max_length=20, required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    password = forms.CharField(label=u'Senha', min_length=3, max_length=150, required=True,
                               error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 300px"}, render_value=True))
    second_password = forms.CharField(label=u'Senha secundaria', min_length=3, max_length=150, required=True,
                                      error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 300px"}, render_value=True))
    protocol = forms.ChoiceField(label=u'Protocolo', choices=[(
        0, 'Selecione')], required=True, error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))
    id_equip = forms.CharField(
        widget=forms.HiddenInput(), label='', required=False)
    name_equip = forms.CharField(
        widget=forms.HiddenInput(), label='', required=False)
