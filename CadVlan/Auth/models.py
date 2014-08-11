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
