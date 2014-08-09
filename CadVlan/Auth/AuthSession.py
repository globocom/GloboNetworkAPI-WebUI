# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapiclient.ClientFactory import ClientFactory
from CadVlan.settings import NETWORK_API_URL, SESSION_EXPIRY_AGE


class AuthSession:

    KEY = 'user'

    def __init__(self, session):
        self.session = session

    def login(self, user):
        '''Log in session user 
        '''
        self.session[self.KEY] = user

    def logout(self):
        '''Log out session user 
        '''
        if self.session.has_key(self.KEY):
            self.session[self.KEY] = None

    def is_authenticated(self):
        '''Validates that the user is authenticated
        '''
        if self.session.has_key(self.KEY) and self.session[self.KEY] != None:
            self.session.set_expiry(SESSION_EXPIRY_AGE)
            return True
        else:
            return False

    def get_user(self):
        '''Get user authenticated
        '''
        if self.is_authenticated():
            return self.session[self.KEY]
        else:
            return None

    def get_clientFactory(self):
        '''Get clientFactory of NetworkAPI
        '''
        user = self.get_user()
        return ClientFactory(NETWORK_API_URL, user.get_username(), user.get_password(), user.get_user_ldap())
