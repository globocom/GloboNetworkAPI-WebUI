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


class EnvironmentVipForm(forms.Form):

    def __init__(self, script_type_list, environment_list=dict(), *args, **kwargs):
        super(EnvironmentVipForm, self).__init__(*args, **kwargs)
        self.fields['option_vip'].choices = [
            (st['id'], st['tipo_opcao'] + " - " + st['nome_opcao_txt'])
            for st in script_type_list["option_vip"]]
        self.fields['environment'].choices = [
            (environment['id'],
             environment['name'])
            for environment in environment_list["environments"]]

    id = forms.IntegerField(
        label="",
        required=False,
        widget=forms.HiddenInput(),
        error_messages=error_messages
    )

    finality = forms.CharField(
        label=u'Finalidade',
        min_length=3,
        max_length=50,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 300px"})
    )

    client = forms.CharField(
        label=u'Cliente',
        min_length=3,
        max_length=50,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 300px"})
    )

    environment_p44 = forms.CharField(
        label=u'Ambiente P44',
        min_length=3,
        max_length=50,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 300px"})
    )

    description = forms.CharField(
        label=u'Descrição',
        min_length=3,
        max_length=50,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 300px"})
    )

    option_vip = forms.MultipleChoiceField(
        label=u'Opções VIP',
        required=False,
        error_messages=error_messages,
        widget=forms.SelectMultiple(attrs={'style': "width: 310px"})
    )

    environment = forms.MultipleChoiceField(
        label=u'Ambientes',
        required=False,
        error_messages=error_messages,
        widget=forms.SelectMultiple(attrs={'style': "width: 310px"})
    )


class ConfValidationEnvironmentVipForm(forms.Form):

    CONF_OPER = (("eq", "EQ"), ("ne", "NE"))
    CONF_TYPE = (
        ("optionvip", "Opção Vip")
    )
    CONF_VARIABLE = (
        ("persistence", "Persistência"),
        ("traffic_return", "Retorno de Trafego")
    )

    def __init__(self, forms_aux, *args, **kwargs):
        super(ConfValidationEnvironmentVipForm, self).__init__(*args, **kwargs)

        if forms_aux.get('value'):
            self.fields['value'].choices = \
                [(env['tipo_opcao'], env["tipo_opcao"]) for env in forms_aux["value"]]

    type = forms.ChoiceField(
        label="Tipo de Dado",
        required=True,
        choices=CONF_TYPE,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "width: 300px",
                'class': 'select2'
            }
        )
    )

    variable = forms.ChoiceField(
        label="Variável",
        required=True,
        choices=CONF_VARIABLE,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "width: 300px",
                'class': 'select2'
            }
        )
    )

    operator = forms.ChoiceField(
        label="Operador",
        required=True,
        choices=CONF_OPER,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "width: 300px",
                'class': 'select2'
            }
        )
    )
    value = forms.ChoiceField(
        label="Valor",
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "width: 300px",
                'class': 'select2'
            }
        )
    )


class ConfUseEnvironmentVipForm(forms.Form):
    CONF_TYPE = (
        ("profile", "Profile"),
        ("translate_port_state", "Translate Port"),
        ("persistence", "Persistência")
    )

    type = forms.ChoiceField(
        label="Tipo de Dado",
        required=True,
        choices=CONF_TYPE,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "width: 300px",
                'class': 'select2'
            }
        )
    )

    value = forms.CharField(
        label=u'Valor',
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 300px"})
    )
