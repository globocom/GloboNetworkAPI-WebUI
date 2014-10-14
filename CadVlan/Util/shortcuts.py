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


import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import loader
from django.contrib.messages.constants import DEFAULT_TAGS
from django.contrib import messages

JSON = 'json'


def render_to_response_ajax(*args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling ajax

    return render_to_response_ajax(templates.LOGIN, {'form': form }, context_instance=RequestContext(request))

    ou

    return render_to_response_ajax( json = Json('', redirect, uri))

    """

    if kwargs.get(JSON) is None:
        return HttpResponse(loader.render_to_string(*args, **kwargs))

    else:
        return HttpResponse(json.dumps(kwargs.get(JSON)))


def render_json(*args, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    httpresponse_kwargs = {'content_type': kwargs.pop('content_type', None)}
    httpresponse_kwargs['content_type'] = "application/json"

    return HttpResponse(*args, **kwargs)


def render_message_json(message, level=messages.SUCCESS, content_type="application/json"):
    """
    Returns a HttpResponse converted Python dict to message json
    """

    context = dict()

    context["message"] = message
    context["status"] = DEFAULT_TAGS.get(level)

    return HttpResponseBadRequest(json.dumps(context), content_type=content_type)
