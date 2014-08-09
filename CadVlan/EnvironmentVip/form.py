# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages


class EnvironmentVipForm(forms.Form):

    def __init__(self, script_type_list, *args, **kwargs):
        super(EnvironmentVipForm, self).__init__(*args, **kwargs)
        self.fields['option_vip'].choices = [
            (st['id'],
             st['tipo_opcao'] +
                " - " +
                st['nome_opcao_txt']) for st in script_type_list["option_vip"]]

    id = forms.IntegerField(
        label="",
        required=False,
        widget=forms.HiddenInput(),
        error_messages=error_messages)
    finality = forms.CharField(
        label=u'Finalidade',
        min_length=3,
        max_length=50,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                'style': "width: 300px"}))
    client = forms.CharField(
        label=u'Cliente',
        min_length=3,
        max_length=50,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                'style': "width: 300px"}))
    environment_p44 = forms.CharField(
        label=u'Ambiente P44',
        min_length=3,
        max_length=50,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                'style': "width: 300px"}))
    option_vip = forms.MultipleChoiceField(
        label=u'Opções VIP',
        required=False,
        error_messages=error_messages,
        widget=forms.SelectMultiple(
            attrs={
                'style': "width: 310px"}))
