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


from django.http import HttpResponse
from django.template import loader
from django.template.context import RequestContext
from django.utils.cache import add_never_cache_headers
from CadVlan.Util.Enum import NETWORK_TYPES
from random import choice
import copy
import re
from networkapiclient.exception import InvalidParameterError


class IP_VERSION:
    IPv6 = ('v6', 'IPv6')
    IPv4 = ('v4', 'IPv4')
    List = (IPv4, IPv6)


def get_id_in_list(iten_list, iten_id):
    for iten in iten_list:
        if iten['id'] == (str(iten_id)):
            return iten


def check_regex(string, regex):
    pattern = re.compile(regex)
    return pattern.match(string) is not None


def is_valid_uri(param):
    '''Checks if the parameter is a valid uri.

    :param param: Value to be validated.

    :return True if the parameter has a valid uri value, or False otherwise.
    '''
    pattern = r"^[a-zA-Z0-9\\-_\\\-\\.!\\~\\*'\\(\\);/\\?:\\@\\&=\\{\\}\\#\\\[\\\]\\,]*$"
    return re.match(pattern, param)


def is_valid_cn(param):
    '''Checks if the parameter is a valid cn.

    :param param: Value to be validated.

    :return True if the parameter has a valid cn value, or False otherwise.
    '''
    pattern = r"^[a-zA-Z0-9\\-_\\\-]*$"
    return re.match(pattern, param)


def is_valid_command(param):
    '''Check if the parameter is a valid command.

    :param param: Value to be validated.

    :return True if the parameter is a valid command, or False otherwise.
    '''
    pattern = r"^[a-zA-Z0-9\!\@\#\$\%\&\*\/\_\\\-\(\)\'\"\+\=\<\>\,\.\[\]\{\}\|\?\;\:\ ]*$"
    return re.match(pattern, param)


def is_valid_phone(param):
    '''Check if the parameter is a valid phone number.

    :param param: Value to be validated.

    :return True if the parameter is a valid phone number, or False otherwise.
    '''
    pattern = r"^[0-9\\\-\\(\\)]*$"
    return re.match(pattern, param)


def convert_string_to_boolean(param):
    '''Convert the parameter of string to boolean.

    :param param: parameter to be converted.

    :return Parameter converted.
    '''
    if param == 'True':
        return True

    elif param == 'False':
        return False


def upcase_first_letter(s):
    return s[0].upper() + s[1:]


def convert_boolean_to_int(param):
    '''Convert the parameter of boolean to int.

    :param param: parameter to be converted.

    :return Parameter converted.
    '''
    if param == True:
        return int(1)

    elif param == False:
        return int(0)


def convert_int_to_boolean(param):
    '''Convert the parameter of int to boolean.

    :param param: parameter to be converted.

    :return Parameter converted.
    '''
    param = int(param)
    if param == 1:
        return True

    elif param == 0:
        return False


def validates_dict(param, key):
    '''Validates that the list is a dictionary and converts it to a vector

    :param param: to be verified and converted.

    :param key: Key List.

    :return list.
    '''
    if param is not None:

        if type(param.get(key)) == dict or type(param.get(key)) == str or type(param.get(key)) == unicode:
            return [param.get(key)]

        else:
            return param.get(key)

    else:

        return None


