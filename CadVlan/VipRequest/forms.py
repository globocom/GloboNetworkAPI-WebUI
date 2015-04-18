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


from CadVlan.Net.business import is_valid_ipv4, is_valid_ipv6
from CadVlan.Util.utility import validates_dict
from CadVlan.Util.forms.customRenderer import RadioCustomRenderer
from CadVlan.Util.forms.decorators import autostrip
from CadVlan.messages import error_messages, request_vip_messages
from django import forms
from django.contrib import messages


class SearchVipRequestForm(forms.Form):

    id_request = forms.IntegerField(label="Id Requisição", required=False,
                                    error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 40px"}))
    ipv4 = forms.CharField(label="IPv4", required=False, min_length=1,
                           max_length=15, error_messages=error_messages, widget=forms.HiddenInput())
    ipv6 = forms.CharField(label="IPv6", required=False, min_length=1,
                           max_length=39, error_messages=error_messages, widget=forms.HiddenInput())
    vip_create = forms.BooleanField(
        label="Buscar apenas vips criados", required=False, error_messages=error_messages)

    def clean(self):
        cleaned_data = super(SearchVipRequestForm, self).clean()
        ipv4 = cleaned_data.get("ipv4")
        ipv6 = cleaned_data.get("ipv6")

        if ipv4 != None and ipv6 != None:
            if len(ipv4) > 0 and len(ipv6) > 0:
                # Only one must be filled
                raise forms.ValidationError("Preencha apenas um: IPv4 ou IPv6")

        return cleaned_data


@autostrip
class RequestVipFormInputs(forms.Form):

    business = forms.CharField(label=u'Área de negócio', min_length=3, max_length=100, required=True,
                               error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    service = forms.CharField(label=u'Nome do serviço', min_length=3, max_length=100, required=True,
                              error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    name = forms.CharField(label=u'Nome do VIP (Host FQDN)', min_length=3, max_length=100, required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    filter_l7 = forms.CharField(label=u'Filtro L7', required=False, error_messages=error_messages, widget=forms.Textarea(
        attrs={'style': "width: 300px", 'rows': 10}))
    created = forms.BooleanField(
        label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    validated = forms.BooleanField(
        label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)


@autostrip
class RequestVipFormEnvironment(forms.Form):

    def __init__(self, finality_list, finality=None, client=None, environment=None, client_api=None, *args, **kwargs):
        super(RequestVipFormEnvironment, self).__init__(*args, **kwargs)
        self.fields['finality'].choices = [
            (st['finality'], st['finality']) for st in finality_list]

        if finality is not None and client is not None:

            client_evip = client_api.create_environment_vip()

            clients = validates_dict(
                client_evip.buscar_cliente_por_finalidade(finality), 'cliente_txt')
            self.fields['client'].choices = [
                (st['cliente_txt'], st['cliente_txt']) for st in clients]

            if environment is not None:

                environments = validates_dict(client_evip.buscar_ambientep44_por_finalidade_cliente(
                    finality, client), 'ambiente_p44')
                self.fields['environment'].choices = [
                    (st['ambiente_p44'], st['ambiente_p44']) for st in environments]

    finality = forms.ChoiceField(label=u'Finalidade', required=True,
                                 error_messages=error_messages, widget=forms.RadioSelect(renderer=RadioCustomRenderer))
    client = forms.ChoiceField(label=u'Cliente', required=True,
                               error_messages=error_messages, widget=forms.RadioSelect(renderer=RadioCustomRenderer))
    environment = forms.ChoiceField(
        label=u'Ambiente', required=True, error_messages=error_messages, widget=forms.RadioSelect(renderer=RadioCustomRenderer))
    environment_vip = forms.IntegerField(
        label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)


@autostrip
class RequestVipFormOptions(forms.Form):

    def __init__(self, request=None, environment_vip=None, client=None, vip_id=None, *args, **kwargs):
        super(RequestVipFormOptions, self).__init__(*args, **kwargs)

        if environment_vip is not None and environment_vip != '':

            client_ovip = client.create_option_vip()

            timeouts = validates_dict(
                client_ovip.buscar_timeout_opcvip(environment_vip), 'timeout_opt')
            if timeouts is not None:
                self.fields['timeout'].choices = [
                    (st['timeout_opt'], st['timeout_opt']) for st in timeouts]
            else:
                if 'initial' in kwargs:
                    timeout = kwargs.get('initial').get(
                        'timeout') if "timeout" in kwargs.get('initial') else ''
                    messages.add_message(request, messages.ERROR, request_vip_messages.get(
                        "error_existing_timeout") % timeout)

            gcaches = validates_dict(
                client_ovip.buscar_grupo_cache_opcvip(environment_vip), 'grupocache_opt')
            if timeouts is not None:
                self.fields['caches'].choices = [
                    (st['grupocache_opt'], st['grupocache_opt']) for st in gcaches]
            else:
                if 'initial' in kwargs:
                    caches = kwargs.get('initial').get(
                        'caches') if "caches" in kwargs.get('initial') else ''
                    messages.add_message(request, messages.ERROR, request_vip_messages.get(
                        "error_existing_cache") % caches)

            persistences = validates_dict(
                client_ovip.buscar_persistencia_opcvip(environment_vip), 'persistencia_opt')
            if persistences is not None:
                self.fields['persistence'].choices = [
                    (st['persistencia_opt'], st['persistencia_opt']) for st in persistences]
            else:
                if 'initial' in kwargs:
                    persistence = kwargs.get('initial').get(
                        'persistence') if "persistence" in kwargs.get('initial') else ''
                    messages.add_message(request, messages.ERROR, request_vip_messages.get(
                        "error_existing_persistence") % persistence)

            rules = validates_dict(
                client_ovip.buscar_rules(environment_vip, vip_id),
                'name_rule_opt'
            )

            if rules is not None:
                self.fields['rules'].choices = [(st['id'] if st['id'] != None else '', st[
                                                 'name_rule_opt'] if st['name_rule_opt'] != None else '') for st in rules]
            else:
                if 'initial' in kwargs:
                    rules = kwargs.get('initial').get('rules') if "rules" in kwargs.get('initial') else ''
                    messages.add_message(request, messages.ERROR, "Existing Rule")

    timeout = forms.ChoiceField(label="Timeout", required=True, error_messages=error_messages, widget=forms.Select(
        attrs={"style": "width: 300px"}))
    caches = forms.ChoiceField(label="Grupos de caches", required=True,
                               error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 300px"}))
    persistence = forms.ChoiceField(
        label="Persistência", required=True, error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 300px"}))

    rules = forms.ChoiceField(label=u'Regras', required=False, error_messages=error_messages, widget=forms.Select(
        attrs={"style": "width: 300px"}))


@autostrip
class RequestVipFormHealthcheck(forms.Form):

    def __init__(self, healthcheck_list, healthcheck_options, *args, **kwargs):
        super(RequestVipFormHealthcheck, self).__init__(*args, **kwargs)
        self.fields['excpect'].choices = [
            (st['id'], st['expect_string']) for st in healthcheck_list]
        self.fields['healthcheck_type'].choices = [
            (healthcheck['name'], healthcheck['name']) for healthcheck in healthcheck_options]

    healthcheck_type = forms.ChoiceField(
        label=u'Healthcheck', required=True, error_messages=error_messages, widget=forms.RadioSelect(renderer=RadioCustomRenderer))
    healthcheck = forms.CharField(label=u'Healthcheck', min_length=3, max_length=100, required=False,
                                  error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    excpect = forms.ChoiceField(label=u'HTTP Expect String', required=True,
                                error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 185px"}))
    excpect_new = forms.CharField(
        label=u'', required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 185px"}))

    def clean(self):
        cleaned_data = self.cleaned_data

        healthcheck_type = cleaned_data.get("healthcheck_type")
        healthcheck = cleaned_data.get("healthcheck")

        if healthcheck_type == 'HTTP':
            if healthcheck == "":
                self._errors["healthcheck"] = self.error_class(
                    ["Este campo é obrigatório com a opção HTTP selecionada."])
        else:
            cleaned_data["excpect"] = None
            cleaned_data["healthcheck"] = None

        return cleaned_data


@autostrip
class HealthcheckForm(forms.Form):

    excpect_new = forms.CharField(label=u'', min_length=3, max_length=100, required=True,
                                  error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 185px"}))


@autostrip
class RequestVipFormReal(forms.Form):

    equip_name = forms.CharField(label=u'Buscar novo', min_length=3, required=False, widget=forms.TextInput(
        attrs={'style': "width: 250px;", 'autocomplete': "off"}), error_messages=error_messages)

    maxcom = forms.IntegerField(label=u'Número máximo de conexões (maxconn)', required=True,
                                error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 231px"}))

@autostrip
class RequestVipFormIP(forms.Form):

    CHOICES = (('0', 'Alocar automaticamente'), ('1', 'Especificar IP'))

    ipv4_check = forms.BooleanField(
        label=u'IPv4', required=False, error_messages=error_messages)
    ipv4_type = forms.ChoiceField(
        label=u'', required=False, error_messages=error_messages, choices=CHOICES, widget=forms.RadioSelect())
    ipv4_specific = forms.CharField(
        label=u'', required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 231px"}))

    ipv6_check = forms.BooleanField(
        label=u'IPv6', required=False, error_messages=error_messages)
    ipv6_type = forms.ChoiceField(
        label=u'', required=False, error_messages=error_messages, choices=CHOICES, widget=forms.RadioSelect())
    ipv6_specific = forms.CharField(
        label=u'', required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 231px"}))

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
                            ["Ip não informado ou informado de forma incorreta. IPv4 deve ser informado no formato xxx.xxx.xxx.xxx"])

            if ipv6_check:

                ipv6_type = cleaned_data.get("ipv6_type")
                ipv6_specific = cleaned_data.get("ipv6_specific")

                if ipv6_type == '1' and ipv6_specific is None:
                    self._errors["ipv6_specific"] = self.error_class(
                        ["Este campo é obrigatório com a opção Especificar IP selecionada."])

                elif ipv6_type == '1' and ipv6_specific is not None:
                    if not is_valid_ipv6(ipv6_specific):
                        self._errors["ipv6_specific"] = self.error_class(
                            ["Ip não informado ou informado de forma incorreta. IPv6 deve ser informado no formato xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx"])

        return cleaned_data


@autostrip
class GenerateTokenForm(forms.Form):

    user = forms.CharField(required=True)
    requestVip = forms.CharField(required=False)
    p = forms.CharField(required=False)
    is_ldap_user = forms.BooleanField(required=False)


@autostrip
class FilterL7Form(forms.Form):
    filter_applied = forms.CharField(label=u'Filtro L7 atual',
                                     required=False, error_messages=error_messages,
                                     widget=forms.Textarea(attrs={'style': "width: 300px",
                                                                  'rows': 10, 'disabled': 'disabled'}))
    filter_l7 = forms.CharField(label=u'Novo Filtro L7 a ser aplicado',
                                required=False, error_messages=error_messages,
                                widget=forms.Textarea(attrs={'style': "width: 300px",
                                                             'rows': 10}))
    filter_rollback = forms.CharField(label=u'Rollback (última configuração válida)',
                                      required=False, error_messages=error_messages,
                                      widget=forms.Textarea(attrs={'style': "width: 300px",
                                                                   'rows': 10, 'disabled': 'disabled'}))


@autostrip
class RuleForm(forms.Form):

    def __init__(self, rules, *args, **kwargs):
        super(RuleForm, self).__init__(*args, **kwargs)
        self.fields['rules'].choices = [(st['id'] if st['id'] != None else '', st[
                                         'name_rule_opt'] if st['name_rule_opt'] != None else '') for st in rules]

    rules = forms.ChoiceField(label=u'Regras', required=False, error_messages=error_messages, widget=forms.Select(
        attrs={"style": "width: 300px"}))


class VipPoolForm(forms.Form):

    def __init__(self, pools_choice, *args, **kwargs):
        super(VipPoolForm, self).__init__(*args, **kwargs)
        pools_choice.insert(0, (0, "-"))
        self.fields['pools'].choices = pools_choice

    pools = forms.ChoiceField(
        label=u'Pools',
        required=False,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={
                "style": "width: 300px",
            }
        )
    )


class ServerPoolForm(forms.Form):

    def __init__(self, choices_opvip, *args, **kwargs):
        super(ServerPoolForm, self).__init__(*args, **kwargs)

        self.fields['balancing'].choices = choices_opvip

    identifier = forms.CharField(
        label=u'Identifier',
        min_length=3,
        max_length=40,
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

    balancing = forms.ChoiceField(
        label=u'Balanceamento',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(
            attrs={'style': "width: 310px"}
        )
    )


class PoolForm(forms.Form):

    def __init__(self, enviroments_choices, optionsvips_choices, healthcheck_choices, *args, **kwargs):
        super(PoolForm, self).__init__(*args, **kwargs)

        self.fields['environment'].choices = enviroments_choices
        self.fields['balancing'].choices = optionsvips_choices
        self.fields['health_check'].choices = healthcheck_choices

    identifier = forms.CharField(
        label=u'Identifier',
        min_length=3,
        max_length=40,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 300px"})
    )

    default_port = forms.CharField(
        label=u'Default Port',
        min_length=2,
        max_length=5,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 100px"})
    )

    environment = forms.ChoiceField(
        label=u'Environment',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={'style': "width: 310px"})
    )

    balancing = forms.ChoiceField(
        label=u'Balanceamento',
        choices=[],
        required=True,
        error_messages=error_messages,
        widget=forms.Select(attrs={'style': "width: 310px"})
    )

    health_check = forms.ChoiceField(
        label=u'HealthCheck',
        choices=[],
        required=False,
        error_messages=error_messages,
        widget=forms.Select(attrs={'style': "width: 310px"})
    )

    maxcom = forms.IntegerField(
        label=u'Número máximo de conexões (maxconn)',
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(attrs={'style': "width: 231px"})
    )
