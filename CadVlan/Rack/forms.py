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


class RackForm(forms.Form):

    rack_number = forms.IntegerField(label=u'Numero do Rack', required=True,  
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 150px"}))
    rack_name = forms.CharField(label=u'Nome do Rack', min_length=2, max_length=4, required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    mac_address_sw1 = forms.CharField(label=u'Mac Address', min_length=1, max_length=17, required=False, 
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 150px"}))
    mac_address_sw2 = forms.CharField(label=u'Mac Address', min_length=1, max_length=17, required=False, 
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 150px"}))
    mac_address_ilo = forms.CharField(label=u'Mac Address', min_length=1, max_length=17, required=False,  
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 150px"}))
    nome_sw1 = forms.CharField(label=u'Nome Cadastrado', min_length=3, max_length=50, required=False,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    nome_sw2 = forms.CharField(label=u'Nome Cadastrado', min_length=3, max_length=50, required=False,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    nome_ilo = forms.CharField(label=u'Nome Cadastrado', min_length=3, max_length=50, required=False,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))


