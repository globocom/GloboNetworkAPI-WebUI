# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django import forms
from CadVlan.messages import error_messages, environment_messages
from CadVlan.Util.utility import check_regex
import types
from django.forms.util import ErrorList


NETWORK_IP_CHOICES = (("v4", "IPv4"), ("v6", "IPv6"))


class DivisaoDCForm(forms.Form):
    id_env = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    nome = forms.CharField(label=u'Divisão do Data Center' , min_length=2, max_length=100, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))

    def clean_nome(self):
        if not check_regex(self.cleaned_data['nome'], r'^[-0-9a-zA-Z]+$'):
            raise forms.ValidationError('Caracteres inválidos.')

        return self.cleaned_data['nome']


class Grupol3Form(forms.Form):
    id_env = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    nome = forms.CharField(label=u'Grupo Layer3' , min_length=2, max_length=80, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))

    def clean_nome(self):
        if not check_regex(self.cleaned_data['nome'], r'^[-0-9a-zA-Z]+$'):
            raise forms.ValidationError('Caracteres inválidos.')

        return self.cleaned_data['nome']


class AmbienteLogicoForm(forms.Form):
    id_env = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    nome = forms.CharField(label=u'Ambiente Lógico' , min_length=2, max_length=80, required=True, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 200px"}))

    def clean_nome(self):
        if not check_regex(self.cleaned_data['nome'], r'^[-0-9a-zA-Z]+$'):
            raise forms.ValidationError('Caracteres inválidos.')

        return self.cleaned_data['nome']


class AmbienteForm(forms.Form):

    def __init__(self, env_logic, division_dc, group_l3, filters, ipv4, ipv6, *args, **kwargs):
        super(AmbienteForm, self).__init__(*args, **kwargs)
        self.fields['divisao'].choices = [(div['id'], div['nome']) for div in division_dc["division_dc"]]
        self.fields['ambiente_logico'].choices = [(amb_log['id'], amb_log['nome']) for amb_log in env_logic["logical_environment"]]
        self.fields['grupol3'].choices = [(grupo['id'], grupo['nome']) for grupo in group_l3["group_l3"]]
        self.fields['filter'].choices = [(filter_['id'], filter_['name']) for filter_ in filters["filter"]]
        self.fields['filter'].choices.insert(0, (None, '--------'))
        self.fields['ipv4_template'].choices = [(template['name'], template['name']) for template in ipv4]
        self.fields['ipv4_template'].choices.insert(0, ('', '--------'))
        self.fields['ipv6_template'].choices = [(template['name'], template['name']) for template in ipv6]
        self.fields['ipv6_template'].choices.insert(0, ('', '--------'))

    id_env = forms.IntegerField(label="", required=False, widget=forms.HiddenInput(), error_messages=error_messages)
    divisao = forms.ChoiceField(label="Divisão DC", choices=[(0, 'Selecione')] , required=True, widget=forms.Select(attrs={'style': "width: 160px"}), error_messages=error_messages)
    ambiente_logico = forms.ChoiceField(label="Ambiente Lógico", required=True, choices=[(0, 'Selecione')] , widget=forms.Select(attrs={'style': "width: 210px"}), error_messages=error_messages)
    grupol3 = forms.ChoiceField(label="Grupo Layer3", choices=[(0, 'Selecione')], required=True, widget=forms.Select(attrs={'style': "width: 280px"}), error_messages=error_messages)
    filter = forms.ChoiceField(label="Filtro", choices=[(None, '--------')], required=False, widget=forms.Select(attrs={'style': "width: 280px"}), error_messages=error_messages)
    acl_path = forms.CharField(label=u'Path ACL', max_length=250, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 280px", 'autocomplete': "off"}))
    ipv4_template = forms.ChoiceField(label="Template ACL IPV4", choices=[('', '--------')], required=False, widget=forms.Select(attrs={'style': "width: 280px"}), error_messages=error_messages)
    ipv6_template = forms.ChoiceField(label="Template ACL IPV6", choices=[('', '--------')], required=False, widget=forms.Select(attrs={'style': "width: 280px"}), error_messages=error_messages)
    link = forms.CharField(label=u'Link', max_length=200, required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 280px"}))

    max_num_vlan_1 = forms.IntegerField(label=u'Max Vlan 1', required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))
    min_num_vlan_1 = forms.IntegerField(label=u'Min Vlan 1', required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))
    max_num_vlan_2 = forms.IntegerField(label=u'Max Vlan 2', required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))
    min_num_vlan_2 = forms.IntegerField(label=u'Min Vlan 2', required=False, error_messages=error_messages, widget=forms.TextInput(attrs={'style': "width: 100px"}))


    def clean_min_num_vlan_1(self):
        max_num_vlan_1 = self.cleaned_data.get('max_num_vlan_1')
        min_num_vlan_1 = self.cleaned_data.get('min_num_vlan_1')

        if (max_num_vlan_1 != '' and min_num_vlan_1 == '') or (min_num_vlan_1 != '' and max_num_vlan_1 == '') or (not max_num_vlan_1 and min_num_vlan_1) or (not min_num_vlan_1 and max_num_vlan_1):
            raise forms.ValidationError('O valor máximo e mínimo devem ser preenchidos.')

        if max_num_vlan_1 and max_num_vlan_1 != '' and min_num_vlan_1 and min_num_vlan_1 != '':
            max_num_vlan_1 = max_num_vlan_1
            min_num_vlan_1 = min_num_vlan_1

            if max_num_vlan_1 < 1 or min_num_vlan_1 < 1:
                raise forms.ValidationError('O valor preenchido deve ser maior que zero.')
            if max_num_vlan_1 <= min_num_vlan_1:
                raise forms.ValidationError('O valor máximo deve ser maior que o mínimo.')

        return min_num_vlan_1


    def clean_min_num_vlan_2(self):
        max_num_vlan_2 = self.cleaned_data.get('max_num_vlan_2')
        min_num_vlan_2 = self.cleaned_data.get('min_num_vlan_2')

        if (max_num_vlan_2 != '' and min_num_vlan_2 == '') or (min_num_vlan_2 != '' and max_num_vlan_2 == '') or  (not max_num_vlan_2 and min_num_vlan_2) or (not min_num_vlan_2 and max_num_vlan_2):
            raise forms.ValidationError('O valor máximo e mínimo devem ser preenchidos.')

        if max_num_vlan_2 and max_num_vlan_2 != '' and min_num_vlan_2 and min_num_vlan_2 != '':
            max_num_vlan_2 = max_num_vlan_2
            min_num_vlan_2 = min_num_vlan_2

            if max_num_vlan_2 < 1 or min_num_vlan_2 < 1:
                raise forms.ValidationError('O valor preenchido deve ser maior que zero.')

            if max_num_vlan_2 <= min_num_vlan_2:
                raise forms.ValidationError('O valor máximo deve ser maior que o mínimo.')

        return min_num_vlan_2


    def clean_acl_path(self):
        # valida acl_path
        if check_regex(self.cleaned_data['acl_path'], r'^.*[\\\\:*?"<>|].*$'):
            raise forms.ValidationError('Caracteres inválidos.')

        path = self.cleaned_data['acl_path']
        if path:
            try:
                while path[0] == "/":
                    path = path[1:]

                while path[-1] == "/":
                    path = path[:-1]
            except IndexError:
                raise forms.ValidationError('Path inválido')
        # valida acl_path

        return self.cleaned_data['acl_path']


