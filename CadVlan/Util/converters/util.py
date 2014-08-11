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



def split_to_array(string, sep=";"):
    """
    Returns an array of strings separated by regex
    """
    if string is not None:
        return string.split(sep)


def replace_id_to_name(main_list, type_list, str_main_id, str_type_id, str_prop):
    """
    Return list replacing type id to type name
    """

    for item in main_list:
        id_type = item[str_main_id]
        for type_item in type_list:
            if type_item[str_type_id] == id_type:
                item[str_main_id] = type_item[str_prop]
                break

    return main_list
