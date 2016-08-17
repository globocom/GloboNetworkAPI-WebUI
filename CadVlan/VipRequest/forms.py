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
import logging

from django import forms

from CadVlan.messages import error_messages
from CadVlan.Net.business import is_valid_ipv4
from CadVlan.Net.business import is_valid_ipv6
from CadVlan.Util.forms import fields
from CadVlan.Util.forms.decorators import autostrip


@autostrip
class GenerateTokenForm(forms.Form):

    user = forms.CharField(required=True)
    requestVip = forms.CharField(required=False)
    p = forms.CharField(required=False)
    is_ldap_user = forms.BooleanField(required=False)


@autostrip
class PoolForm(forms.Form):

    def __init__(self, enviroments_choices, optionsvips_choices,
                 servicedownaction_choices, *args, **kwargs):
        super(PoolForm, self).__init__(*args, **kwargs)

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

    default_port = forms.CharField(
        label=u'Default Port',
        min_length=2,
        max_length=5,
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
        widget=forms.Select(attrs={
            "style": "",
            "style": "width: 310px",
            'class': 'select2'}
        )
    )

    balancing = forms.ChoiceField(
        label=u'Balanceamento',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 310px",
            'class': 'select2'}
        )
    )

    servicedownaction = forms.ChoiceField(
        label=u'Action on ServiceDown',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
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
class PoolHealthcheckForm(forms.Form):

    def __init__(self, healthcheck_choices=[], *args, **kwargs):
        super(PoolHealthcheckForm, self).__init__(*args, **kwargs)

        self.fields['healthcheck'].choices = healthcheck_choices

    healthcheck = forms.ChoiceField(
        label=u'HealthCheck',
        choices=[],
        required=False,
        error_messages=error_messages,
        widget=forms.Select(attrs={
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
                "style": "width: 310px"}
        )
    )

    healthcheck_destination = forms.CharField(
        label=u'Porta',
        max_length=5,
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                "style": "width: 100px"}
        )
    )


