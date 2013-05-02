# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class GroupEquipForm(forms.Form):
    
    id = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    name = forms.CharField  (label=u'Nome Grupo', min_length=3, max_length=100,  required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))