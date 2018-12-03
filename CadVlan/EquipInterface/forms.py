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
from CadVlan.Util.utility import check_regex
from CadVlan.settings import PATCH_PANEL_ID


class ConnectForm(forms.Form):

    def __init__(self, equipment, interf_list, *args, **kwargs):
        super(ConnectForm, self).__init__(*args, **kwargs)

        front_choices = []
        back_choices = []
        attrs = dict()

        front_choices.append(("", "Selecione"))
        back_choices.append(("", "Selecione"))

        if equipment['id_tipo_equipamento'] == str(PATCH_PANEL_ID):
            for interf in interf_list:
                if interf["ligacao_front"] == None:
                    front_choices.append((interf['id'], interf['interface']))
                if interf['ligacao_back'] == None:
                    back_choices.append((interf['id'], interf['interface']))
        else:
            attrs["style"] = "display: none;"
            for interf in interf_list:
                if interf["ligacao_front"] == None:
                    front_choices.append((interf['id'], interf['interface']))

        if len(front_choices) == 1:
            front_choices = [("", "Nenhuma interface disponível")]
        if len(back_choices) == 1:
            back_choices = [("", "Nenhuma interface disponível")]

        self.fields['front'].choices = front_choices
        self.fields['back'].widget = forms.Select(attrs=attrs)
        self.fields['back'].choices = back_choices

    front = forms.ChoiceField(
        label="", required=False, error_messages=error_messages)
    back = forms.ChoiceField(
        label="", required=False, error_messages=error_messages)
    equip_name = forms.CharField(
        widget=forms.HiddenInput(), label='', required=False)
    equip_id = forms.IntegerField(
        widget=forms.HiddenInput(), label='', required=False)

    def clean_back(self):
        front = self.cleaned_data.get("front")
        back = self.cleaned_data.get("back")

        if not len(front) == 0 and not len(back) == 0:
            # Only one must be filled
            raise forms.ValidationError("Preencha apenas um: Front ou Back")

        elif len(front) == 0 and len(back) == 0:
            # Only one must be filled
            raise forms.ValidationError(
                "Preencha pelo menos um: Front ou Back")

        return self.cleaned_data.get("back")


class ConnectFormV3(forms.Form):

    def __init__(self, equipment, interf_list, *args, **kwargs):
        super(ConnectFormV3, self).__init__(*args, **kwargs)

        front_choices = list()
        back_choices = list()
        attrs = dict()

        front_choices.append(("", "Selecione"))
        back_choices.append(("", "Selecione"))

        if equipment['equipment_type'] == str(PATCH_PANEL_ID):
            for interf in interf_list:
                if not interf["front_interface"]:
                    front_choices.append((interf['id'], interf['interface']))
                if not interf['ligacao_back']:
                    back_choices.append((interf['id'], interf['interface']))
        else:
            attrs["style"] = "display: none;"
            for interf in interf_list:
                if not interf["front_interface"]:
                    front_choices.append((interf['id'], interf['interface']))

        if not front_choices:
            front_choices = [("", "Nenhuma interface disponível")]
        if not back_choices:
            back_choices = [("", "Nenhuma interface disponível")]

        self.fields['front'].choices = front_choices
        self.fields['back'].widget = forms.Select(attrs=attrs)
        self.fields['back'].choices = back_choices

    front = forms.ChoiceField(
        label="", required=False, error_messages=error_messages)
    back = forms.ChoiceField(
        label="", required=False, error_messages=error_messages)
    equip_name = forms.CharField(
        widget=forms.HiddenInput(), label='', required=False)
    equip_id = forms.IntegerField(
        widget=forms.HiddenInput(), label='', required=False)

    def clean_back(self):
        front = self.cleaned_data.get("front")
        back = self.cleaned_data.get("back")

        if not len(front) == 0 and not len(back) == 0:
            # Only one must be filled
            raise forms.ValidationError("Preencha apenas um: Front ou Back")

        elif len(front) == 0 and len(back) == 0:
            # Only one must be filled
            raise forms.ValidationError(
                "Preencha pelo menos um: Front ou Back")

        return self.cleaned_data.get("back")

