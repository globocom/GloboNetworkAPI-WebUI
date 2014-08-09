# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.core.exceptions import ValidationError
from CadVlan.Util.utility import is_valid_cn, is_valid_command, is_valid_phone


def validate_cn(value):
    if not is_valid_cn(value):
        raise ValidationError(u"Este campo permite apenas caracteres alfanuméricos e os caracteres '_' e '-'.")

def validate_commands(lst):
    for value in lst:
        if not is_valid_command(value):
            raise ValidationError(u"O nome dos comandos permite apenas caracteres alfanuméricos sem acento e alguns símbolos especiais.")

def validate_phone(value):
    if not is_valid_phone(value):
        raise ValidationError(u"Este campo permite apenas caracteres numéricos, parênteses e '-'.")
