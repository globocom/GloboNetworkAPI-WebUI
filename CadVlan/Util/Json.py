# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''


class Json(object):

    content = None
    redirect = None
    uri = None

    def __init__(self, content, redirect = None, uri = None):
        self.content = content
        self.redirect = redirect
        self.uri = uri

    def get_content(self):
        return self.content

    def get__redirect(self):
        return self.redirect

    def get__uri(self):
        return self.uri