# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class UserGroupForm(forms.Form):
    
    def __init__(self, user_list, *args, **kwargs):
        super(UserGroupForm, self).__init__(*args, **kwargs)
        if user_list is not None:
            self.fields['users'].choices = [(st['id'], st['nome']) for st in user_list["users"]]

    users = forms.MultipleChoiceField(label=u'Usuários'  , required=True, error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))
    
class PermissionGroupForm(forms.Form):
    
    id_group_perms = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    function = forms.CharField  (label=u'Função', min_length=3, max_length=100 , required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    read = forms.BooleanField(label=u'Leitura', required=False, error_messages=error_messages)
    write = forms.BooleanField(label=u'Escrita', required=False, error_messages=error_messages)