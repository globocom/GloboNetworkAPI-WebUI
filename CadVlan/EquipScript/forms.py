# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages
from CadVlan.forms import EquipForm


class AssociateScriptForm(EquipForm):

    def __init__(self, script_list, *args, **kwargs):
        super(AssociateScriptForm, self).__init__(*args, **kwargs)
        self.fields['script'].choices = [
            (st['id'], st['roteiro'] + " - " + st['descricao']) for st in script_list["script"]]

    script = forms.ChoiceField(label='', required=True, widget=forms.Select(
        attrs={'style': "width: 400px"}), error_messages=error_messages)
