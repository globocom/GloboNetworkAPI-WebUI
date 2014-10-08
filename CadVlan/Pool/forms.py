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

    def __init__(self, env_choices, choices_opvip, choices_healthcheck, *args, **kwargs):
        super(PoolForm, self).__init__(*args, **kwargs)


        self.fields['environment'].choices = env_choices
        self.fields['balancing'].choices = choices_opvip
        self.fields['healthcheck'].choices = choices_healthcheck

    identifier = forms.CharField(label=u'Identifier', min_length=3, max_length=40, required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    default_port = forms.CharField(label=u'Default Port', min_length=3, max_length=5, required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))
    environment = forms.ChoiceField(label=u'Environment', choices=[], required=True,
                                  error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))
    balancing = forms.ChoiceField(label=u'Balanceamento', choices=[], required=True,
                              error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))
    healthcheck = forms.ChoiceField(label=u'HealthCheck', choices=[], required=True,
                              error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))


