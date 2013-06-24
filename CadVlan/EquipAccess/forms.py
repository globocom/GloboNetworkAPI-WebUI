from django import forms
from CadVlan.messages import error_messages

class EquipAccessForm(forms.Form):
    
    def __init__(self, protocol_list, *args, **kwargs):
        super(EquipAccessForm, self).__init__(*args, **kwargs)
        self.fields['protocol'].choices = [(p['id'], p['protocolo']) for p in protocol_list["tipo_acesso"]]
                
    host = forms.CharField  (label=u'Host', min_length=5, max_length=100 , required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    user = forms.CharField  (label=u'Usuario', min_length=3, max_length=20 , required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    password = forms.CharField  (label=u'Senha', min_length=3, max_length=150 , required=True, error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 300px"},render_value = True))
    second_password = forms.CharField  (label=u'Senha secundaria', min_length=3, max_length=150 , required=True, error_messages=error_messages, widget=forms.PasswordInput(attrs={'style': "width: 300px"},render_value = True))
    protocol = forms.ChoiceField(label=u'Protocolo', choices=[(0, 'Selecione')]  , required=True, error_messages=error_messages, widget=forms.Select(attrs={'style': "width: 310px"}))
    id_equip = forms.CharField(widget=forms.HiddenInput(), label='',required=False)
    name_equip = forms.CharField(widget=forms.HiddenInput(), label='',required=False)