class AddInterfaceForm(forms.Form):

    def __init__(self, int_type_list, marca, index, *args, **kwargs):
        super(AddInterfaceForm, self).__init__(*args, **kwargs)

        attrs = dict()
        if marca == "3":
            attrs["onChange"] = "javascript:setMask(" + str(index) + ")"
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [
                ("", "Selecione"), ("Eth","Eth"), ("Fa", "Fa"), ("Gi", "Gi"), ("mgmt", "mgmt"), ("Serial", "Serial"), ("Te", "Te")]
        elif marca == "21":
            attrs["onChange"] = "javascript:setMask(" + str(index) + ")"
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [
                ("", "Selecione"), ("GE","GE"), ("10GE", "10GE"), ("40GE", "40GE"), ("100GE", "100GE"), ("meth", "meth")]
        elif marca == "8":
            attrs["onChange"] = "javascript:setMask(" + str(index) + ")"
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [
                ("", "Selecione"), ("For", "For"), ("Ten","Ten"), ("Twe", "Twe")]
        else:
            attrs["style"] = "display: none;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("", "")]

        widget = forms.TextInput(attrs={"style": "width: 100px;"})
        self.fields['name'].widget = widget


    combo = forms.ChoiceField(label="", required=False, error_messages=error_messages)
    name = forms.CharField(label="Nome da Interface", required=True, error_messages=error_messages, min_length=1, max_length=30)
    description = forms.CharField(label=u'Descrição', required=False, min_length=3, max_length=200, error_messages=error_messages)
    protected = forms.ChoiceField(label="Protegido", required=True, choices=[(0, "Não"), (1, "Sim")], error_messages=error_messages,
                                  widget=forms.RadioSelect, initial=0)
    equip_name = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    equip_id = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    inter_id = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    int_type = forms.ChoiceField(label="Tipo de Interface", required=True, choices=[(0, "Access"), (1, "Trunk")], error_messages=error_messages,
                                  widget=forms.RadioSelect, initial=0)
    vlan = forms.CharField(label="Numero da Vlan Nativa", required=False, error_messages=error_messages, min_length=1, max_length=5)
    channel = forms.CharField(widget=forms.HiddenInput(), label='', required=False)

    def clean_type(self):
        int_type = self.cleaned_data['int_type']
        if int_type:
            self.cleaned_data['int_type'] = "access"
        else:
            self.cleaned_data['int_type'] = "trunk"

        return self.cleaned_data['int_type']

class AddEnvInterfaceForm(forms.Form):

    def __init__(self, envs, *args, **kwargs):
        super(AddEnvInterfaceForm, self).__init__(*args, **kwargs)

        ambiente_choice = ([(env['id'], env["divisao_dc_name"] + " - " + env["ambiente_logico_name"] + " - " +
                         env["grupo_l3_name"] + " ( " + env["range"] + " ) ")  for env in envs["ambiente"]])
        self.fields['environment'].choices = ambiente_choice

    environment = forms.ChoiceField(label="Ambiente (Range Permitido de Vlans)", required=True, widget=forms.Select(
                                    attrs={'style': "width: 400px"}), error_messages=error_messages)
    vlans = forms.CharField(label="Defina o range de vlans:", required=False, error_messages=error_messages, min_length=1,
                            max_length=200)

