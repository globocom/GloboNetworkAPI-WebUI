# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages


class ScriptTypeForm(forms.Form):

    script_type = forms.CharField(
        label=u'Tipo de Roteiro',
        min_length=3,
        max_length=40,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                'style': "width: 300px"}))
    description = forms.CharField(
        label=u'Descrição',
        min_length=3,
        max_length=100,
        required=True,
        error_messages=error_messages,
        widget=forms.Textarea(
            attrs={
                'style': "width: 500px",
                'rows': 3,
                'data-maxlenght': 100}))
