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
from CadVlan.Util.forms.decorators import autostrip


class PoolForm(forms.Form):

    def __init__(self, enviroments_choices, optionsvips_choices, servicedownaction_choices, healthcheck_choices=[('', '')], *args, **kwargs):
        super(PoolForm, self).__init__(*args, **kwargs)

        self.fields['environment'].choices = enviroments_choices
        self.fields['balancing'].choices = optionsvips_choices
        self.fields['servicedownaction'].choices = servicedownaction_choices
        self.fields['health_check'].choices = healthcheck_choices

    id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )

    identifier = forms.CharField(
        label=u'Identifier',
        min_length=3,
        max_length=200,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={'style': "width: 300px"}
        )
    )

    default_port = forms.CharField(
        label=u'Default Port',
        min_length=2,
        max_length=5,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={'style': "width: 100px"}
        )
    )
    environment = forms.ChoiceField(
        label=u'Environment',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={'style': "width: 310px"}
        )
    )
    balancing = forms.ChoiceField(
        label=u'Balanceamento',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={'style': "width: 310px"}
        )
    )
    servicedownaction = forms.ChoiceField(
        label=u'Action on ServiceDown',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={'style': "width: 310px"}
        )
    )
    health_check = forms.ChoiceField(
        label=u'HealthCheck',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={'style': "width: 310px"}
        )
    )
    max_con = forms.IntegerField(
        label=u'Número máximo de conexões (maxconn)',
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={'style': "width: 231px"}
        )
    )


@autostrip
class PoolFormV3(forms.Form):

    def __init__(self, enviroments_choices, optionsvips_choices,
                 servicedownaction_choices, *args, **kwargs):
        super(PoolFormV3, self).__init__(*args, **kwargs)

        self.fields['environment'].choices = enviroments_choices
        self.fields['balancing'].choices = optionsvips_choices
        self.fields['servicedownaction'].choices = servicedownaction_choices

    identifier = forms.CharField(
        label=u'Identifier',
        min_length=3,
        max_length=200,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                "style": "width: 300px"}
        )
    )

    default_port = forms.IntegerField(
        label=u'Default Port',
        min_value=1,
        max_value=65535,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                "style": "width: 100px"}
        )
    )

    environment = forms.ChoiceField(
        label=u'Environment',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "",
                "style": "width: 310px",
                'class': 'select2'
            }
        )
    )

    balancing = forms.ChoiceField(
        label=u'Balanceamento',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "width: 310px",
                'class': 'select2'
            }
        )
    )

    servicedownaction = forms.ChoiceField(
        label=u'Action on ServiceDown',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "width: 310px",
                'class': 'select2'}
        )
    )

    maxcon = forms.IntegerField(
        label=u'Número máximo de conexões (maxconn)',
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                "style": "width: 100px"}
        )
    )


@autostrip
class PoolGroupUsersForm(forms.Form):

    def __init__(self, forms_aux, edit, *args, **kwargs):
        super(PoolGroupUsersForm, self).__init__(*args, **kwargs)

        self.fields['group_users'].choices = [(gu["id"], gu["nome"]) for gu in forms_aux["user_group"]]
        if not edit:
            del self.fields['overwrite']
        else:
            self.fields['overwrite'].check_test = False

    group_users = forms.MultipleChoiceField(
        label=u'Grupo de usuários',
        required=False,
        error_messages=error_messages,
        widget=forms.SelectMultiple(attrs={'style': "width: 310px"})
    )

    overwrite = forms.BooleanField(
        label='Sobrescrever permissões?',
        required=False,
        error_messages=error_messages,
        widget=forms.CheckboxInput()
    )


@autostrip
class PoolHealthcheckForm(forms.Form):

    def __init__(self, healthcheck_choices=[], *args, **kwargs):
        super(PoolHealthcheckForm, self).__init__(*args, **kwargs)

        self.fields['healthcheck'].choices = healthcheck_choices

    healthcheck = forms.ChoiceField(
        label=u'HealthCheck',
        choices=[],
        required=False,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "width: 310px",
                'class': 'select2'}
        )
    )

    healthcheck_request = forms.CharField(
        label=u'Healthcheck Request',
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                "style": "width: 310px"}
        )
    )

    healthcheck_expect = forms.CharField(
        label=u'HTTP Expect String',
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                "style": "width : 310px"}
        )
    )

    healthcheck_destination = forms.IntegerField(
        label=u'Porta',
        min_value=1,
        max_value=65535,
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                "style": "width: 100px"}
        )
    )


class SearchPoolForm(forms.Form):

    def __init__(self, environment_list, *args, **kwargs):

        super(SearchPoolForm, self).__init__(*args, **kwargs)
        env_choices = ([(env['id'], env["name"]) for env in environment_list])
        env_choices.insert(0, (0, "Busque pelo Ambiente do Pool..."))

        self.fields['environment'].choices = env_choices

    environment = forms.ChoiceField(
        label="Ambiente",
        required=False,
        choices=[(0, "Busque pelo Ambiente do Pool...")],
        error_messages=error_messages,
        widget=forms.Select(
            attrs={"class": "form-control",
                   "style": "height: 2.7em;"}
        )
    )


class PoolFormEdit(forms.Form):

    def __init__(self, choices_opvip, servicedownaction_choices, *args, **kwargs):

        super(PoolFormEdit, self).__init__(*args, **kwargs)

        self.fields['balancing'].choices = choices_opvip
        self.fields['balancing'].choices.insert(0, ('', ''))

        self.fields['servicedownaction'].choices = servicedownaction_choices
        self.fields['servicedownaction'].choices.insert(0, ('', ''))

    default_port = forms.CharField(
        label=u'Default Port',
        min_length=2,
        max_length=5,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={'style': "width: 100px"}
        )
    )
    balancing = forms.ChoiceField(
        label=u'Balanceamento',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={'style': "width: 310px"}
        )
    )
    servicedownaction = forms.ChoiceField(
        label=u'Action on ServiceDown',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={'style': "width: 310px"}
        )
    )
