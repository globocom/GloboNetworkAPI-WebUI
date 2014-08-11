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


from django.core.exceptions import ValidationError
from CadVlan.Util.utility import is_valid_cn, is_valid_command, is_valid_phone


def validate_cn(value):
    if not is_valid_cn(value):
        raise ValidationError(
            u"Este campo permite apenas caracteres alfanuméricos e os caracteres '_' e '-'.")


def validate_commands(lst):
    for value in lst:
        if not is_valid_command(value):
            raise ValidationError(
                u"O nome dos comandos permite apenas caracteres alfanuméricos sem acento e alguns símbolos especiais.")


def validate_phone(value):
    if not is_valid_phone(value):
        raise ValidationError(
            u"Este campo permite apenas caracteres numéricos, parênteses e '-'.")
