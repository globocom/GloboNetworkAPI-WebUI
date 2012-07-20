# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class SearchVipRequestForm(forms.Form):
    
    id_request = forms.IntegerField(label="Id Requisição", required=False,error_messages=error_messages,widget=forms.TextInput(attrs={"style": "width: 40px"}))
    ipv4 = forms.CharField(label="IPv4", required=False, min_length=1, max_length=15, error_messages=error_messages, widget=forms.HiddenInput())
    ipv6 = forms.CharField(label="IPv6", required=False, min_length=1, max_length=39, error_messages=error_messages, widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = super(SearchVipRequestForm, self).clean()
        ipv4 = cleaned_data.get("ipv4")
        ipv6 = cleaned_data.get("ipv6")
        
        if ipv4 != None and ipv6 != None:
            if len(ipv4) > 0 and len(ipv6) > 0:
                # Only one must be filled
                raise forms.ValidationError("Preencha apenas um: IPv4 ou IPv6")
            
        return cleaned_data