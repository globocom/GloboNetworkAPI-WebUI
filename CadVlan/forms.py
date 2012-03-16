# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms

class DeleteForm(forms.Form):
    ids = forms.CharField(widget=forms.HiddenInput(), label='', required=True)
