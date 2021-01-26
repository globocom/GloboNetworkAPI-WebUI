# -*- coding: utf-8 -*-
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


class SearchEquipmentForm(forms.Form):

    def __init__(self, environment_list, type_list, groups_list, *args, **kwargs):
        super(SearchEquipmentForm, self).__init__(*args, **kwargs)

        env_choices = ([(env['id'], env['name']) for env in environment_list['environments']])
        env_choices.insert(0, (0, '-'))

        type_choices = [(tp['id'], tp['nome'])
                        for tp in type_list['equipment_type']]
        type_choices.insert(0, (0, '-'))

        groups_choices = [(tp['id'], tp['nome'])
                          for tp in groups_list['grupo']]
        groups_choices.insert(0, (0, '-'))

        self.fields['environment'].choices = env_choices
        self.fields['type_equip'].choices = type_choices
        self.fields['group'].choices = groups_choices

    name = forms.CharField(label='Nome', required=False, min_length=3, max_length=80,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': 'width: 150px'}))
    iexact = forms.BooleanField(
        label='Buscar nomes exatos', required=False, error_messages=error_messages)
    environment = forms.ChoiceField(label='Ambiente', required=False, choices=[(
        0, 'Selecione')], error_messages=error_messages, widget=forms.Select(attrs={'class': 'select2', 'style': 'width: 300px'}))
    type_equip = forms.ChoiceField(label='Tipo', required=False, choices=[(
        0, 'Selecione')], error_messages=error_messages, widget=forms.Select(attrs={'style': 'width: 180px'}))
    group = forms.ChoiceField(label='Grupo', required=False, choices=[(
        0, 'Selecione')], error_messages=error_messages, widget=forms.Select(attrs={'style': 'width: 180px'}))
    ipv4 = forms.CharField(label='IPv4', required=False, min_length=1,
                           max_length=15, error_messages=error_messages, widget=forms.HiddenInput())
    ipv6 = forms.CharField(label='IPv6', required=False, min_length=1,
                           max_length=39, error_messages=error_messages, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(SearchEquipmentForm, self).clean()
        ipv4 = cleaned_data.get('ipv4')
        ipv6 = cleaned_data.get('ipv6')

        if ipv4 is not None and ipv6 is not None:
            if len(ipv4) > 0 and len(ipv6) > 0:
                # Only one must be filled
                raise forms.ValidationError('Preencha apenas um: IPv4 ou IPv6')

        return cleaned_data


class EquipForm(forms.Form):

    def __init__(self, forms_aux, *args, **kwargs):
        super(EquipForm, self).__init__(*args, **kwargs)

        marca_choices = [(m['id'], m['nome']) for m in forms_aux['marcas']]
        marca_choices.insert(0, (0, 'Selecione uma marca'))

        type_choices = [(tp['id'], tp['nome'])
                        for tp in forms_aux['tipo_equipamento']]
        type_choices.insert(0, (0, 'Selecione um tipo de Equipamento'))

        self.fields['tipo_equipamento'].choices = type_choices
        self.fields['marca'].choices = marca_choices
        self.fields['grupo'].choices = (
            [(m['id'], m['nome']) for m in forms_aux['grupos']])

        environments = [(env['id'], env['name']) for env in forms_aux['ambientes']]

        self.fields['ambiente'].choices = environments

        sdn_controlled_environment = [
            (env['id'], env['name']) for env in forms_aux['sdn_controlled_environment']]

        self.fields['sdn_controlled_environment'].choices = (
            sdn_controlled_environment)

        if forms_aux['modelos'] is not None:
            self.fields['modelo'].choices = (
                [(m['id'], m['nome']) for m in forms_aux['modelos']])

    nome = forms.CharField(label=u'Nome',
                           min_length=3,
                           max_length=50,
                           required=True,
                           error_messages=error_messages,
                           widget=forms.TextInput(
                               attrs={'style': 'width: 200px'}))
    maintenance = forms.BooleanField(
        label='Em manutencao', required=False, error_messages=error_messages)
    tipo_equipamento = forms.ChoiceField(label='Tipo equipamento',
                                         widget=forms.Select(
                                             attrs={'style': 'width: 400px'}),
                                         error_messages=error_messages)
    marca = forms.ChoiceField(label='Marca',
                              widget=forms.Select(
                                  attrs={'style': 'width: 400px'}),
                              error_messages=error_messages)
    modelo = forms.ChoiceField(label=u'Modelo',
                               widget=forms.Select(
                                   attrs={'style': 'width: 400px'}),
                               error_messages=error_messages)
    grupo = forms.MultipleChoiceField(label='Grupos Disponíveis',
                                      widget=forms.SelectMultiple(
                                          attrs={'style': 'width: 400px'}),
                                      error_messages=error_messages)
    ambiente = forms.MultipleChoiceField(label='Ambientes Disponíveis',
                                         required=False,
                                         widget=forms.SelectMultiple(
                                             attrs={'style': 'width: 400px'}),
                                         error_messages=error_messages)
    sdn_controlled_environment = forms.MultipleChoiceField(
        label='Ambientes SDN Disponíveis para Controlar',
        required=False,
        widget=forms.SelectMultiple(attrs={'style': 'width: 400px'}),
        error_messages=error_messages)

    def clean_tipo_equipamento(self):
        if int(self.cleaned_data['tipo_equipamento']) <= 0:
            raise forms.ValidationError('Este campo é obrigatório')
        return self.cleaned_data['tipo_equipamento']

    def clean_marca(self):
        if int(self.cleaned_data['marca']) <= 0:
            raise forms.ValidationError('Este campo é obrigatório')
        return self.cleaned_data['marca']

    def clean_modelo(self):
        if int(self.cleaned_data['modelo']) <= 0:
            raise forms.ValidationError('Este campo é obrigatório')
        return self.cleaned_data['modelo']


class MarcaForm(forms.Form):

    nome = forms.CharField(label='Nome da marca', required=True, min_length=3, max_length=100,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': 'width: 150px'}))


class ModeloForm(forms.Form):

    def __init__(self, marcas, *args, **kwargs):
        super(ModeloForm, self).__init__(*args, **kwargs)

        marca_choices = [(m['id'], m['nome']) for m in marcas['brand']]
        marca_choices.insert(0, (0, 'Selecione uma marca'))

        self.fields['marca'].choices = marca_choices

    marca = forms.ChoiceField(label='Marca', required=True, widget=forms.Select(
        attrs={'style': 'width: 400px'}), error_messages=error_messages)
    nome = forms.CharField(label='Nome do modelo', required=True, min_length=3, max_length=100,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': 'width: 150px'}))

    def clean_marca(self):
        if int(self.cleaned_data['marca']) <= 0:
            raise forms.ValidationError('Este campo é obrigatório')

        return self.cleaned_data['marca']
