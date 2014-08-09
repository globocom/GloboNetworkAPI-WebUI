# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages
from CadVlan.Util.utility import check_regex


class TipoRedeForm(forms.Form):

    name = forms.CharField(label=u'Nome', min_length=3, max_length=100, required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))

    def clean_nome(self):
        if not check_regex(self.cleaned_data['name'], r'^[- 0-9a-zA-Z]+$'):
            raise forms.ValidationError('Caracteres inválidos.')

        return self.cleaned_data['name']
