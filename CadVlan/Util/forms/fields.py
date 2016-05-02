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


from django.forms.widgets import Select
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape, escape


class SelectWithAttr(Select):

    """
    Subclass of Django's select widget that allows attr in option
    To disable an option, pass a dict instead of a string for its label,
    of the form: {'label': 'option label', 'attrs': {'attr x': 'value y'}}
    """

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if (option_value in selected_choices):
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        attr_extend = ''
        if isinstance(option_label, dict):
            if dict.get(option_label, 'attrs'):
                for key, val in option_label['attrs'].iteritems():
                    attr_extend = u' %s="%s"' % (key, val)
            option_label = option_label['label']
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, attr_extend,
            conditional_escape(force_unicode(option_label)))
