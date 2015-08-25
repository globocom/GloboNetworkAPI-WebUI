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

from django.forms import formsets


class BaseFormSet(formsets.BaseFormSet):

    """
    Override of BaseFormSet to set parameters on form class creation
    """

    def _construct_forms(self):
        # instantiate all the forms and put them in self.forms
        self.forms = []

        qnt = xrange(self.total_form_count()) #numero de forms necessarios

        if len(self.params) != len(qnt): #o params tera que ser algo do tipo [[parametros form1],[parametros form2],...,[parametros formn]]
            raise AttributeError(
                "'%s' object with attribute 'params' has different length of forms quantity" % self.__class__.__name__)

        for i in qnt:
            self.forms.append(self._construct_form(i))

    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i)}
        if self.is_bound:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        form = self.form(self.params[len(self.params) - i - 1][1], self.params[len(self.params) - i - 1][0], i, **defaults) #passando o params[i] para o form[i]
        self.add_fields(form, i)
        return form

    def _get_empty_form(self, **kwargs):
        defaults = {
            'auto_id': self.auto_id,
            'prefix': self.add_prefix('__prefix__'),
            'empty_permitted': True,
        }
        defaults.update(kwargs)
        form = self.form("", **defaults)
        self.add_fields(form, None)
        return form
    empty_form = property(_get_empty_form)


def formset_factory(form, params=[], equip_types=[], up=[], down=[], front_or_back=[],
                    formset=BaseFormSet, extra=1, can_order=False, can_delete=False, max_num=None):
    """Return a FormSet for the given form class with parameters."""
    attrs = {'form': form, 'extra': extra, 'max_num': max_num, 'can_order': can_order, 'can_delete': can_delete,
             'params': params, 'equip_types': equip_types, 'up': up, 'down': down, 'front_or_back': front_or_back}

    return type(form.__name__ + 'Set', (formset,), attrs)
