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