@autostrip
class RequestVipBasicForm(forms.Form):

    def __init__(self, forms_aux, *args, **kwargs):
        super(RequestVipBasicForm, self).__init__(*args, **kwargs)

    business = forms.CharField(
        label=u'Área de negócio',
        min_length=3,
        max_length=100,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 300px"}))

    service = forms.CharField(
        label=u'Nome do serviço',
        min_length=3,
        max_length=100,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 300px"}))

    name = forms.CharField(
        label=u'Nome do VIP (Host FQDN)',
        min_length=3,
        max_length=100,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 300px"}))

    created = forms.BooleanField(
        label="",
        required=False,
        widget=forms.HiddenInput(),
        error_messages=error_messages)


@autostrip
class RequestVipEnvironmentVipForm(forms.Form):

    def __init__(self, forms_aux, *args, **kwargs):
        super(RequestVipEnvironmentVipForm, self).__init__(*args, **kwargs)

        if forms_aux.get('finalities'):
            self.fields['step_finality'].choices = \
                [(env['finalidade_txt'], env["finalidade_txt"]) for env in forms_aux["finalities"]]
            self.fields['step_finality'].choices.insert(0, ('', ''))

        if forms_aux.get('clients'):
            self.fields['step_client'].choices = \
                [(env['cliente_txt'], env["cliente_txt"]) for env in forms_aux["clients"]]
            self.fields['step_client'].choices.insert(0, ('', ''))

        if forms_aux.get('environments'):
            self.fields['step_environment'].choices = \
                [(env['ambiente_p44_txt'], {
                    'label': env["ambiente_p44_txt"],
                    'attrs':{'attr': env["id"]}
                }) for env in forms_aux["environments"]]
            self.fields['step_environment'].choices.insert(0, ('', ''))

    step_finality = forms.ChoiceField(
        label=u'Finalidade',
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2'}))

    step_client = forms.ChoiceField(
        label=u'Cliente',
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2'}))

    step_environment = forms.ChoiceField(
        label=u'Ambiente',
        required=True,
        error_messages=error_messages,
        widget=fields.SelectWithAttr(attrs={
            "style": "width: 300px",
            'class': 'select2'}))

    environment_vip = forms.IntegerField(
        label="",
        required=False,
        widget=forms.HiddenInput(),
        error_messages=error_messages)


@autostrip
class RequestVipOptionVipForm(forms.Form):

    logger = logging.getLogger(__name__)

    def __init__(self, forms_aux, *args, **kwargs):
        super(RequestVipOptionVipForm, self).__init__(*args, **kwargs)

        if forms_aux.get('timeout'):
            self.fields['timeout'].choices = \
                [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["timeout"]]

        if forms_aux.get('caches'):
            self.fields['caches'].choices = \
                [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["caches"]]

        if forms_aux.get('persistence'):
            self.fields['persistence'].choices = \
                [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["persistence"]]

        if forms_aux.get('trafficreturn'):
            self.fields['trafficreturn'].choices = \
                [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["trafficreturn"]]

    timeout = forms.ChoiceField(
        label="Timeout",
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2'}))

    caches = forms.ChoiceField(
        label="Grupos de caches",
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2'}))

    persistence = forms.ChoiceField(
        label="Persistência",
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2'}))

    trafficreturn = forms.ChoiceField(
        label="Traffic Return",
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2'}))


@autostrip
class RequestVipOptionVipEditForm(forms.Form):

    logger = logging.getLogger(__name__)

    def __init__(self, forms_aux, *args, **kwargs):
        super(RequestVipOptionVipEditForm, self).__init__(*args, **kwargs)

        if forms_aux.get('timeout'):
            self.fields['timeout'].choices = \
                [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["timeout"]]

        if forms_aux.get('caches'):
            self.fields['caches'].choices = \
                [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["caches"]]

        if forms_aux.get('persistence'):
            self.fields['persistence'].choices = \
                [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["persistence"]]

        if forms_aux.get('trafficreturn'):
            self.fields['trafficreturn'].choices = \
                [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["trafficreturn"]]

    timeout = forms.ChoiceField(
        label="Timeout",
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2'}))

    caches = forms.ChoiceField(
        label="Grupos de caches",
        required=False,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2',
            "readonly": "true"}))

    persistence = forms.ChoiceField(
        label="Persistência",
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2'}))

    trafficreturn = forms.ChoiceField(
        label="Traffic Return",
        required=False,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2',
            "readonly": "true"}))


class RequestVipPortOptionVipForm(forms.Form):

    logger = logging.getLogger(__name__)

    def __init__(self, forms_aux, *args, **kwargs):
        super(RequestVipPortOptionVipForm, self).__init__(*args, **kwargs)

        if forms_aux.get('l4_protocol'):
            self.fields['l4_protocol'].choices = [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["l4_protocol"]]
        self.fields['l4_protocol'].choices.insert(0, ('', ''))

        if forms_aux.get('l7_protocol'):
            self.fields['l7_protocol'].choices = [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["l7_protocol"]]
        self.fields['l7_protocol'].choices.insert(0, ('', ''))

        if forms_aux.get('l7_rule'):
            self.fields['l7_rule'].choices = [(env['id'], env["nome_opcao_txt"]) for env in forms_aux["l7_rule"]]
        self.fields['l7_rule'].choices.insert(0, ('', ''))

        if forms_aux.get('pools'):
            self.fields['pools'].choices = [(env['id'], env["identifier"]) for env in forms_aux["pools"]['server_pools']]
        self.fields['pools'].choices.insert(0, ('', ''))

    port_vip = forms.ChoiceField(
        label="Porta Vip",
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={
            "style": "width: 50px"}))

    l4_protocol = forms.ChoiceField(
        label="Protocolo L4",
        required=False,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 150px",
            'class': 'select2'}))

    l7_protocol = forms.ChoiceField(
        label="Protocolo L7",
        required=False,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 150px",
            'class': 'select2'}))

    l7_rule_check = forms.BooleanField(
        label=u'Tem regra de L7?', required=False, error_messages=error_messages)

    order = forms.ChoiceField(
        label="Posição do L7",
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={
            "style": "width: 50px"}))

    l7_rule = forms.ChoiceField(
        label="Tipo Regra de L7",
        required=False,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 150px",
            'class': 'select2'}))

    l7_value = forms.ChoiceField(
        label="Valor de L7",
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={
            "style": "width: 50px"}))

    pools = forms.ChoiceField(
        label=u'Pools',
        required=False,
        error_messages=error_messages,
        widget=forms.Select(attrs={
            "style": "width: 300px",
            'class': 'select2'}))


