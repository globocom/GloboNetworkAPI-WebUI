# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.permissions import USER_ADMINISTRATION


class User(object):

    __id = None
    __username = None
    __name = None
    __email = None
    __password = None
    __permission = None
    __active = None
    __user_ldap = None

    def __init__(self, id, user, nome, email, pwd, permission, ativo, user_ldap):
        self.__id = id
        self.__username = user
        self.__name = nome
        self.__email = email
        self.__password = pwd
        self.__permission = permission
        self.__active = ativo
        self.__user_ldap = user_ldap

    def get_id(self):
        return self.__id

    def get_username(self):
        return self.__username

    def get_name(self):
        return self.__name

    def get_email(self):
        return self.__email

    def get_password(self):
        return self.__password

    def get_permission(self):
        return self.__permission

    def get_active(self):
        return self.__active

    def get_user_ldap(self):
        return self.__user_ldap

    def set_password(self, password):
        self.__password = password

    def has_perm(self, permission,  write=None, read=None):
        '''Validates that the user has access permission

            :param permission: access permission to be validated
            :param write: permission be write
            :param read: permission be read
        '''
        if self.__permission.has_key(permission):

            if write is not None:

                if self.__permission.get(permission).get('write') == "False":
                    return False

            if read is not None:

                if self.__permission.get(permission).get('read') == "False":
                    return False

            return True
        else:
            return False

    def has_perm_menu(self, write=None, read=None):
        '''Validates that the user has access permission in top menu

            :param write: permission be write
            :param read: permission be read
        '''
        for permission in self.__permission.keys():

            if permission != USER_ADMINISTRATION:

                if write is not None:

                    if self.__permission.get(permission).get('write') == "True":
                        return True

                if read is not None:

                    if self.__permission.get(permission).get('read') == "True":
                        return True

        return False
