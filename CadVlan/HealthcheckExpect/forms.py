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


class HealthckeckExpectForm(forms.Form):

    def __init__(self, environment_list, *args, **kwargs):
        super(HealthckeckExpectForm, self).__init__(*args, **kwargs)

        env_choices = ([
            (env['id'], env['name']) for env in environment_list["environments"]])
        env_choices.insert(0, (0, "-"))
        self.fields['environment'].choices = env_choices

    match_list = forms.CharField(label=u'Match List',
                                 min_length=2,
                                 max_length=50,
                                 required=True,
                                 error_messages=error_messages,
                                 widget=forms.TextInput(
                                     attrs={'style': "width: 200px"}))
    expect_string = forms.CharField(label=u'Except String',
                                    min_length=2,
                                    max_length=50,
                                    required=True,
                                    error_messages=error_messages,
                                    widget=forms.TextInput(
                                        attrs={'style': "width: 200px"}))
    environment = forms.ChoiceField(label="Ambiente",
                                    choices=[(0, "Selecione")],
                                    error_messages=error_messages,
                                    widget=forms.Select(
                                        attrs={"style": "width: 300px"}))

    def clean_environment(self):
        if int(self.cleaned_data['environment']) <= 0:
            raise forms.ValidationError('Este campo é obrigatório')

        return self.cleaned_data['environment']
