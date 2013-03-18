# -*- coding:utf-8 -*-

from django import forms
from CadVlan.messages import error_messages
from datetime import datetime


class SearchFormLog(forms.Form):
    
    def __init__(self, users, actions, functionalities, *args, **kwargs):
        super(SearchFormLog, self).__init__(*args, **kwargs)
        
        if isinstance(users, list):
            USER_CHOICES = ([(user['id_usuario'], (user['nome'] + ' - ' +user['usuario'])) for user in users])
        else:
            USER_CHOICES = ((0, '-'),)
        
        ACTION_CHOICES = ([(action, action) for action in actions])
        ACTION_CHOICES.insert(0, ('', '-'))
        
        if isinstance(functionalities, list):
            FUNCTIONALITY_CHOICES = ([(f['f_value'], f['f_name']) for f in functionalities])
        else:
            FUNCTIONALITY_CHOICES = ((0, '-'),)
            
        self.fields['user'].choices = USER_CHOICES
        self.fields['action'].choices = ACTION_CHOICES
        self.fields['functionality'].choices = FUNCTIONALITY_CHOICES


    
    user = forms.ChoiceField(label=u'Usuário', required=False, choices=[('', 'Selecione')], widget=forms.Select(attrs={'style': "width: 300px;"}), error_messages=error_messages)
    first_date = forms.CharField(label="De", required=False, min_length=3, max_length=80, error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 70px"}))
    start_time = forms.CharField(label="", required=False, min_length=5, max_length=5, initial='00:00', error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 40px"}))
    last_date = forms.CharField(label="Até", required=False, min_length=10, max_length=10, error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 70px"}))
    end_time = forms.CharField(label="", required=False, min_length=5, max_length=5, initial='23:59', error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 40px"}))
    action = forms.ChoiceField(label="Ação", required=False, choices=[('', 'Selecione'),],error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 90px"}))
    functionality = forms.ChoiceField(label="Funcionalidade", required=False, choices=[('', 'Selecione')], error_messages=error_messages, widget=forms.Select(attrs={"style": "width: 150px"}))
    parameter = forms.CharField(label="", required=False, min_length=1, max_length=80, error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 150px"}))
    
    def clean(self):
        cleaned_data = super(SearchFormLog, self).clean()
        
        first_date = cleaned_data.get("first_date")
        last_date = cleaned_data.get("last_date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        
        if first_date != '' and last_date != '':
            start_time = cleaned_data.get("start_time")
            first_date = first_date + ' ' + start_time + ':00'
            
            end_time = cleaned_data.get("end_time")
            last_date = last_date + ' ' + end_time + ':59'
            
            try:
                first_date = datetime.strptime(first_date, '%d/%m/%Y %H:%M:%S')
            except ValueError, e:
                raise forms.ValidationError("Formato de data e hora inválido.")
            
            try:
                last_date = datetime.strptime(last_date, '%d/%m/%Y %H:%M:%S')
            except ValueError, e:
                self.log.error(u'Datetime format of %s is invalid.', e.value)
                raise forms.ValidationError("Formato de data e hora inválido.")
            
            if last_date < first_date:
                raise forms.ValidationError("A data/hora final não pode ser menor que a data inicial.")
            if (first_date > datetime.today()):
                raise forms.ValidationError("A data/hora inicial não pode ser maior que a data atual.")
        else:
            start_time = datetime.strptime(start_time, '%H:%M')
            end_time   = datetime.strptime(end_time, '%H:%M')
            if end_time < start_time:
                raise forms.ValidationError("A hora final não pode ser menor que a hora inicial.")
                    
        if first_date != '' and last_date == '':
            raise forms.ValidationError("A data final do período deve ser informada.")
        if first_date == '' and last_date != '':
            raise forms.ValidationError("A data inicial do período deve ser informada.")
       
        
        return cleaned_data