@autostrip
class RequestVipIPForm(forms.Form):

    def __init__(self, forms_aux, *args, **kwargs):
        super(RequestVipIPForm, self).__init__(*args, **kwargs)

    CHOICES = (('0', 'Alocar automaticamente'), ('1', 'Especificar IP'))

    ipv4_check = forms.BooleanField(
        label=u'IPv4',
        required=False,
        error_messages=error_messages)

    ipv4_type = forms.ChoiceField(
        label=u'',
        required=False,
        error_messages=error_messages,
        choices=CHOICES,
        widget=forms.RadioSelect())

    ipv4_specific = forms.CharField(
        label=u'',
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={'style': "width: 231px"}))

    ipv6_check = forms.BooleanField(
        label=u'IPv6',
        required=False,
        error_messages=error_messages)

    ipv6_type = forms.ChoiceField(
        label=u'',
        required=False,
        error_messages=error_messages,
        choices=CHOICES,
        widget=forms.RadioSelect())

    ipv6_specific = forms.CharField(
        label=u'',
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={'style': "width: 231px"}))

    def clean(self):
        cleaned_data = self.cleaned_data

        ipv4_check = cleaned_data.get("ipv4_check")
        ipv6_check = cleaned_data.get("ipv6_check")

        if not ipv4_check and not ipv6_check:
            self._errors["ipv4_check"] = self.error_class(
                ["Pelo menos uma opção de IP tem que ser selecionada"])

        else:

            if ipv4_check:

                ipv4_type = cleaned_data.get("ipv4_type")
                ipv4_specific = cleaned_data.get("ipv4_specific")

                if ipv4_type == '1' and ipv4_specific is None:
                    self._errors["ipv4_specific"] = self.error_class(
                        ["Este campo é obrigatório com a opção Especificar IP selecionada."])

                elif ipv4_type == '1' and ipv4_specific is not None:
                    if not is_valid_ipv4(ipv4_specific):
                        self._errors["ipv4_specific"] = self.error_class(
                            ["Ip não informado ou informado de forma incorreta. \
                            IPv4 deve ser informado no formato xxx.xxx.xxx.xxx"])

            if ipv6_check:

                ipv6_type = cleaned_data.get("ipv6_type")
                ipv6_specific = cleaned_data.get("ipv6_specific")

                if ipv6_type == '1' and ipv6_specific is None:
                    self._errors["ipv6_specific"] = self.error_class(
                        ["Este campo é obrigatório com a opção Especificar IP selecionada."])

                elif ipv6_type == '1' and ipv6_specific is not None:
                    if not is_valid_ipv6(ipv6_specific):
                        self._errors["ipv6_specific"] = self.error_class(
                            ["Ip não informado ou informado de forma incorreta. \
                            IPv6 deve ser informado no formato xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx"])

        return cleaned_data


class SearchVipRequestForm(forms.Form):

    id_request = forms.IntegerField(
        label="Id Requisição",
        required=False,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={"style": "width: 40px"}))

    ipv4 = forms.CharField(
        label="IPv4",
        required=False,
        min_length=1,
        max_length=15,
        error_messages=error_messages,
        widget=forms.HiddenInput())

    ipv6 = forms.CharField(
        label="IPv6",
        required=False,
        min_length=1,
        max_length=39,
        error_messages=error_messages,
        widget=forms.HiddenInput())

    vip_created = forms.BooleanField(
        label="Buscar apenas vips criados",
        required=False,
        error_messages=error_messages)

    def clean(self):
        cleaned_data = super(SearchVipRequestForm, self).clean()
        ipv4 = cleaned_data.get("ipv4")
        ipv6 = cleaned_data.get("ipv6")

        if ipv4 is not None and ipv6 is not None:
            if len(ipv4) > 0 and len(ipv6) > 0:
                # Only one must be filled
                raise forms.ValidationError("Preencha apenas um: IPv4 ou IPv6")

        return cleaned_data
