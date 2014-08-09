# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages


class LoginForm(forms.Form):
    username = forms.CharField(label=u'Usuário', min_length=3, max_length=45, required=True,
                               error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    password = forms.CharField(label=u'Senha', min_length=3, max_length=45, required=True,
                               error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 200px"}))
    redirect = forms.CharField(
        widget=forms.HiddenInput(), label='', required=False)
    is_ldap_user = forms.BooleanField(
        label=u"Autenticar com usuário da rede", required=False)


class PassForm(forms.Form):
    username = forms.CharField(label=u'Usuário', min_length=3, max_length=45, required=True,
                               error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    email = forms.EmailField(label=u'Email', min_length=6, max_length=300, required=True,
                             error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))


class ChangePassForm(forms.Form):
    new_pass = forms.CharField(label=u'Nova senha', min_length=6, max_length=20, required=True,
                               error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 200px"}))
    confirm_new_password = forms.CharField(label=u'Confirme a nova senha', min_length=6, max_length=20,
                                           required=True, error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 200px"}))

    def clean_confirm_new_password(self):
        if self.cleaned_data['confirm_new_password'] != self.data['new_pass']:
            raise forms.ValidationError('Confirmacao da senha nao confere')

        return self.cleaned_data['confirm_new_password']
