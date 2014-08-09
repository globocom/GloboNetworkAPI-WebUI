# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages


class UserForm(forms.Form):

    def __init__(self, group_list, ldap_group_list=None, ldap_user_list=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if group_list is not None:
            self.fields['groups'].choices = [
                (gl['id'], gl['nome']) for gl in group_list["user_group"]]

        if ldap_group_list is not None:
            self.fields['ldap_group'].choices = [
                (ldap_grp[0], ldap_grp[1]) for ldap_grp in ldap_group_list]

        if ldap_user_list is not None:
            self.fields['ldap_user'].choices = [
                (ldap_usr, ldap_usr) for ldap_usr in ldap_user_list]

    name = forms.CharField(label=u'Nome', required=True, max_length=200, min_length=3,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    email = forms.EmailField(label=u'Email', required=True, max_length=300, min_length=6,
                             error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    user = forms.CharField(label=u'Usuário', required=True, max_length=45, min_length=3,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))

    is_ldap = forms.BooleanField(label='Associar usuário LDAP', required=False)
    ldap_group = forms.ChoiceField(label='Grupo LDAP', required=False)
    ldap_user = forms.ChoiceField(label='Usuário LDAP', required=False, widget=forms.Select(
        attrs={'style': "width: 507px", 'size': "10"}))

    groups = forms.MultipleChoiceField(label=u'Grupos de Usuário', required=False,
                                       error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))
    password = forms.CharField(
        label='', required=False, widget=forms.HiddenInput())
    active = forms.BooleanField(
        label='', required=False, widget=forms.HiddenInput())

    def clean_ldap_user(self):

        try:
            is_ldap = self.cleaned_data['is_ldap']
            if not is_ldap:
                raise KeyError

            if self.cleaned_data['ldap_user'] == '':
                raise forms.ValidationError(
                    'Escolha um usuário LDAP para associar')

        except KeyError:
            self.cleaned_data['ldap_group'] = None
            self.cleaned_data['ldap_user'] = None

        return self.cleaned_data['ldap_user']
