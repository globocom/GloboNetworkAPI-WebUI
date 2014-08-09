# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages


class FilterForm(forms.Form):

    def __init__(self, equip_type_list, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['equip_type'].choices = [
            (et['id'], et['nome']) for et in equip_type_list["equipment_type"]]

    id = forms.IntegerField(
        label="",
        required=False,
        widget=forms.HiddenInput(),
        error_messages=error_messages)
    name = forms.CharField(
        label=u'Nome',
        min_length=3,
        max_length=100,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                'style': "width: 300px"}))
    description = forms.CharField(
        label=u'Descrição',
        min_length=3,
        max_length=200,
        required=True,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                'style': "width: 300px"}))
    equip_type = forms.MultipleChoiceField(
        label=u'Tipos de equipamento',
        required=True,
        error_messages=error_messages,
        widget=forms.SelectMultiple(
            attrs={
                'style': "width: 310px"}))
