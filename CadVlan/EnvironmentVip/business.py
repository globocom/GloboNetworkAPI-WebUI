# -*- coding:utf-8 -*-
'''
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''


def get_ambiente_by_id(ambientes, id_ambiente):

    for ambiente in ambientes:
        if ambiente['id'] == id_ambiente:
            return ambiente

    return None
