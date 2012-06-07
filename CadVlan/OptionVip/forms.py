# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages
from CadVlan.Util.utility import check_regex

REGEX_TEXT = r"^[a-zA-Z\\-_\\\-\\ ]*$"

class OptionVipForm(forms.Form):

    id_option = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    name_option = forms.CharField  (label=u'Nome', min_length=3, max_length=50 , required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    type_option = forms.CharField  (label=u'Tipo', min_length=3, max_length=50,  required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))

    def clean_name_option(self):
        if not check_regex(self.cleaned_data['name_option'], REGEX_TEXT):
            raise forms.ValidationError('Caracteres inválidos.')

        return self.cleaned_data['name_option']

    def clean_type_option(self):
        if not check_regex(self.cleaned_data['type_option'], REGEX_TEXT):
            raise forms.ValidationError('Caracteres inválidos.')

        return self.cleaned_data['type_option']