class OctFieldV4(forms.CharField):

    def __init__(self, *args, **kwargs):
        super(OctFieldV4, self).__init__(max_length=3, required=False, *args, **kwargs)

    label = u""
    error_messages = error_messages
    widget = forms.TextInput(
        attrs={
           'style': "width:30px;",
           'class': "ipv4"
        }
    )


class OctFieldV6(forms.CharField):

    def __init__(self, *args, **kwargs):
        super(OctFieldV6, self).__init__(max_length=4, required=False, *args, **kwargs)

    label = u""
    error_messages = error_messages
    widget = forms.TextInput(
        attrs={
            'style': "width:35px;"
        }
    )


class IpConfigForm(forms.Form):

    ip_version = forms.ChoiceField(

        label="Rede IPv4/IPv6",
        required=True,
        choices=NETWORK_IP_CHOICES,
        error_messages=error_messages,
        widget=forms.RadioSelect,
        initial='v4'
    )

    v4oct1 = OctFieldV4()

    v4oct2 = OctFieldV4()

    v4oct3 = OctFieldV4()

    v4oct4 = OctFieldV4()

    v4oct5 = forms.CharField(

        label=u"",
        required=False,
        error_messages=error_messages,
        max_length=2,
        widget=forms.TextInput(
            attrs={'style': "width:18px;",
                   'class': "ipv4"
            }
        )

    )

    v6oct1 = OctFieldV6()

    v6oct2 = OctFieldV6()

    v6oct3 = OctFieldV6()

    v6oct4 = OctFieldV6()

    v6oct5 = OctFieldV6()

    v6oct6 = OctFieldV6()

    v6oct7 = OctFieldV6()

    v6oct8 = OctFieldV6()

    v6oct9 = forms.CharField(

        label=u"",
        required=False,
        error_messages=error_messages,
        max_length=3,
        widget=forms.TextInput(
            attrs={'style': "width:24px;",
                   'id': "mask"
            }
        )

    )

    prefix = forms.IntegerField(
        label=u'Prefixo:',
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                'style': "width: 26px"
            }
        )
    )

    network_validate = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def clean(self):

        if not self._errors:
            ip_version = self.cleaned_data.get('ip_version', '')
            prefix = int(self.cleaned_data.get('prefix', ''))

            if ip_version == "v4":

                if prefix not in range(33):
                    self._errors['prefix'] = self.error_class([environment_messages.get('invalid_prefix_ipv4')])

                v4oct1 = self.cleaned_data.get('v4oct1', '')
                v4oct2 = self.cleaned_data.get('v4oct2', '')
                v4oct3 = self.cleaned_data.get('v4oct3', '')
                v4oct4 = self.cleaned_data.get('v4oct4', '')
                v4oct5 = self.cleaned_data.get('v4oct5', '')

                try:
                    if int(v4oct5) >= int(prefix):
                        self._errors['prefix'] = self.error_class([environment_messages.get('invalid_prefix')])
                except Exception:
                    pass

                network_ipv4 = v4oct1 + v4oct2 + v4oct3 + v4oct4 + v4oct5
                self.cleaned_data['network_validate'] = v4oct1 + '.' + v4oct2 + '.' + v4oct3 + '.' + v4oct4 + '/' + v4oct5

                if len(network_ipv4) < 10:
                    self._errors['network_validate'] = self.error_class([environment_messages.get('invalid_network')])

            else:
                if prefix not in range(129):
                    self._errors['prefix'] = self.error_class([environment_messages.get('invalid_prefix_ipv6')])

                v6oct1 = self.cleaned_data.get('v6oct1', '')
                v6oct2 = self.cleaned_data.get('v6oct2', '')
                v6oct3 = self.cleaned_data.get('v6oct3', '')
                v6oct4 = self.cleaned_data.get('v6oct4', '')
                v6oct5 = self.cleaned_data.get('v6oct5', '')
                v6oct6 = self.cleaned_data.get('v6oct6', '')
                v6oct7 = self.cleaned_data.get('v6oct7', '')
                v6oct8 = self.cleaned_data.get('v6oct8', '')
                v6oct9 = self.cleaned_data.get('v6oct9', '')

                try:
                    if int(v6oct9) >= int(prefix):
                        self._errors['prefix'] = self.error_class([environment_messages.get('invalid_prefix')])
                except Exception:
                    pass

                network_ipv6 = v6oct1 + v6oct2 + v6oct3 + v6oct4 + v6oct5 + v6oct6 + v6oct7 + v6oct8 + v6oct9
                self.cleaned_data['network_validate'] = v6oct1 + ':' + v6oct2 + ':' + v6oct3 + ':' + v6oct4 + ':' + v6oct5 + ':' + v6oct6 + ':' + v6oct7 + ':' + v6oct8 + '/' + v6oct9

                if len(network_ipv6) < 18:
                    self._errors['network_validate'] = self.error_class([environment_messages.get('invalid_network')])

            return self.cleaned_data
