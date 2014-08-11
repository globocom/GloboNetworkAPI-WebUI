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


from CadVlan.Util.utility import DataTablePaginator, validates_dict
from networkapiclient.Pagination import Pagination
from django.http import HttpResponseServerError, HttpResponse
import logging
from CadVlan.Util.Decorators import log, login_required, has_perm, access_external
from django.shortcuts import render_to_response
from CadVlan.templates import LOG_SEARCH_LIST, SEARCH_FORM_ERRORS, AJAX_LOG_LIST,\
    VERSION_HTML
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.permissions import AUDIT_LOG
from CadVlan.EventLog.forms import SearchFormLog
from django.template import loader
from CadVlan.settings import CADVLAN_VERSION
from networkapiclient.version_control import CLIENT_VERSION
logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": AUDIT_LOG, "read": True}])
def search_list(request):
    try:
        lists = dict()

        # Get User
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        choices_map = client.create_log().get_choices()
        usuarios = choices_map['usuario']
        acoes = choices_map['acao']
        funcionalidades = choices_map['funcionalidade']

        search_form = SearchFormLog(usuarios, acoes, funcionalidades)

        lists['search_form'] = search_form

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(LOG_SEARCH_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": AUDIT_LOG, "read": True}])
def ajax_list_logs(request):
    try:

        # If form was submited
        if request.method == 'GET':

            # Get user auth
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()

            # Pagination
            columnIndexNameMap = {0: '', 1: '', 2: '', 3: '', 4: '', 5: ''}
            dtp = DataTablePaginator(request, columnIndexNameMap)

            # Make params
            dtp.build_server_side_list()

            # Set params in simple Pagination class
            pag = Pagination(dtp.start_record, dtp.end_record,
                             dtp.asorting_cols, dtp.searchable_columns, dtp.custom_search)

            user_name = ''
            first_date = ''
            start_time = ''
            last_date = ''
            end_time = ''
            action = ''
            functionality = ''
            parameter = ''

            choices_map = client.create_log().get_choices()
            usuarios = choices_map['usuario']
            acoes = choices_map['acao']
            funcionalidades = choices_map['funcionalidade']

            search_form = SearchFormLog(
                usuarios, acoes, funcionalidades, request.GET)
            if search_form.is_valid():
                user_name = search_form.cleaned_data['user']
                first_date = search_form.cleaned_data['first_date']
                start_time = search_form.cleaned_data['start_time']
                last_date = search_form.cleaned_data['last_date']
                end_time = search_form.cleaned_data['end_time']
                action = search_form.cleaned_data['action']
                functionality = search_form.cleaned_data['functionality']
                parameter = search_form.cleaned_data['parameter']

            else:
                # Remake search form
                lists = dict()
                lists["search_form"] = search_form

                # Returns HTML
                response = HttpResponse(loader.render_to_string(
                    SEARCH_FORM_ERRORS, lists, context_instance=RequestContext(request)))
                # Send response status with error
                response.status_code = 412
                return response

            # Call API passing all params
            logs = client.create_log().find_logs(user_name, first_date, start_time,
                                                 last_date, end_time, action, functionality, parameter, pag)

            if not logs.has_key("eventlog"):
                logs["eventlog"] = []

            # Returns JSON
            return dtp.build_response(logs["eventlog"], logs["total"], AJAX_LOG_LIST, request)

    except NetworkAPIClientError, e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')
    except BaseException, e:
        logger.error(e)
        return HttpResponseServerError(e, mimetype='application/javascript')


@log
@login_required
def version_checks(request):
    # Get user auth
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    # Show versions
    lists = dict()
    lists['version_cadvlan'] = CADVLAN_VERSION
    lists['version_client'] = CLIENT_VERSION
    lists['version_api'] = client.create_log().get_version().get('api_version')
    return render_to_response(VERSION_HTML, lists, context_instance=RequestContext(request))
