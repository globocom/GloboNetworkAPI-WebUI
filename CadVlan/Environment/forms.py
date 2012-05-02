# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class DivisaoDCForm(forms.Form):
    nome = forms.CharField(label=u'Divisão do Data Center' , min_length=3, max_length=100, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    
class Grupol3Form(forms.Form):
    nome = forms.CharField(label=u'Grupo Layer3' , min_length=3, max_length=80, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    
class AmbienteLogicoForm(forms.Form):
    nome = forms.CharField(label=u'Ambiente Lógico' , min_length=3, max_length=80, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    
class AmbienteForm(forms.Form):
    
    def __init__(self,ambientes,*args,**kwargs):
        super(AmbienteForm, self).__init__(*args, **kwargs)
        self.fields['divisao'].choices = [(div['id'], div['nome']) for div in ambientes["divisoes"]]
        self.fields['ambiente_logico'].choices = [(amb_log['id'], amb_log['nome']) for amb_log in ambientes["ambientesl"]]
        self.fields['grupol3'].choices = [(grupo['id'], grupo['nome']) for grupo in ambientes["gruposl3"]]
        
    divisao = forms.ChoiceField(label="Divisão DC",choices=[(0, 'Selecione')] ,required=True,widget=forms.Select(attrs={'style': "width: 400px"}), error_messages=error_messages)
    ambiente_logico = forms.ChoiceField(label="Ambiente Lógico",required=True,choices=[(0, 'Selecione')] ,widget=forms.Select(attrs={'style': "width: 400px"}), error_messages=error_messages)
    grupol3 = forms.ChoiceField(label="Grupo Layer3",choices=[(0, 'Selecione')],required=True,widget=forms.Select(attrs={'style': "width: 400px"}), error_messages=error_messages)
    link = forms.CharField(label=u'Link', max_length=200, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"})) 