# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class EquipForm(forms.Form):
    equip_id   = forms.IntegerField(label='', required=False, widget=forms.HiddenInput())
    equip_name = forms.CharField   (label='', required=False, widget=forms.HiddenInput())

class DeleteForm(EquipForm):
    ids = forms.CharField(widget=forms.HiddenInput(), label='', required=True)

class SearchEquipForm(forms.Form):
    equip_name = forms.CharField(label=u'Nome de Equipamento', min_length=3, required=True, widget=forms.TextInput(attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default", 'autocomplete': "off"}), error_messages=error_messages)
    
