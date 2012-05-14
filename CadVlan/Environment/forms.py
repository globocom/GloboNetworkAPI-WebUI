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
    
    def __init__(self, env_logic, division_dc, group_l3, *args, **kwargs):
        super(AmbienteForm, self).__init__(*args, **kwargs)
        self.fields['divisao'].choices = [(div['id'], div['nome']) for div in division_dc["divisao_dc"]]
        self.fields['ambiente_logico'].choices = [(amb_log['id'], amb_log['nome']) for amb_log in env_logic["ambiente_logico"]]
        self.fields['grupol3'].choices = [(grupo['id'], grupo['nome']) for grupo in group_l3["grupo_l3"]]
        
    id_env = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    divisao = forms.ChoiceField(label="Divisão DC",choices=[(0, 'Selecione')] ,required=True,widget=forms.Select(attrs={'style': "width: 160px"}), error_messages=error_messages)
    ambiente_logico = forms.ChoiceField(label="Ambiente Lógico",required=True,choices=[(0, 'Selecione')] ,widget=forms.Select(attrs={'style': "width: 210px"}), error_messages=error_messages)
    grupol3 = forms.ChoiceField(label="Grupo Layer3",choices=[(0, 'Selecione')],required=True,widget=forms.Select(attrs={'style': "width: 280px"}), error_messages=error_messages)
    link = forms.CharField(label=u'Link', max_length=200, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 280px"}))
