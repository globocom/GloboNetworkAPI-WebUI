# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class AclForm(forms.Form):
    
    acl = forms.CharField(label=u'ACL', required=False, error_messages=error_messages, widget=forms.Textarea(attrs={'style': "width: 800px;height:400px;resize:none;"}))
    comments = forms.CharField(label=u'Comentários', required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    apply_acl = forms.BooleanField(widget=forms.HiddenInput(), label='', required=False)