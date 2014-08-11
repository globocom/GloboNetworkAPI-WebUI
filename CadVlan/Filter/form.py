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


class FilterForm(forms.Form):

    def __init__(self, equip_type_list, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['equip_type'].choices = [
            (et['id'], et['nome']) for et in equip_type_list["equipment_type"]]

    id = forms.IntegerField(
        label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    name = forms.CharField(label=u'Nome', min_length=3, max_length=100, required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    description = forms.CharField(label=u'Descrição', min_length=3, max_length=200,  required=True,
                                  error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    equip_type = forms.MultipleChoiceField(label=u'Tipos de equipamento', required=True,
                                           error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))
