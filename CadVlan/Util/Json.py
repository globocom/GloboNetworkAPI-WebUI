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



class Json(object):

    content = None
    redirect = None
    uri = None

    def __init__(self, content, redirect=None, uri=None):
        self.content = content
        self.redirect = redirect
        self.uri = uri

    def get_content(self):
        return self.content

    def get__redirect(self):
        return self.redirect

    def get__uri(self):
        return self.uri
