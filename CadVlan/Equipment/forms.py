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
