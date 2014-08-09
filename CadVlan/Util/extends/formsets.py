# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''
from django.forms import formsets


class BaseFormSet(formsets.BaseFormSet):
    """
    Override of BaseFormSet to set parameters on form class creation
    """
    
    def _construct_forms(self):
        # instantiate all the forms and put them in self.forms
        self.forms = []
        
        qnt = xrange(self.total_form_count())
        
        if len(self.params) != len(qnt):
            raise AttributeError("'%s' object with attribute 'params' has different length of forms quantity" % self.__class__.__name__)
        
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
        form = self.form(self.params[len(self.params)-i-1], i, **defaults)
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
    attrs = {'form': form, 'extra': extra, 'max_num': max_num, 'can_order': can_order,
             'can_delete': can_delete, 'params': params, 'equip_types': equip_types,
             'up': up, 'down': down, 'front_or_back': front_or_back}
    return type(form.__name__ + 'Set', (formset,), attrs)