# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django import forms
from CadVlan.messages import error_messages
from CadVlan.forms import EquipForm


class AssociateScriptForm(EquipForm):

    def __init__(self, script_list, *args, **kwargs):
        super(AssociateScriptForm, self).__init__(*args, **kwargs)
        self.fields['script'].choices = [
            (st['id'], st['roteiro'] + " - " + st['descricao'] + " - " + st['id']) for st in script_list["script"]]

    script = forms.ChoiceField(label='', required=True, widget=forms.Select(
        attrs={'style': "width: 400px"}), error_messages=error_messages)
