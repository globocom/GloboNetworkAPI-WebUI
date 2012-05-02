# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class IPForm(forms.Form):
    equip_name = forms.CharField(label=u'Nome do Equipamento', min_length=3, required=True, widget=forms.TextInput(attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default", 'autocomplete': "off"}), error_messages=error_messages)
    descricao = forms.CharField(label=u'Descrição'   , min_length=3, max_length=100, required=False, error_messages=error_messages, widget=forms.Textarea(attrs={'style': "width: 500px", 'rows': 3, 'data-maxlenght':100}))
    
class IPEditForm(forms.Form):
    descricao = forms.CharField(label=u'Descrição'   , min_length=3, max_length=100, required=False, error_messages=error_messages, widget=forms.Textarea(attrs={'style': "width: 500px", 'rows': 3, 'data-maxlenght':100}))
    equip_names = forms.CharField(label=u'',required=False,widget=forms.HiddenInput())