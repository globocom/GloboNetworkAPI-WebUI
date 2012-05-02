# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class AjaxAutoCompleteForm(forms.Form):
    
    name = forms.CharField(min_length=3, max_length=40, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'autocomplete': "off"}))
    
class SearchEquipmentForm(forms.Form):
    
    def __init__(self, environment_list, type_list, groups_list, *args, **kwargs):
        super(SearchEquipmentForm, self).__init__(*args, **kwargs)
        
        env_choices = ([(env['id'], env["divisao_dc_name"] + " - " + env["ambiente_logico_name"] + " - " + env["grupo_l3_name"]) for env in environment_list["ambiente"]])
        env_choices.insert(0, (0, "-"))
        
        type_choices = [(tp["id"], tp["nome"]) for tp in type_list["tipo_equipamento"]]
        type_choices.insert(0, (0, "-"))
        
        groups_choices = [(tp["id"], tp["nome"]) for tp in groups_list["grupo"]]
        groups_choices.insert(0, (0, "-"))
        
        self.fields['environment'].choices = env_choices
        self.fields['type_equip'].choices = type_choices
        self.fields['group'].choices = groups_choices
    
    name = forms.CharField(label="Nome", required=False, min_length=3, max_length=80, error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 150px"}))
    iexact = forms.BooleanField(label="Buscar nomes exatos", required=False, error_messages=error_messages)
    environment = forms.ChoiceField(label="Ambiente", required=False, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 300px"}))
    type_equip = forms.ChoiceField(label="Tipo", required=False, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 180px"}))
    group = forms.ChoiceField(label="Grupo", required=False, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 180px"}))
    ipv4 = forms.CharField(label="IPv4", required=False, min_length=1, max_length=18, error_messages=error_messages, widget=forms.HiddenInput())
    ipv6 = forms.CharField(label="IPv6", required=False, min_length=1, max_length=43, error_messages=error_messages, widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = super(SearchEquipmentForm, self).clean()
        ipv4 = cleaned_data.get("ipv4")
        ipv6 = cleaned_data.get("ipv6")
        
        if ipv4 != None and ipv6 != None:
            if len(ipv4) > 0 and len(ipv6) > 0:
                # Only one must be filled
                raise forms.ValidationError("Preencha apenas um: IPv4 ou IPv6")
        
        return cleaned_data