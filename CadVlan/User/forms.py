# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class UserForm(forms.Form):
    
    def __init__(self, group_list, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if group_list is not None:
            self.fields['groups'].choices = [(gl['id'], gl['nome']) for gl in group_list["grupo"]]
    
    name = forms.CharField(label=u'Nome',required=True,max_length = 200, min_length = 3,error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    email = forms.EmailField(label=u'Email',required=True,max_length = 300, min_length = 6,error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    user = forms.CharField(label=u'Usuário',required=True,max_length = 45, min_length = 3,error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    groups = forms.MultipleChoiceField(label=u'Grupos de Usuário'  , required=False, error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))
    password =  forms.CharField(label='', required=False, widget=forms.HiddenInput())
    active =  forms.BooleanField(label='', required=False, widget=forms.HiddenInput())