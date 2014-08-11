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
from CadVlan.messages import error_messages, ldap_messages
from CadVlan.Util.forms.decorators import autostrip
from CadVlan.Util.forms.customRenderer import RadioCustomRenderer
from CadVlan.Util.forms.validators import validate_cn, validate_phone, validate_commands
from CadVlan.Ldap.model import Ldap


@autostrip
class GroupForm(forms.Form):

    def __init__(self, users_list, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['member_uid'].choices = [
            (st['cn'], st['cn']) for st in users_list]

    cn = forms.CharField(label=u'Groupname (GID / CN):', min_length=3, max_length=50,  required=True, validators=[
                         validate_cn], error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    gidNumber = forms.IntegerField(
        label=u'gidNumber:', required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    member_uid = forms.MultipleChoiceField(
        label=u'Usuarios:', required=False, error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))

    def clean(self):
        cleaned_data = self.cleaned_data
        gidNumber = cleaned_data.get("gidNumber")

        if gidNumber is not None:

            ldap = Ldap(None)

            if not ldap.valid_range_group(gidNumber):
                self._errors["gidNumber"] = self.error_class([ldap_messages.get(
                    "error_range_out_group") % (ldap.rangeGroups[0], ldap.rangeGroups[-1])])

        return cleaned_data


@autostrip
class SudoerForm(forms.Form):

    def __init__(self, groups_list, commands_list=[], *args, **kwargs):
        super(SudoerForm, self).__init__(*args, **kwargs)
        self.fields['groups'].choices = [
            (st['cn'], st['cn']) for st in groups_list]
        self.fields['commands'].choices = [(st, st) for st in commands_list]

    cn = forms.CharField(label=u'Nome da regra:',  max_length=50,  required=True, validators=[
                         validate_cn], error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    host = forms.CharField(label=u'Host ou rede:', max_length=50,  required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    groups = forms.MultipleChoiceField(
        label=u'Grupos:', required=True, error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))
    command = forms.CharField(label=u'Comandos:', required=False, error_messages=error_messages, widget=forms.TextInput(
        attrs={'style': "width: 215px"}))
    commands = forms.MultipleChoiceField(label=u'', required=True, validators=[
                                         validate_commands], error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))

CHOICES_GROUP = ((44000, 'Globo.com'), (44001, 'Externo'))
CHOICES_USER_TYPE = (('dev', 'Desenvolvimento'), ('prod', 'Produção'))


@autostrip
class UserForm(forms.Form):

    def __init__(self, groups_list, policys_list, usertype_list, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['groups'].choices = [
            (st['cn'], st['cn']) for st in groups_list]
        self.fields['policy'].choices = [
            (st['cn'], st['cn']) for st in policys_list]
        if usertype_list is None:
            self.fields['userType'].choices = []
        else:
            self.fields['userType'].choices = CHOICES_USER_TYPE

    groupPattern = forms.ChoiceField(label=u'Grupo Padrão:', required=True, choices=CHOICES_GROUP,
                                     error_messages=error_messages,  widget=forms.RadioSelect(renderer=RadioCustomRenderer))
    userType = forms.ChoiceField(label=u'Tipo de Usuário:',  required=False, choices=CHOICES_USER_TYPE, initial=CHOICES_USER_TYPE[
                                 0][0], error_messages=error_messages,  widget=forms.RadioSelect(renderer=RadioCustomRenderer))

    cn = forms.CharField(label=u'Username (UID / CN):', max_length=50,  required=True, validators=[
                         validate_cn], error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    uidNumber = forms.IntegerField(
        label=u'uidNumber:', required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    homeDirectory = forms.CharField(label=u'homeDirectory:',  max_length=50,  required=False,
                                    error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    loginShell = forms.CharField(label=u'loginShell:',  max_length=50,  required=True,
                                 error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    shadowMin = forms.IntegerField(
        label=u'shadowMin:', required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    shadowMax = forms.IntegerField(label=u'shadowMax:',   required=True,
                                   error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    shadowWarning = forms.IntegerField(
        label=u'shadowWarning:', required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    shadowLastChange = forms.IntegerField(
        label=u'shadowLastChange:', required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    policy = forms.ChoiceField(label=u'Policy:',  required=True,
                               error_messages=error_messages,  widget=forms.RadioSelect(renderer=RadioCustomRenderer))
    groups = forms.MultipleChoiceField(
        label=u'Grupos:', required=False, error_messages=error_messages, widget=forms.SelectMultiple(attrs={'style': "width: 310px"}))

    givenName = forms.CharField(label=u'Primeiro Nome:', max_length=50,  required=True,
                                error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    initials = forms.CharField(label=u'Nome do Meio:',  max_length=50,  required=True,
                               error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    sn = forms.CharField(label=u'Último Nome:',  max_length=50,  required=True,
                         error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    mail = forms.CharField(label=u'E-mail:',  max_length=50,  required=True,
                           error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    employeeNumber = forms.IntegerField(
        label=u'Matricula:', required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    employeeType = forms.CharField(label=u'Cargo:',  max_length=50,  required=True,
                                   error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    homePhone = forms.CharField(label=u'Telefone:', max_length=50,  required=True, validators=[
                                validate_phone], error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    mobile = forms.CharField(label=u'Celular:',  max_length=50,  required=True, validators=[
                             validate_phone], error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    street = forms.CharField(label=u'Endereço:',  max_length=60,  required=True,
                             error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))
    description = forms.CharField(label=u'Descrição:',  max_length=60,  required=True,
                                  error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 300px"}))

    def clean(self):
        cleaned_data = self.cleaned_data

        userType = cleaned_data.get("userType")
        homeDirectory = cleaned_data.get("homeDirectory")
        uidNumber = cleaned_data.get("uidNumber")
        groupPattern = cleaned_data.get("groupPattern")

        if groupPattern is not None:

            if str(groupPattern) == str(CHOICES_GROUP[0][0]):

                if homeDirectory is None or homeDirectory == "":
                    self._errors["homeDirectory"] = self.error_class(
                        [error_messages.get("required")])

                if userType is None or userType == "":
                    self._errors["userType"] = self.error_class(
                        [error_messages.get("required")])

            if uidNumber is not None:

                ldap = Ldap(None)

                if groupPattern == ldap.groupStandard:

                    if not ldap.valid_range_user_internal(uidNumber):
                        self._errors["uidNumber"] = self.error_class([ldap_messages.get(
                            "error_range_out_user") % (ldap.rangeUsers[0], ldap.rangeUsers[-1])])

                else:

                    if not ldap.valid_range_user_external(uidNumber):
                        self._errors["uidNumber"] = self.error_class([ldap_messages.get(
                            "error_range_out_user") % (ldap.rangeUsersExternal[0], ldap.rangeUsersExternal[-1])])

        return cleaned_data


@autostrip
class UserSearchForm(forms.Form):

    uidNumner = forms.IntegerField(
        label="Número", required=False, error_messages=error_messages, widget=forms.TextInput(attrs={"style": "width: 50px"}))
    cn = forms.CharField(label=u'uid:',  required=False, error_messages=error_messages,
                         widget=forms.TextInput(attrs={'style': "width: 150px"}))
    name = forms.CharField(label=u'Nome:', required=False, error_messages=error_messages,
                           widget=forms.TextInput(attrs={'style': "width: 150px"}))
    lock = forms.BooleanField(
        label="exibir dados de Lock", required=False, error_messages=error_messages)
