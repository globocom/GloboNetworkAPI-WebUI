# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages
from CadVlan.Util.utility import check_regex


class DivisaoDCForm(forms.Form):
    id_env = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    nome = forms.CharField(label=u'Divisão do Data Center' , min_length=2, max_length=100, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    
    def clean_nome(self):
        if not check_regex(self.cleaned_data['nome'], r'^[-0-9a-zA-Z]+$'):
            raise forms.ValidationError('Caracteres inválidos.')
        
        return self.cleaned_data['nome']
    
class Grupol3Form(forms.Form):
    id_env = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    nome = forms.CharField(label=u'Grupo Layer3' , min_length=2, max_length=80, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    
    def clean_nome(self):
        if not check_regex(self.cleaned_data['nome'], r'^[-0-9a-zA-Z]+$'):
            raise forms.ValidationError('Caracteres inválidos.')
        
        return self.cleaned_data['nome']
    
class AmbienteLogicoForm(forms.Form):
    id_env = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    nome = forms.CharField(label=u'Ambiente Lógico' , min_length=2, max_length=80, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    
    def clean_nome(self):
        if not check_regex(self.cleaned_data['nome'], r'^[-0-9a-zA-Z]+$'):
            raise forms.ValidationError('Caracteres inválidos.')
        
        return self.cleaned_data['nome']
    
class AmbienteForm(forms.Form):
    
    def __init__(self, env_logic, division_dc, group_l3, filters, ipv4, ipv6, *args, **kwargs):
        super(AmbienteForm, self).__init__(*args, **kwargs)
        self.fields['divisao'].choices = [(div['id'], div['nome']) for div in division_dc["division_dc"]]
        self.fields['ambiente_logico'].choices = [(amb_log['id'], amb_log['nome']) for amb_log in env_logic["logical_environment"]]
        self.fields['grupol3'].choices = [(grupo['id'], grupo['nome']) for grupo in group_l3["group_l3"]]
        self.fields['filter'].choices = [(filter_['id'], filter_['name']) for filter_ in filters["filter"]]
        self.fields['filter'].choices.insert(0, (None,'--------'))
        self.fields['ipv4_template'].choices = [(template['name'], template['name']) for template in ipv4]
        self.fields['ipv4_template'].choices.insert(0, ('','--------'))
        self.fields['ipv6_template'].choices = [(template['name'], template['name']) for template in ipv6]
        self.fields['ipv6_template'].choices.insert(0, ('','--------'))
        
    id_env = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    divisao = forms.ChoiceField(label="Divisão DC",choices=[(0, 'Selecione')] ,required=True,widget=forms.Select(attrs={'style': "width: 160px"}), error_messages=error_messages)
    ambiente_logico = forms.ChoiceField(label="Ambiente Lógico",required=True,choices=[(0, 'Selecione')] ,widget=forms.Select(attrs={'style': "width: 210px"}), error_messages=error_messages)
    grupol3 = forms.ChoiceField(label="Grupo Layer3",choices=[(0, 'Selecione')],required=True,widget=forms.Select(attrs={'style': "width: 280px"}), error_messages=error_messages)
    filter = forms.ChoiceField(label="Filtro",choices=[(None, '--------')],required=False,widget=forms.Select(attrs={'style': "width: 280px"}), error_messages=error_messages)
    acl_path = forms.CharField(label=u'Path ACL', max_length=250, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 280px", 'autocomplete': "off"}))
    ipv4_template = forms.ChoiceField(label="Template ACL IPV4",choices=[('', '--------')],required=False,widget=forms.Select(attrs={'style': "width: 280px"}), error_messages=error_messages)
    ipv6_template = forms.ChoiceField(label="Template ACL IPV6",choices=[('', '--------')],required=False,widget=forms.Select(attrs={'style': "width: 280px"}), error_messages=error_messages)
    link = forms.CharField(label=u'Link', max_length=200, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 280px"}))
    
    max_num_vlan_1 = forms.CharField(label=u'Max Vlan 1', max_length=50, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))
    min_num_vlan_1 = forms.CharField(label=u'Min Vlan 1', max_length=50, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))
    max_num_vlan_2 = forms.CharField(label=u'Max Vlan 2', max_length=50, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))
    min_num_vlan_2 = forms.CharField(label=u'Min Vlan 2', max_length=50, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))


    def clean_min_num_vlan_1(self):
        max_num_vlan_1 = self.cleaned_data['max_num_vlan_1']
        min_num_vlan_1 = self.cleaned_data['min_num_vlan_1']

        if (max_num_vlan_1 != '' and min_num_vlan_1 == '') or ( min_num_vlan_1 != '' and max_num_vlan_1 == ''):
            raise forms.ValidationError('O valor máximo e mínimo devem ser preenchidos.')

        if max_num_vlan_1 != '' and min_num_vlan_1 != '':
            max_num_vlan_1 = int(max_num_vlan_1)
            min_num_vlan_1 = int(min_num_vlan_1)

            if max_num_vlan_1 < 1 or min_num_vlan_1 < 1:
                raise forms.ValidationError('O valor preenchido deve ser maior que zero.')
            if max_num_vlan_1 <= min_num_vlan_1:
                raise forms.ValidationError('O valor máximo deve ser maior que o mínimo.')

        return min_num_vlan_1


    def clean_min_num_vlan_2(self):
        max_num_vlan_2 = self.cleaned_data['max_num_vlan_2']
        min_num_vlan_2 = self.cleaned_data['min_num_vlan_2']

        if (max_num_vlan_2 != '' and min_num_vlan_2 == '') or ( min_num_vlan_2 != '' and max_num_vlan_2 == ''):
            raise forms.ValidationError('O valor máximo e mínimo devem ser preenchidos.')

        if max_num_vlan_2 != '' and min_num_vlan_2 != '':
            max_num_vlan_2 = int(max_num_vlan_2)
            min_num_vlan_2 = int(min_num_vlan_2)
            
            if max_num_vlan_2 < 1 or min_num_vlan_2 < 1:
                raise forms.ValidationError('O valor preenchido deve ser maior que zero.')
            
            if max_num_vlan_2 <= min_num_vlan_2:
                raise forms.ValidationError('O valor máximo deve ser maior que o mínimo.')

        return min_num_vlan_2


    def clean_acl_path(self):
        #valida acl_path
        if check_regex(self.cleaned_data['acl_path'], r'^.*[\\\\:*?"<>|].*$'):
            raise forms.ValidationError('Caracteres inválidos.')
            
        path = self.cleaned_data['acl_path']
        if path:
            try:
                while path[0] == "/":
                    path = path[1:]
                
                while path[-1] == "/":
                    path = path[:-1]
            except IndexError:
                raise forms.ValidationError('Path inválido')
        #valida acl_path

        return self.cleaned_data['acl_path']
