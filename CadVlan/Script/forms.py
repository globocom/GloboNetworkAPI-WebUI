# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class ScriptForm(forms.Form):
    
    def __init__(self, script_type_list, *args, **kwargs):
        super(ScriptForm, self).__init__(*args, **kwargs)
        self.fields['script_type'].choices = [(st['id'], st['tipo'] + " - " + st['descricao']) for st in script_type_list["tipo_roteiro"]]
    
    name        = forms.CharField  (label=u'Nome do Roteiro', min_length=3, max_length=40 , required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    script_type = forms.ChoiceField(label=u'Tipo de Roteiro', choices=[(0, 'Selecione')]  , required=True, error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))
    description = forms.CharField  (label=u'Descrição'      , min_length=3, max_length=100, required=True, error_messages=error_messages, widget=forms.Textarea(attrs={'style': "width: 500px", 'rows': 3, 'data-maxlenght':100}))