def make_random_password(length=8, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'):
    "Generates a random password with the given length and given allowed_chars"
    return ''.join([choice(allowed_chars) for i in range(length)])


def clone(obj):
    '''Clone the object

    :param obj: object to be cloned

    :return object cloned.
    '''
    return copy.copy(obj)


def acl_key(network):
    '''Convert the key of value acl.

    :param network: v4 or v6.

    :return value of key.

    :raise ValueError: Parameter null or blank
    '''
    if network is None:
        raise ValueError("Parameter null or blank")

    if network == NETWORK_TYPES.v4:
        return 'acl_file_name'

    else:
        return 'acl_file_name_v6'


def is_valid_int_param(param, required=True):
    '''Checks if the parameter is a valid integer value.

    :param param: Value to be validated.

    :return True if the parameter has a valid integer value, or False otherwise.
    '''
    if param is None and not required:
        return True
    elif param is None:
        return False

    try:
        int(param)
    except (TypeError, ValueError):
        return False
    return True


def get_param_in_request(request, param):
    '''Get value of param in request

    :param request: request.
    :param param: param.

    :return value of key.
    '''
    if param in request.POST:
        value = str(request.POST[param])

    elif param in request.GET:
        value = str(request.GET[param])

    else:
        value = None

    return value


class DataTablePaginator():

    @property
    def sColumns(self):
        return self.sColumns

    @property
    def sEcho(self):
        return self.sEcho

    @property
    def start_record(self):
        return self.start_record

    @property
    def end_record(self):
        return self.end_record

    @property
    def asorting_cols(self):
        return self.asorting_cols

    @property
    def searchable_columns(self):
        return self.searchable_columns

    @property
    def custom_search(self):
        return self.custom_search

    def __init__(self, request, columnIndexNameMap):
        self.request = request
        self.columnIndexNameMap = columnIndexNameMap

    def build_server_side_list(self):
        """
        Build all params to send to API
        """

        # Datatable params
        cols = int(self.request.GET.get('iColumns', 0))
        iDisplayLength = min(
            int(self.request.GET.get('iDisplayLength', 10)), 100)
        self.start_record = int(self.request.GET.get('iDisplayStart', 0))
        self.end_record = self.start_record + iDisplayLength

        # Pass sColumns
        keys = self.columnIndexNameMap.keys()
        keys.sort()
        colitems = [self.columnIndexNameMap[key] for key in keys]
        self.sColumns = ",".join(map(str, colitems))

        # Ordering data
        iSortingCols = int(self.request.GET.get('iSortingCols', 0))
        self.asorting_cols = []

        if iSortingCols:
            for sortedColIndex in range(0, iSortingCols):
                sortedColID = int(
                    self.request.GET.get('iSortCol_' + str(sortedColIndex), 0))
                if self.request.GET.get('bSortable_{0}'.format(sortedColID), 'false') == 'true':
                    sortedColName = self.columnIndexNameMap[sortedColID]
                    sortingDirection = self.request.GET.get(
                        'sSortDir_' + str(sortedColIndex), 'asc')
                    if sortingDirection == 'desc':
                        sortedColName = '-' + sortedColName
                    self.asorting_cols.append(sortedColName)

        # Determine which columns are searchable
        self.searchable_columns = []
        for col in range(0, cols):
            if self.request.GET.get('bSearchable_{0}'.format(col), False) == 'true':
                self.searchable_columns.append(self.columnIndexNameMap[col])

        # Apply filtering by value sent by user
        self.custom_search = self.request.GET.get(
            'sSearch', '').encode('utf-8')

        self.sEcho = int(self.request.GET.get('sEcho', 0))

    def build_response(self, data, total, json_template, request, request_var = None):
        """
        Build the response to ajax
        """
        # Build return json
        response_dict = dict()
        response_dict["aaData"] = data
        response_dict["sEcho"] = self.sEcho
        response_dict["iTotalRecords"] = total
        response_dict["iTotalDisplayRecords"] = total
        response_dict["sColumns"] = self.sColumns
        response_dict["requestVar"] = request_var
        response_dict["jsonData"] = data

        response = HttpResponse(loader.render_to_string(
            json_template, response_dict, context_instance=RequestContext(request)), mimetype='application/javascript')
        response.status_code = 200

        # Prevent from caching datatables result
        add_never_cache_headers(response)

        # Returns JSON
        return response


def safe_list_get(list_obj, index, default=None):

    try:
        return list_obj[index]
    except IndexError:
        return default
