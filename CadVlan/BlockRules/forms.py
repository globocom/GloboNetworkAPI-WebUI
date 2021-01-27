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


class BlockRulesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BlockRulesForm, self).__init__(*args, **kwargs)

    content = forms.CharField(label=u'Conteúdo',
                              required=True,
                              error_messages=error_messages,
                              widget=forms.Textarea(
                                  attrs={'style': 'width: 300px', 'rows': 10}))


class EnvironmentsBlockForm(forms.Form):

    def __init__(self, env_list, *args, **kwargs):
        super(EnvironmentsBlockForm, self).__init__(*args, **kwargs)
        self.fields['envs'].choices = ([(env['id'], env["name"]) for env in env_list])

    envs = forms.ChoiceField(label=u'Ambiente',
                             error_messages=error_messages)


class EnvironmentRules(forms.Form):

    name = forms.CharField(label="Nome da regra",
                           required=True,
                           error_messages=error_messages,
                           widget=forms.TextInput(
                               attrs={"style": "width: 300px;"}))


class ContentRulesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ContentRulesForm, self).__init__(*args, **kwargs)

    content = forms.CharField(label=u'Conteúdo',
                              required=True,
                              error_messages=error_messages,
                              widget=forms.Textarea(
                                  attrs={'style': 'width: 300px', 'rows': 7}))
    rule_content = forms.CharField(widget=forms.HiddenInput(
        attrs={'order': ''}), label='', required=False, initial=0)


class DeleteForm(forms.Form):

    ids = forms.CharField(widget=forms.HiddenInput(),
                          label='',
                          required=True)
