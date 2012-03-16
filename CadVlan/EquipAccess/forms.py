from django import forms
from CadVlan.messages import error_messages

class SearchEquipAccessForm(forms.Form):
    
    equip_name = forms.CharField(label=u'Nome de Equipamento', min_length=3, required=True, widget=forms.TextInput(attrs={'style': "width: 300px; height: 19px;", 'class': "ui-state-default"}), error_messages=error_messages)
    