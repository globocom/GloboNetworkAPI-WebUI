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


class VariableForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(VariableForm, self).__init__(*args, **kwargs)


    name = forms.CharField(label=u'Nome', min_length=1, max_length=40, required=True, error_messages=error_messages,
                           widget=forms.TextInput(attrs={'style': "width: 300px"}))
    value = forms.CharField(label=u'Valor', min_length=1, max_length=40, required=True, error_messages=error_messages,
                           widget=forms.TextInput(attrs={'style': "width: 300px"}))
    description = forms.CharField(label=u'Descrição', min_length=1, max_length=40, required=False,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
