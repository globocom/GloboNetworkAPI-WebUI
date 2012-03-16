# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class LoginForm(forms.Form):
    username = forms.CharField(label=u'Usuário' , min_length=3, max_length=45, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    password = forms.CharField(label=u'Senha'   , min_length=3, max_length=45, required=True, error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 200px"}))
    redirect = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
