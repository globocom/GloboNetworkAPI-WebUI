# -*- coding:utf-8 -*-

#!/usr/bin/env python
import os
import sys

# OBSERVACAO: Este arquivo deve permanecer aqui para poder ser utilizado
# pelo deployment em produção

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CadVlan.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
