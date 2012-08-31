# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages, ldap_messages
from CadVlan.Util.forms.decorators import autostrip
from CadVlan.Util.utility import is_valid_cn
from CadVlan.Ldap.model import Ldap

@autostrip
class GroupForm(forms.Form):
    
    def __init__(self, users_list, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['member_uid'].choices = [(st['cn'], st['cn']) for st in users_list]

    cn = forms.CharField(label=u'Groupname (GID / CN):', min_length=3, max_length=50,  required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))    
    gidNumber = forms.IntegerField(label=u'gidNumber:', required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    member_uid = forms.MultipleChoiceField(label=u'Usuarios:'  , required=True, error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))
    
    def clean(self):
        cleaned_data = self.cleaned_data

        cn  = cleaned_data.get("cn")
        gidNumber  = cleaned_data.get("gidNumber")
        
        if cn is not None:
            
            if not is_valid_cn(cn):
                self._errors["cn"] = self.error_class([ldap_messages.get("invalid_cn")])  

        if gidNumber is not None:

            ldap = Ldap(None)

            if not ldap.valid_range_group(gidNumber):
                self._errors["gidNumber"] = self.error_class([ldap_messages.get("error_range_out_group") % ( ldap.rangeGroups[0], ldap.rangeGroups[-1] )])

        return cleaned_data