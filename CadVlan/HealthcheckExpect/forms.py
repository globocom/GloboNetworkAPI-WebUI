# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages

class HealthckeckExpectForm(forms.Form):
    
    def __init__(self, environment_list, *args, **kwargs):
        super(HealthckeckExpectForm, self).__init__(*args, **kwargs)
        
        env_choices = ([(env['id'], env["divisao_dc_name"] + " - " + env["ambiente_logico_name"] + " - " + env["grupo_l3_name"]) for env in environment_list["ambiente"]])
        env_choices.insert(0, (0, "-"))
        self.fields['environment'].choices = env_choices

    match_list = forms.CharField(label=u'Match List' , min_length=2, max_length=50, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    expect_string = forms.CharField(label=u'Except String' , min_length=2, max_length=50, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))
    environment = forms.ChoiceField(label="Ambiente", required=True, choices=[(0, "Selecione")], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 300px"}))
 
    def clean_environment(self):
        if int(self.cleaned_data['environment']) <= 0:
            raise forms.ValidationError('Este campo é obrigatório')

        return self.cleaned_data['environment']
    