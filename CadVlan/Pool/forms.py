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


class PoolForm(forms.Form):

    def __init__(self, enviroments_choices, optionsvips_choices, healthcheck_choices=[('', '-')], *args, **kwargs):
        super(PoolForm, self).__init__(*args, **kwargs)

        self.fields['environment'].choices = enviroments_choices
        self.fields['balancing'].choices = optionsvips_choices
        self.fields['health_check'].choices = healthcheck_choices

    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    identifier = forms.CharField(label=u'Identifier', min_length=3, max_length=40, required=True,
                                 error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    default_port = forms.CharField(label=u'Default Port', min_length=2, max_length=5, required=True,
                                   error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))
    environment = forms.ChoiceField(label=u'Environment', choices=[], required=True,
                                    error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))
    balancing = forms.ChoiceField(label=u'Balanceamento', choices=[], required=True,
                                  error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))
    health_check = forms.ChoiceField(label=u'HealthCheck', choices=[], required=True,
                                  error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))
    max_con = forms.IntegerField(label=u'Número máximo de conexões (maxconn)', required=True,
                                error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 231px"}))



class SearchPoolForm(forms.Form):

    def __init__(self, environment_list, *args, **kwargs):

        super(SearchPoolForm, self).__init__(*args, **kwargs)
        env_choices = ([(env['id'], env["divisao_dc_name"] + " - " + env["ambiente_logico_name"] +
                         " - " + env["grupo_l3_name"]) for env in environment_list["ambiente"]])
        env_choices.insert(0, (0, "-"))

        self.fields['environment'].choices = env_choices

    environment = forms.ChoiceField(
        label="Ambiente",
        required=False,
        choices=[(0, "Selecione")],
        error_messages=error_messages,
        widget=forms.Select(attrs={"style": "width: 300px"})
    )


class PoolFormEdit(forms.Form):

    def __init__(self, choices_opvip, *args, **kwargs):

        super(PoolFormEdit, self).__init__(*args, **kwargs)

        self.fields['balancing'].choices = choices_opvip
        self.fields['balancing'].choices.insert(0, ('',''))

    default_port = forms.CharField(label=u'Default Port', min_length=2, max_length=5, required=True,
                                   error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))
    balancing = forms.ChoiceField(label=u'Balanceamento', choices=[], required=True,
                                  error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))
