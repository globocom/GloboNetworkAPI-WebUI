# -*- coding:utf-8 -*-
"""
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
"""

from django import forms
from CadVlan.messages import error_messages

NETWORK_IP_CHOICES = ((0, "Exato"), (1, "Sub/Super Redes"))

class SearchVlanForm(forms.Form):
    
    def __init__(self, environment_list, net_type_list, *args, **kwargs):
        super(SearchVlanForm, self).__init__(*args, **kwargs)
        
        env_choices = ([(env['id'], env["divisao_dc_name"] + " - " + env["ambiente_logico_name"] + " - " + env["grupo_l3_name"]) for env in environment_list["ambiente"]])
        env_choices.insert(0, (0, "-"))
        
        net_choices = [(net["id"], net["nome"]) for net in net_type_list["tipo_rede"]]
        net_choices.insert(0, (0, "-"))
        
        self.fields['environment'].choices = env_choices
        self.fields['net_type'].choices = net_choices
    
    number = forms.IntegerField(label="Número", required=False, error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 50px"}))
    name = forms.CharField(label="Nome", required=False, min_length=3, max_length=80, error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 150px"}))
    iexact = forms.BooleanField(label="Buscar nomes exatos", required=False, error_messages=error_messages)
    environment = forms.ChoiceField(label="Ambiente", required=False, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 300px"}))
    net_type = forms.ChoiceField(label="Tipo", required=False, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 180px"}))
    ip_version = forms.IntegerField(label="Versão", required=True, error_messages=error_messages)
    networkv4 = forms.CharField(label="Rede IPv4", required=False, min_length=1, max_length=15, error_messages=error_messages, widget=forms.HiddenInput())
    networkv6 = forms.CharField(label="Rede IPv6", required=False, min_length=1, max_length=39, error_messages=error_messages, widget=forms.HiddenInput())
    subnet = forms.ChoiceField(label="Exato-Sub/Super Redes", required=False, choices=NETWORK_IP_CHOICES, error_messages=error_messages, widget=forms.RadioSelect, initial=0)
    acl = forms.BooleanField(label="Apenas Acls não validadas", required=False, error_messages=error_messages)
    
    def clean(self):
        cleaned_data = super(SearchVlanForm, self).clean()
        networkv4 = cleaned_data.get("networkv4")
        networkv6 = cleaned_data.get("networkv6")
        
        if len(networkv4) > 0 and len(networkv6) > 0:
            # Only one must be filled
            raise forms.ValidationError("Preencha apenas um: Rede IPv4 ou Rede IPv6")
        
        return cleaned_data