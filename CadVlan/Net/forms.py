# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

NETWORK_IP_CHOICES = ((0, "IPv4"), (1, "IPv6"))

class IPForm(forms.Form):
    equip_name = forms.CharField(label=u'Nome do Equipamento', min_length=3, required=True, widget=forms.TextInput(attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default", 'autocomplete': "off"}), error_messages=error_messages)
    descricao = forms.CharField(label=u'Descrição'   , min_length=3, max_length=100, required=False, error_messages=error_messages, widget=forms.Textarea(attrs={'style': "width: 500px", 'rows': 3, 'data-maxlenght':100}))
    
class IPEditForm(forms.Form):
    descricao = forms.CharField(label=u'Descrição'   , min_length=3, max_length=100, required=False, error_messages=error_messages, widget=forms.Textarea(attrs={'style': "width: 500px", 'rows': 3, 'data-maxlenght':100}))
    equip_names = forms.CharField(label=u'',required=False,widget=forms.HiddenInput())
    
class IPAssocForm(forms.Form):
    equip_name = forms.CharField(label=u'Nome do Equipamento', min_length=3, required=True, widget=forms.TextInput(attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default", 'autocomplete': "off"}), error_messages=error_messages)
    descricao = forms.CharField(label=u'Descrição'   , min_length=3, max_length=100, required=False, error_messages=error_messages, widget=forms.Textarea(attrs={'style': "width: 500px", 'rows': 3, 'data-maxlenght':100}))
    equip_names = forms.CharField(label=u'',required=False,widget=forms.HiddenInput())

class NetworkForm(forms.Form):
    
    def __init__(self, net_type_list, env_vip_list, *args, **kwargs):
        super(NetworkForm, self).__init__(*args, **kwargs)
        
        net_choices = [(net["id"], net["name"]) for net in net_type_list["net_type"]]
        net_choices.insert(0, ('', "-"))
        
        env_choices = ([(env['id'], env["finalidade_txt"] + " - " + env["cliente_txt"] + " - " + env["ambiente_p44_txt"]) for env in env_vip_list["environment_vip"]])
        env_choices.insert(0, ('', "-"))
        
        self.fields['net_type'].choices = net_choices
        self.fields['env_vip'].choices = env_choices
    
    vlan_name = forms.CharField(label=u'Número da Vlan', min_length=3, max_length=100, required=True, widget=forms.TextInput(attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default", 'autocomplete': "off"}), error_messages=error_messages)
    vlan_name_id = forms.IntegerField(label="Id da Vlan", required=True, error_messages=error_messages, widget=forms.HiddenInput())
    ip_version = forms.ChoiceField(label="Rede IPv4/IPv6", required=True, choices=NETWORK_IP_CHOICES, error_messages=error_messages, widget=forms.RadioSelect, initial=0)
    networkv4 = forms.CharField(label="Rede IPv4", required=False, min_length=1, max_length=18, error_messages=error_messages, widget=forms.HiddenInput())
    networkv6 = forms.CharField(label="Rede IPv6", required=False, min_length=1, max_length=43, error_messages=error_messages, widget=forms.HiddenInput())
    net_type = forms.ChoiceField(label="Tipo de Rede", required=True, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 180px"}))
    env_vip = forms.ChoiceField(label="Ambiente VIP", required=False, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 340px"}))
    
class NetworkEditForm(forms.Form):
    
    def __init__(self, net_type_list, env_vip_list, *args, **kwargs):
        super(NetworkEditForm, self).__init__(*args, **kwargs)
        
        net_choices = [(net["id"], net["name"]) for net in net_type_list["net_type"]]
        net_choices.insert(0, ('', "-"))
        
        env_choices = ([(env['id'], env["finalidade_txt"] + " - " + env["cliente_txt"] + " - " + env["ambiente_p44_txt"]) for env in env_vip_list["environment_vip"]])
        env_choices.insert(0, ('', "-"))
        
        self.fields['net_type'].choices = net_choices
        self.fields['env_vip'].choices = env_choices
    
    vlan_name = forms.CharField(label=u'Número da Vlan', min_length=3, max_length=100, required=True, widget=forms.TextInput(attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default", 'autocomplete': "off"}), error_messages=error_messages)
    ip_version = forms.ChoiceField(label="Rede IPv4/IPv6", required=True, choices=NETWORK_IP_CHOICES, error_messages=error_messages, widget=forms.RadioSelect, initial=0)
    net_type = forms.ChoiceField(label="Tipo de Rede", required=True, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 180px"}))
    env_vip = forms.ChoiceField(label="Ambiente VIP", required=False, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 340px"}))   