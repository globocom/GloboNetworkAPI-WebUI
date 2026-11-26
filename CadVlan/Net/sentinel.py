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

import logging

import requests
from requests.auth import HTTPBasicAuth

from CadVlan.settings import OMNICLOUD_API_URL, SENTINEL_OMNIAUTH_CLIENT_ID, \
    SENTINEL_OMNIAUTH_CLIENT_SECRET, OMNICLOUD_TIMEOUT, OMNICLOUD_TENANT_ID

logger = logging.getLogger(__name__)

TOKEN_PATH = '/iam/v1/auth/token'
IP_VALIDATION_PATH = '/sentinel/v1/validations/ip/%s'


class SentinelError(Exception):
    pass


def _get_access_token():
    try:
        response = requests.post(
            OMNICLOUD_API_URL + TOKEN_PATH,
            auth=HTTPBasicAuth(SENTINEL_OMNIAUTH_CLIENT_ID,
                               SENTINEL_OMNIAUTH_CLIENT_SECRET),
            data={'grant_type': 'client_credentials', 'tenant_id': OMNICLOUD_TENANT_ID},
            timeout=OMNICLOUD_TIMEOUT)
            # verify=SSL_PEM)
        response.raise_for_status()
        token = response.json().get('access_token')
    except (requests.RequestException, ValueError, AttributeError) as e:
        logger.error(e)
        raise SentinelError(u'Falha ao obter token para verificação: %s' % e)

    return token


def validate_ip(ip):
    token = _get_access_token()
    try:
        response = requests.get(
            OMNICLOUD_API_URL + IP_VALIDATION_PATH % ip,
            headers={'Authorization': 'Bearer %s' % token},
            timeout=OMNICLOUD_TIMEOUT)
            # verify=SSL_PEM)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        logger.error(e)
        raise SentinelError(u'Falha ao validar o IP: %s' % e)
