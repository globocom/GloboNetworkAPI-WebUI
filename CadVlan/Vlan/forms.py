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

NETWORK_IP_CHOICES = ((0, "Exato"), (1, "Sub/Super Redes"))


class SearchVlanForm(forms.Form):

    def __init__(self, environment_list, net_type_list, *args, **kwargs):
        super(SearchVlanForm, self).__init__(*args, **kwargs)

        env_choices = ([(env['id'], env["name"])
                        for env in environment_list["environments"]])
        env_choices.insert(0, (0, "-"))

        net_choices = [(net["id"], net["name"])
                       for net in net_type_list["net_type"]]
        net_choices.insert(0, (0, "-"))

        self.fields['environment'].choices = env_choices
        self.fields['net_type'].choices = net_choices

    number = forms.IntegerField(label="Número", required=False, error_messages=error_messages,
                                widget=forms.TextInput(attrs={"style": "width: 50px"}))
    name = forms.CharField(label="Nome", required=False, min_length=3, max_length=80,
                           error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 150px"}))
    iexact = forms.BooleanField(label="Buscar nomes exatos", required=False, error_messages=error_messages)
    environment = forms.ChoiceField(label="Ambiente", required=False, choices=[(0, "Selecione")],
                                    error_messages=error_messages,
                                    widget=forms.Select(attrs={"class": "select2", "style": "width: 300px"}))
    net_type = forms.ChoiceField(label="Tipo", required=False, choices=[(0, "Selecione")],
                                 error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 180px"}))
    ip_version = forms.IntegerField(label="Versão", required=True, error_messages=error_messages)
    networkv4 = forms.CharField(label="Rede IPv4", required=False, min_length=1,
                                max_length=18, error_messages=error_messages, widget=forms.HiddenInput())
    networkv6 = forms.CharField(label="Rede IPv6", required=False, min_length=1,
                                max_length=43, error_messages=error_messages, widget=forms.HiddenInput())
    subnet = forms.ChoiceField(label="Exato-Sub/Super Redes", required=False,
                               choices=NETWORK_IP_CHOICES, error_messages=error_messages,
                               widget=forms.RadioSelect, initial=0)
    acl = forms.BooleanField(label="Apenas Acls não validadas", required=False, error_messages=error_messages)

    def clean(self):
        cleaned_data = super(SearchVlanForm, self).clean()
        networkv4 = cleaned_data.get("networkv4")
        networkv6 = cleaned_data.get("networkv6")

        if networkv4 is not None and networkv6 is not None:
            if len(networkv4) > 0 and len(networkv6) > 0:
                # Only one must be filled
                raise forms.ValidationError(
                    "Preencha apenas um: Rede IPv4 ou Rede IPv6")

        return cleaned_data


class VlanForm(forms.Form):
    """ VlanForm Class
    """

    CHOICES_NETWORK = (
        ('0', 'Não'),
        ('1', 'Sim'),
    )

    def __init__(self, environment_list, *args, **kwargs):
        super(VlanForm, self).__init__(*args, **kwargs)

        env_choices = ([(env['id'], env["name"])
                        for env in environment_list["environments"]])
        env_choices.insert(0, (0, "-"))

        self.fields['environment'].choices = env_choices

    environment = forms.ChoiceField(label="Ambiente",
                                    choices=[(0, "Selecione")],
                                    error_messages=error_messages,
                                    widget=forms.Select(attrs={"class": "select2", "style": "width: 500px"}))

    name = forms.CharField(label="Nome",
                           required=True,
                           min_length=3,
                           max_length=50,
                           error_messages=error_messages,
                           widget=forms.TextInput(attrs={"style": "width: 400px"}))

    description = forms.CharField(label="Descrição",
                                  required=False,
                                  min_length=3,
                                  max_length=200,
                                  error_messages=error_messages,
                                  widget=forms.TextInput(attrs={"style": "width: 400px"}))

    vlan_number = forms.ChoiceField(label="Deseja especificar o Número da Vlan?",
                                    required=False,
                                    choices=CHOICES_NETWORK,
                                    error_messages=error_messages)

    number = forms.IntegerField(label="Número da Vlan",
                                required=False,
                                error_messages=error_messages,
                                widget=forms.TextInput(attrs={"style": "width: 80px", "maxlength": "9"}))

    apply_vlan = forms.BooleanField(widget=forms.HiddenInput(),
                                    label='',
                                    required=False)

    network_ipv4 = forms.ChoiceField(label='Adicionar rede IPv4 automaticamente',
                                     required=False,
                                     choices=CHOICES_NETWORK,
                                     widget=forms.Select())

    prefixv4 = forms.IntegerField(label="Mascara rede IPv4",
                                  required=False,
                                  error_messages=error_messages,
                                  widget=forms.TextInput(attrs={"style": "width: 80px", "maxlength": "2"}))

    network_ipv6 = forms.ChoiceField(label='Adicionar rede IPv6 automaticamente',
                                     required=False,
                                     choices=CHOICES_NETWORK,
                                     widget=forms.Select())

    prefixv6 = forms.IntegerField(label="Mascara rede IPv6",
                                  required=False,
                                  error_messages=error_messages,
                                  widget=forms.TextInput(attrs={"style": "width: 80px", "maxlength": "3"}))

    def clean_environment(self):
        if int(self.cleaned_data['environment']) <= 0:
            raise forms.ValidationError('Este campo é obrigatório')

        return self.cleaned_data['environment']


class VlanEditForm(forms.Form):
    """ VlanEditForm Class
    """

    CHOICES_NETWORK = (
        ('0', 'Não'),
        ('1', 'Sim'),
    )

    def __init__(self, environment_list, *args, **kwargs):
        super(VlanEditForm, self).__init__(*args, **kwargs)

        env_choices = ([(env['id'], env["name"])
                        for env in environment_list["environments"]])
        env_choices.insert(0, (0, "-"))

        self.fields['environment'].choices = env_choices

    environment = forms.ChoiceField(label="Ambiente",
                                    choices=[(0, "Selecione")],
                                    error_messages=error_messages,
                                    widget=forms.Select(attrs={"class": "select2", "style": "width: 500px"}))

    name = forms.CharField(label="Nome",
                           required=True,
                           min_length=3,
                           max_length=50,
                           error_messages=error_messages,
                           widget=forms.TextInput(attrs={"style": "width: 400px"}))

    description = forms.CharField(label="Descrição",
                                  required=False,
                                  min_length=3,
                                  max_length=200,
                                  error_messages=error_messages,
                                  widget=forms.TextInput(attrs={"style": "width: 400px"}))

    number = forms.IntegerField(label="Número da Vlan",
                                required=False,
                                error_messages=error_messages,
                                widget=forms.TextInput(attrs={"style": "width: 80px", "maxlength": "9"}))

    apply_vlan = forms.BooleanField(widget=forms.HiddenInput(),
                                    label='',
                                    required=False)

    def clean_environment(self):
        if int(self.cleaned_data['environment']) <= 0:
            raise forms.ValidationError('Este campo é obrigatório')

        return self.cleaned_data['environment']