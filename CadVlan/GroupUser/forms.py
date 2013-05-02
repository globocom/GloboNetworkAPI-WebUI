# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class GroupUserForm(forms.Form):

    id_group_user = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    name = forms.CharField  (label=u'Nome', min_length=3, max_length=100 , required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    read = forms.BooleanField(label=u'Leitura', required=False, error_messages=error_messages)
    write = forms.BooleanField(label=u'Escrita', required=False, error_messages=error_messages)
    edition = forms.BooleanField(label=u'Edição', required=False, error_messages=error_messages)
    delete = forms.BooleanField(label=u'Exclusão', required=False, error_messages=error_messages)