class EnvInterfaceForm(forms.Form):

    def __init__(self, envs, *args, **kwargs):
        super(EnvInterfaceForm, self).__init__(*args, **kwargs)

        ambiente_choice = ([(env['id'], env["divisao_dc_name"] + " - " + env["ambiente_logico_name"] + " - " +
                         env["grupo_l3_name"] + " ( " + env["range"] + " ) ")  for env in envs["ambiente"]])
        self.fields['environment'].choices = ambiente_choice

    environment = forms.MultipleChoiceField(label="Ambiente (Range Permitido de Vlans)", required=True, widget=forms.SelectMultiple(
                                    attrs={'style': "width: 400px"}), error_messages=error_messages)

class AddSeveralInterfaceForm(forms.Form):

    def __init__(self, marca, *args, **kwargs):
        super(AddSeveralInterfaceForm, self).__init__(*args, **kwargs)

        attrs = dict()
        attrs["onChange"] = "javascript:showHideInput()"
        self.fields['campos'].widget = forms.Select(attrs=attrs)

        attrs = dict()
        if marca == "3":
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [
                ("Fa", "Fa"), ("Gi", "Gi"), ("Te", "Te"), ("Serial", "Serial"), ("Eth","Eth")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [
                ("Fa", "Fa"), ("Gi", "Gi"), ("Te", "Te"), ("Serial", "Serial"), ("Eth","Eth")]
            self.regex = "^(Fa|Gi|Te|Serial|Eth)[0-9]+(/[0-9]+(/[0-9]+)?)?$"
            self.fields['campos'].choices = [
                ("1", "1"), ("2", "2"), ("3", "3")]
  
        elif marca == "2":
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.regex = "^(Int)\s[0-9]+$"
            self.fields['campos'].choices = [("1", "1")]
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("Int", "Int")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [("Int", "Int")]

        elif marca == "4":
            self.regex = "^(interface)\s[0-9]+(.[0-9]+)?$"
            self.fields['campos'].choices = [("1", "1"), ("2", "2")]
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("interface", "interface")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [("interface", "interface")]
        elif marca == "5":
            self.regex = "^(eth)[0-9]+(/[0-9]+)?$"
            self.fields['campos'].choices = [("1", "1"), ("2", "2")]
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("eth", "eth")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [("eth", "eth")]
        elif marca == "6":
            self.regex = "^(Hu|Fi|Fo|Tf|Te|Gi)\s+[0-9]+(/[0-9]+(/[0-9]+(/[0-9]+)?)?)?$"
            self.fields['campos'].choices = [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")]
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("Hu", "Hu"),("Fi", "Fi"),("Fo", "Fo"),("Tf", "Tf"),("Te", "Te"),("Gi", "Gi")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [("Hu", "Hu"),("Fi", "Fi"),("Fo", "Fo"),("Tf", "Tf"),("Te", "Te"),("Gi", "Gi")]

        elif marca == "21":
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [
                ("GE","GE"), ("10GE", "10GE"), ("40GE", "40GE"), ("100GE", "100GE")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [
                ("GE","GE"), ("10GE", "10GE"), ("40GE", "40GE"), ("100GE", "100GE")]
            self.regex = "^(GE|10GE|40GE|100GE|meth)\s+[0-9]+(/[0-9]+(/[0-9]+)?)?$"
            self.fields['campos'].choices = [
                ("1", "1"), ("2", "2"), ("3", "3")]

    campos = forms.ChoiceField(
        label="Campos", required=False, error_messages=error_messages)
    combo = forms.ChoiceField(
        label="", required=False, error_messages=error_messages)
    combo_aux = forms.ChoiceField(
        label="", required=False, error_messages=error_messages)
    name = forms.CharField(label="", required=True, min_length=3,
                           max_length=20, error_messages=error_messages, widget=forms.HiddenInput())
    last_piece_name = forms.IntegerField(
        label="", required=True,  error_messages=error_messages, widget=forms.HiddenInput())
    last_piece_name2 = forms.IntegerField(
        label="", required=True,  error_messages=error_messages, widget=forms.HiddenInput())
    description = forms.CharField(label=u'Descrição', required=False, min_length=3, max_length=200, error_messages=error_messages, widget=forms.Textarea(
        attrs={'style': "width: 250px", 'rows': 2, 'data-maxlenght': 200}))
    protected = forms.ChoiceField(label="Protegido", required=True, choices=[(
        0, "Não"), (1, "Sim")], error_messages=error_messages, widget=forms.RadioSelect, initial=0)
    equip_name = forms.CharField(
        widget=forms.HiddenInput(), label='', required=False)
    equip_id = forms.IntegerField(
        widget=forms.HiddenInput(), label='', required=False)
    inter_id = forms.IntegerField(
        widget=forms.HiddenInput(), label='', required=False)

class EditForm(forms.Form):


    def __init__(self, int_type_list, marca, index, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)

        attrs = dict()
        if marca == "3":
            attrs["onChange"] = "javascript:setMask(" + str(index) + ")"
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [
                ("", "Selecione"), ("Eth","Eth"), ("Fa", "Fa"), ("Gi", "Gi"), ("mgmt", "mgmt"), ("Serial", "Serial"), ("Te", "Te")]
        elif marca == "21":
            attrs["onChange"] = "javascript:setMask(" + str(index) + ")"
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [
                ("", "Selecione"), ("GE","GE"), ("10GE", "10GE"), ("40GE", "40GE"), ("100GE", "100GE"), ("meth", "meth")]
        elif marca == "8":
            attrs["onChange"] = "javascript:setMask(" + str(index) + ")"
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [
                ("", "Selecione"), ("For", "For"), ("Ten","Ten"), ("Twe", "Twe")]
        else:
            attrs["style"] = "display: none;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("", "")]

        widget = forms.TextInput(attrs={"style": "width: 100px;", "readonly": True})
        self.fields['name'].widget = widget

    combo = forms.ChoiceField(label="", required=False, error_messages=error_messages)
    name = forms.CharField(label="Nome da Interface", required=True, error_messages=error_messages, min_length=1, max_length=30)
    protected = forms.ChoiceField(label="Protegido", required=True, choices=[(0, "Não"), (1, "Sim")], error_messages=error_messages,
                                  widget=forms.RadioSelect(attrs={'disabled': 'disabled'}), initial=0)
    equip_name = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    equip_id = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    inter_id = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    front = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    back = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    channel = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    type = forms.CharField(widget=forms.HiddenInput(), label='', required=False)

class ChannelAddForm(forms.Form):


    def __init__(self , equip_list, *args, **kwargs):
        super(ChannelAddForm, self).__init__(*args, **kwargs)

        widget = forms.TextInput(attrs={"style": "width: 100px;"})
        self.fields['name'].widget = widget

        equip_interface = [(tp["id"], tp["equipamento_nome"] + "   " + tp["nome"]) for tp in equip_list["interfaces"]]
        equip_interface.insert(0, (0, "Selecione uma interface para adicionar"))

        self.fields['equip_interface'].choices = equip_interface

    name = forms.CharField(label="Numero do Channel", required=True, error_messages=error_messages, min_length=1,
                           max_length=20)
    lacp = forms.ChoiceField(label="LACP", required=True, choices=[(0, "Não"), (1, "Sim")], error_messages=error_messages,
                                  widget=forms.RadioSelect(), initial=1)
    equip_interface = forms.ChoiceField(label="Equipamento/Interface", required=False, error_messages=error_messages,
                                        widget=forms.Select(attrs={'style': "width: 400px"}))
    ids = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    equip_name = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    vlan = forms.CharField(label="Numero da Vlan Nativa", required=False, error_messages=error_messages, min_length=1,
                           max_length=5)
    int_type = forms.ChoiceField(label="Tipo de Interface", required=True, choices=[(0, "Access"), (1, "Trunk")],
                                 error_messages=error_messages, widget=forms.RadioSelect)
    id = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    type = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    channel = forms.CharField(widget=forms.HiddenInput(), label='', required=False)