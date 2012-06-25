# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class EquipGroupForm(forms.Form):
    
    id_egroup = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    egroup = forms.CharField  (label=u'Nome Grupo', min_length=3, max_length=50,  required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px",'readonly':'readonly'}))
    equip_name = forms.CharField(label=u'Nome de Equipamento', min_length=3, required=True, widget=forms.TextInput(attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default", 'autocomplete': "off"}), error_messages=error_messages)
    
    