# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages
from CadVlan.Util.utility import check_regex
from CadVlan.settings import PATCH_PANEL_ID

class ConnectForm(forms.Form):
    
    def __init__(self, equipment, interf_list, *args, **kwargs):
        super(ConnectForm, self).__init__(*args, **kwargs)
        
        front_choices = []
        back_choices = []
        attrs = dict()
        
        front_choices.append(("", "Selecione"))
        back_choices.append(("", "Selecione"))
        
        if equipment['id_tipo_equipamento'] == str(PATCH_PANEL_ID):
            for interf in interf_list:
                if interf["ligacao_front"] == None:
                    front_choices.append((interf['id'], interf['interface']))
                if interf['ligacao_back'] == None:
                    back_choices.append((interf['id'], interf['interface']))
        else:
            attrs["style"] = "display: none;"
            for interf in interf_list:
                if interf["ligacao_front"] == None:
                    front_choices.append((interf['id'], interf['interface']))
                    
        if len(front_choices) == 1:
            front_choices = [("", "Nenhuma interface disponível")]
        if len(back_choices) == 1:
            back_choices = [("", "Nenhuma interface disponível")]
            
        self.fields['front'].choices = front_choices
        self.fields['back'].widget = forms.Select(attrs=attrs)
        self.fields['back'].choices = back_choices
        
    front = forms.ChoiceField(label="", required=False, error_messages=error_messages)
    back = forms.ChoiceField(label="", required=False, error_messages=error_messages)
    equip_name = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    equip_id = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    
    def clean_back(self):
        front = self.cleaned_data.get("front")
        back = self.cleaned_data.get("back")
        
        if not len(front) == 0 and not len(back) == 0:
            # Only one must be filled
            raise forms.ValidationError("Preencha apenas um: Front ou Back")
        
        elif len(front) == 0 and len(back) == 0:
            # Only one must be filled
            raise forms.ValidationError("Preencha pelo menos um: Front ou Back")
        
        return self.cleaned_data.get("back")
    
class AddInterfaceForm(forms.Form):
    
    def __init__(self, marca, index, *args, **kwargs):
        super(AddInterfaceForm, self).__init__(*args, **kwargs)
        
        attrs = dict()
        if marca == "3":
            attrs["onChange"] = "javascript:setMask(" + str(index) + ")"
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("", "Selecione"),("Fa", "Fa"),("Gi", "Gi"),("Te", "Te"),("Serial", "Serial")]
        else:
            attrs["style"] = "display: none;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("", "")]
            
        widget=forms.TextInput(attrs={"style": "width: 150px;", "onKeyUp": "javascript:fixName(this, " + str(index) + ");"})
        self.fields['name'].widget = widget
        
        if marca == "0":
            self.regex = "^([a-zA-Z0-9]+(:)?){1,6}$"
        elif marca == "2":
            self.regex = "^(Int)\s[0-9]+$"
        elif marca == "3":
            self.regex = "^(Fa|Gi|Te|Serial)[0-9]+(/[0-9]+(/[0-9]+)?)?$"
        elif marca == "4":
            self.regex = "^(interface)\s[0-9]+(.[0-9]+)?$"
        elif marca == "5":
            self.regex = "^(eth)[0-9]+(/[0-9]+)?$"
        elif marca == "8":
            self.regex = "^[0-9]+$"
        else:
            self.regex = ""
            
    combo = forms.ChoiceField(label="", required=False, error_messages=error_messages)
    name = forms.CharField(label="Nome da Interface", required=True, min_length=3, max_length=20, error_messages=error_messages)
    description = forms.CharField(label=u'Descrição', required=False, min_length=3, max_length=200, error_messages=error_messages, widget=forms.Textarea(attrs={'style': "width: 250px; height: 34px;", 'rows': 2, 'data-maxlenght':200}))
    protected = forms.ChoiceField(label="Protegido", required=True, choices=[(0, "Não"),(1, "Sim")], error_messages=error_messages, widget=forms.RadioSelect, initial=0)
    equip_name = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    equip_id = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    inter_id = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if not check_regex(name, self.regex):
            raise forms.ValidationError('Nome da interface inválida para esta marca')
        
        return self.cleaned_data['name']
    
class AddSeveralInterfaceForm(forms.Form):
    
    def __init__(self, marca, *args, **kwargs):
        super(AddSeveralInterfaceForm, self).__init__(*args, **kwargs)
        
        
        attrs = dict()
        attrs["onChange"] = "javascript:showHideInput()"
        self.fields['campos'].widget = forms.Select(attrs=attrs)
        
        attrs = dict()
        if marca == "3":
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("Fa", "Fa"),("Gi", "Gi"),("Te", "Te"),("Serial", "Serial")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [("Fa", "Fa"),("Gi", "Gi"),("Te", "Te"),("Serial", "Serial")]
            self.regex = "^(Fa|Gi|Te|Serial)[0-9]+(/[0-9]+(/[0-9]+)?)?$"
            self.fields['campos'].choices = [("1", "1"),("2", "2"),("3", "3")]
             
        elif marca == "2":
            attrs["style"] = "width: 98px;"
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.regex = "^(Int)\s[0-9]+$"
            self.fields['campos'].choices = [("1", "1")]
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("Int", "Int")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [("Int", "Int")]
            
        elif marca == "4":
            self.regex = "^(interface)\s[0-9]+(.[0-9]+)?$"
            self.fields['campos'].choices = [("1", "1"),("2", "2")]
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("interface", "interface")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [("interface", "interface")]
        elif marca == "5":
            self.regex = "^(eth)[0-9]+(/[0-9]+)?$"
            self.fields['campos'].choices = [("1", "1"),("2", "2")]
            self.fields['combo'].widget = forms.Select(attrs=attrs)
            self.fields['combo'].choices = [("eth", "eth")]
            attrs['disabled'] = "disabled"
            self.fields['combo_aux'].widget = forms.Select(attrs=attrs)
            self.fields['combo_aux'].choices = [("eth", "eth")]
        
            
    campos = forms.ChoiceField(label="Campos", required=False, error_messages=error_messages)        
    combo = forms.ChoiceField(label="", required=False, error_messages=error_messages)
    combo_aux = forms.ChoiceField(label="", required=False, error_messages=error_messages)
    name = forms.CharField(label="", required=True, min_length=3, max_length=20, error_messages=error_messages, widget=forms.HiddenInput())
    last_piece_name = forms.IntegerField(label="", required=True,  error_messages=error_messages, widget=forms.HiddenInput())
    last_piece_name2 = forms.IntegerField(label="", required=True,  error_messages=error_messages, widget=forms.HiddenInput())
    description = forms.CharField(label=u'Descrição', required=False, min_length=3, max_length=200, error_messages=error_messages, widget=forms.Textarea(attrs={'style': "width: 250px", 'rows': 2, 'data-maxlenght':200}))
    protected = forms.ChoiceField(label="Protegido", required=True, choices=[(0, "Não"),(1, "Sim")], error_messages=error_messages, widget=forms.RadioSelect, initial=0)
    equip_name = forms.CharField(widget=forms.HiddenInput(), label='', required=False)
    equip_id = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)
    inter_id = forms.IntegerField(widget=forms.HiddenInput(), label='', required=False)

    def clean_name(self):
        name = self.cleaned_data['name']
        if not check_regex(name, self.regex):
            raise forms.ValidationError('Nome da interface inválida para esta marca')
        
        return self.cleaned_data['name']