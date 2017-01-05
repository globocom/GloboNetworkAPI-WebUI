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

from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie
from networkapiclient.exception import NetworkAPIClientError

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.messages import vrf_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import VRF_CREATE
from CadVlan.templates import VRF_EDIT
from CadVlan.templates import VRF_LIST
from CadVlan.Util.Decorators import has_perm
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Vrf.forms import VrfForm

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def insert_vrf(request):
    try:
        lists = {}

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists["form_vrf"] = VrfForm()  # TODO Alterar depois de edit pra ""

        if request.method == 'POST':
            # Set data in form
            vrf_form = VrfForm(request.POST)

            # Return data to form in case of error
            lists["form_vrf"] = vrf_form

            # Validate
            if vrf_form.is_valid():
                vrf = vrf_form.cleaned_data["vrf"]
                internal_name = vrf_form.cleaned_data["internal_name"]

                list_vrf = [{
                    "vrf": vrf,
                    "internal_name": internal_name

                }]

                client.create_api_vrf().create(list_vrf)
                messages.add_message(
                    request, messages.SUCCESS, vrf_messages.get("success_insert"))

                return redirect('vrf.list')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VRF_CREATE, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}, {"permission": ADMINISTRATION, "write": True}])
def edit_vrf(request, id_vrf):
    try:
        lists = {}

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        vrf = client.create_api_vrf().get(ids=[id_vrf]).get("vrfs")[0]

        lists['form_vrf'] = VrfForm(
            initial=vrf
        )

        if request.method == 'POST':
            # Set data in form
            vrf_form = VrfForm(request.POST)

            # Return data to form in case of error
            lists["form_vrf"] = vrf_form

            if vrf_form.is_valid():
                id = vrf_form.cleaned_data["id"]
                vrf = vrf_form.cleaned_data["vrf"]
                internal_name = vrf_form.cleaned_data["internal_name"]

                list_vrf = [{
                    "id": id,
                    "vrf": vrf,
                    "internal_name": internal_name
                }]

                client.create_api_vrf().update(list_vrf)
                messages.add_message(
                    request, messages.SUCCESS, vrf_messages.get("success_edit"))

                return redirect('vrf.list')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VRF_EDIT, lists, context_instance=RequestContext(request))


@log
@login_required
@ensure_csrf_cookie
def list_vrf(request):

    try:
        lists = {}

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        vrfs = client.create_api_vrf().search()["vrfs"]
        lists['vrfs'] = vrfs

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VRF_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
def delete_vrf(request):

    try:
        ids = request.POST.getlist('ids[]')

        lists = {}

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        client.create_api_vrf().delete(ids)

        vrfs = client.create_api_vrf().search()["vrfs"]
        lists['vrfs'] = vrfs

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(VRF_LIST, lists, context_instance=RequestContext(request))


def create_fake_vrfs():

    vetor = []
    for i in range(1, 30):
        vetor.append({
            "id": i,
            "internal_name": "iname1",
            "vrf": "vrfname"
        })

    return vetor
